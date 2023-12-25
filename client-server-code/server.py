import pyarrow.flight as flight
import pyarrow as pa
import pandas as pd
from pandas import json_normalize
import json
import os
import threading

class FlightServer(flight.FlightServerBase):
    def __init__(self, location, tables):
        super(FlightServer, self).__init__(location)
        self.tables = tables

    def do_get(self, context, ticket):
        table_name = ticket.ticket.decode()
        if table_name == "get_table_names":
            table_names = pa.Table.from_pandas(pd.DataFrame({"table_name": list(self.tables.keys())}))
            return flight.RecordBatchStream(table_names)
        elif table_name not in self.tables:
            raise ValueError("Table not found.")
        else:
            return flight.RecordBatchStream(self.tables[table_name])


class JSONPathMethod:
    def flatten_json(self, y):
        out = {}

        def flatten(x, name=''):
            if isinstance(x, dict):
                for a in x:
                    flatten(x[a], name + a + '.')
            elif isinstance(x, list):
                for i, a in enumerate(x):
                    flatten(a, name.rstrip('.') + '[' + str(i) + '].')
            else:
                out[name.rstrip('.')] = x

        flatten(y)
        return out

    def load_and_flatten(self, path):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [self.flatten_json(item) for item in data]
            else:
                return [self.flatten_json(data)]

    def serve_example(self, paths, port):
        results = {f"JSONPathMethod_{os.path.splitext(os.path.basename(path))[0]}": pa.Table.from_pandas(pd.DataFrame(self.load_and_flatten(path))) for path in paths}
        location = flight.Location.for_grpc_tcp("localhost", port)
        server = FlightServer(location, results)
        print("Serving on", location)
        server.serve()

class SimpleMethod:
    def load_and_flatten(self, path):
        return json_normalize(json.load(open(path, encoding='utf-8')))

    def serve_example(self, paths,port):
        results = {f"SimpleMethod_{os.path.splitext(os.path.basename(path))[0]}": pa.Table.from_pandas(self.load_and_flatten(path)) for path in paths}
        location = flight.Location.for_grpc_tcp("localhost", port)
        server = FlightServer(location, results)
        print("Serving on", location)
        server.serve()

class TablesMethod:
    def make_new_json(self, lists, table_name):
        data = []
        for i, item in enumerate(lists[table_name]):
            if isinstance(item, list):
                for elem in item or [None]:
                    data.append({"row_number": i, "value": elem})
            elif item is not None:
                data.append({"row_number": i, "value": item})
        return data

    def delete_lists(self, df, name, path):
        df = pd.json_normalize(df)
        is_list = df.applymap(lambda x: isinstance(x, list)).any()
        list_columns = is_list[is_list].index.tolist()

        if list_columns:
            list_df = df[list_columns].copy()
            df = df.drop(columns=list_columns)
            df['row_number'] = range(1, len(df) + 1)

        main_table = pa.Table.from_pandas(df)
        tables = {f"TablesMethod_{path}{'_' if name != '' else ''}{name}": main_table}

        for dropped_list in list_columns:
            new_json = self.make_new_json(list_df, dropped_list)
            tables.update(self.delete_lists(new_json, dropped_list, path))

        return tables

    def serve_example(self, paths, port):
        results = []
        for path in paths:
            with open(path, encoding='utf-8') as f:
                dt = json.load(f)
            tables = self.delete_lists(dt, '', os.path.splitext(os.path.basename(path))[0])
            results.append(tables)

        merged_results = {k: v for tables in results for k, v in tables.items()}

        location = flight.Location.for_grpc_tcp("localhost", port)
        server = FlightServer(location, merged_results)
        print("Serving on", location)
        server.serve()



if __name__ == '__main__':
    paths = [ '../data/airlines.json', 
            '../data/gists.json', 
            '../data/historical-events.json',
            '../data/movies.json',
            '../data/reddit.json',
            '../data/nasa.json']
    
    method1 = JSONPathMethod()
    thread1 = threading.Thread(target=method1.serve_example, args=(paths, 50051))
    thread1.start()

    method2 = SimpleMethod()
    thread2 = threading.Thread(target=method2.serve_example, args=(paths, 50052))
    thread2.start()

    method3 = TablesMethod()
    thread3 = threading.Thread(target=method3.serve_example, args=(paths, 50053))
    thread3.start()


    thread1.join()
    thread2.join()
    thread3.join()


