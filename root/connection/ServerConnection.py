import asyncio
import re
from  connection.TorServiceManager import TorServiceManager

class ServerConnection():
    def __init__(self, name , max_number_of_connections,messages_queue, notifications_queue, HOST , PORT , pin = None):
        self.users = []
        self.name = name
        self.max_number_of_connections = max_number_of_connections
        self.pin = pin
        self.messages_queue = messages_queue
        self.notifications_queue = notifications_queue
        self.onion_adress = ""

        self.active  = True
        self.HOST = HOST
        self.PORT = PORT
        self.my_connections = []

    def delete_user(self, user_id):
        self.users.remove(user_id)
        self.local_black_list.append()
    
    def async_server(self):
        async def events():
            self.web_loop = asyncio.get_event_loop()
            await asyncio.gather(self.server_listener() ,self.check_messages_for_web())
        
        asyncio.run(events())
    
    async def check_messages_for_web(self):
        while True:
            last_message = await self.web_queue.get()
            await self.broadcast_message(last_message)
            
    async def server_listener(self):
        # print("inicio um loop para o servidor")

        async def connection_handler(reader, writer):
            async def local_listerner(reader, writer):
                self.my_connections.append(writer)
                while True:
                    data = await reader.read(1024)
                    if not data:
                        print("Cliente desconectado.")
                        break
                    message = data.decode().strip()
                    print(f"==== chegou mensagem: {message}")
                    msg_info = {
                        "entry": message,
                        "author_name": writer.get_extra_info('peername'), 
                        "owner": False
                    }
                    await self.web_queue.put(msg_info)
                    self.messages_queue.put(msg_info)
                    print("mensagem recebida!!")
                    # self.add_message_on_gui(entry = message, author_name = " " , owner =  False)
            await local_listerner(reader , writer)
            
        async def serve(server):
            print("to servindo pra sempre")
            async with server:
                print("servidor iniciado")
                await server.serve_forever()

        self.web_queue = asyncio.Queue()
        server = await asyncio.start_server(connection_handler , self.HOST ,self.PORT)
        sock = server.sockets[0]
        local_port = sock.getsockname()[1]

        await asyncio.gather(serve(server) ,self.start_onion_service(local_port))

    async def start_onion_service(self, port):
        
        self.onion_connection = TorServiceManager.start_onion_server(self.name , port)

            

    async def broadcast_message(self, message):
        data = message["entry"]
        data_encoded = (data + "\n").encode()


        for w in self.my_connections:
            peername = w.get_extra_info('peername')
            # print(peername)
            try:
                # ip, port = re.findall(r"\d{1,5}(?:\.\d{1,5}){0,3}", peername) 
                if message["author_name"] != peername:
                    w.write(data_encoded)
                    await w.drain()
            except (ConnectionResetError , ConnectionRefusedError): 
                print("erro de conexao")
            print("===========")
        
    def add_message(self,message):
        self.web_loop.call_soon_threadsafe(self.web_queue.put_nowait , {"entry" : message,
                             "author_name" : " " , "owner" :  True })