import time
from threading import Thread

from src.main.python.client import Client
from src.main.python.create_message import create_message
from src.main.python.server import Server

if __name__ == "__main__":
    port = 12345
    host = "127.0.0.1"

    server = Server(host, port)
    thread_server = Thread(target=server.start)
    thread_server.start()

    client = Client(host, port)
    client.connect()
    while True:
        time.sleep(0.1)
        client.send_message(create_message())
        response = client.receive_message()
        print(response)
        time.sleep(0.1)
        want_continue = input("Do you want to continue? (y/n): ")
        if want_continue.lower() != "y":
            break
    print(client.receive_message())
    client.close()
    server.stop()