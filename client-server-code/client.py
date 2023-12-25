import pyarrow.flight as flight

def client_example():
    client = flight.FlightClient("grpc+tcp://localhost:50053")
    table_name = 'TablesMethod_movies_cast'
    reader = client.do_get(flight.Ticket(table_name.encode()))
    data = reader.read_all()
    print(data)


if __name__ == '__main__':
    client_example()
