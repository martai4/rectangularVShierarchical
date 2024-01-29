import pyarrow.flight as flight
import pyarrow as pa
import pandas as pd
import json, os

from FlightServer import FlightServer

class SimpleMethod:
    def load_and_flatten(self, path):
        return pd.json_normalize(json.load(open(path, encoding='utf-8')))

    def serve_example(self, paths,port):
        results = {f"SimpleMethod_{os.path.splitext(os.path.basename(path))[0]}": pa.Table.from_pandas(self.load_and_flatten(path)) for path in paths}
        location = flight.Location.for_grpc_tcp("0.0.0.0", port)
        server = FlightServer(location, results)
        print("Serving on", location)
        server.serve()