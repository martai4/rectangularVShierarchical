import pyarrow.flight as flight
import pyarrow as pa
import pandas as pd

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