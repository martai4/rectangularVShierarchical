import pyarrow.flight as flight
import pyarrow as pa
import pandas as pd
import json, os

from FlightServer import FlightServer

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
        location = flight.Location.for_grpc_tcp("0.0.0.0", port)
        server = FlightServer(location, results)
        print("Serving on", location)
        server.serve()