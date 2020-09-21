import asyncio


class ClientServerProtocol(asyncio.Protocol):
    requests = {}

    """def __init__(self):
        super().__init__()
        self.requests = {}"""

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        data = data.decode()
        resp = self.process_data(data)
        self.transport.write(resp.encode())

    def process_data(self, data):
        if not data.endswith("\n"):
            return("error\nwrong command\n\n")
        data = data[0: len(data) - 1]
        data = data.split(" ")
        command = data[0]
        data = data[1:]
        if command == "get":
            resp = self.process_get(data)
            return resp
        elif command == "put":
            resp = self.process_put(data)
            return resp
        else:
            return "error\nwrong command\n\n"

    def process_get(self, data):
        if len(data) != 1:
            return "error\nwrong command\n\n"
        metric = data[0]
        if metric not in self.requests.keys() and metric != "*":
            return "ok\n\n"
        resp = "ok\n"
        if metric == "*":
            metrics = self.requests.keys()
            for m in metrics:
                string = self.process_request(m)
                resp += string
            resp += "\n"
            return resp

        resp += self.process_request(metric) + "\n"
        return resp
        
    def process_request(self, key):
        resp = ""
        for item in self.requests[key]:
            resp += f"{key} {item[0]} {item[1]}\n"
        return resp
        
        

    def process_put(self, data):
        if len(data) != 3:
            return "error\nwrong command\n\n" 
        try:
            metric = str(data[0])
            value = float(data[1])
            timestamp = int(data[2])
        except ValueError:
            return "error\nwrong command\n\n"
        except TypeError:
            return "error\nwrong command\n\n"

        if metric not in self.requests.keys():
            self.requests[metric] = []

        i = 0
        for item in self.requests[metric]:
            if timestamp == item[1]:
                self.requests[metric][i] = (value, timestamp)
                return "ok\n\n"
            i += 1

        self.requests[metric].append((value, timestamp))
        return "ok\n\n"        

def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == "__main__":
    run_server('127.0.0.1', 8889)