import pyarrow.flight as flight
import pyarrow as pa
import pandas as pd
import json, os

from FlightServer import FlightServer

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

        location = flight.Location.for_grpc_tcp("0.0.0.0", port)
        server = FlightServer(location, merged_results)
        print("Serving on", location)
        server.serve()

