import asyncio
import re
from  connection.tor_service_manager import TorServiceManager
from models.notification import Notification , NotificationType


class ServerConnection():
    def __init__(self, name  , pin = None):
        self.users = []
        self.name = name
        # self.max_number_of_connections = max_number_of_connections
        self.pin = pin
        self.messages_queue = None
        self.notification_queue = None
        self.messages_to_send_queue = None

        self.onion_adress = ""
        self._active  = True
        self.PORT = None
        self.HOST = "127.0.0.1"
        self.my_connections = []
        self._connected = False
        
    def validate_connection_state(func):
        async def inner_wrapper(self ,*args, **kwargs):
            if self._connected:
                return await func(self,*args, **kwargs)
            else:
                raise ValueError("The connection didnt start yet!")
        return inner_wrapper
    

    def delete_user(self, user_id):
        self.users.remove(user_id)
        self.local_black_list.append()
    
    
    async def start_server(self ,port):
        # async def events():
        self.messages_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()
        self.messages_to_send_queue = asyncio.Queue()
        self.PORT  = port
        self._connected = True
        await self.server_listener() 
        # asyncio.run(events())
        # await events()


    @validate_connection_state    
    async def check_messages_for_web(self):
        while True:
            try:
                last_message = await self.messages_to_send_queue.get()
                await self.broadcast_message(last_message)
            except  asyncio.CancelledError :
                pass
   
    @validate_connection_state
    async def connection_handler(self,reader, writer):
        async def local_listerner(reader, writer):
            self.my_connections.append(writer)
            while True:
                data = await reader.read(4096)
                if not data:
                    await self.notification_queue.put(
                    Notification(NotificationType.WARNING,f"User {writer.get_extra_info('peername')}"))
                break
            message = data.decode().strip()
            msg_info = {
                "entry": message,
                "author_name": writer.get_extra_info('peername'), 
                "owner": False
            }
            await self.messages_queue.put(msg_info)

        await local_listerner(reader , writer)

    @validate_connection_state
    async def server_listener(self):
   
        async def serve(server):
            print("to servindo pra sempre")
            async with server:
                print("servidor iniciado")
                await server.serve_forever()

        server = None
        try:
            server = await asyncio.start_server(self.connection_handler, self.HOST, self.PORT)
            sock = server.sockets[0]
            local_port = sock.getsockname()[1]
            # update address/port and notify success
            self.onion_adress = f"{self.HOST}:{local_port}"
            await self.notification_queue.put(
            Notification(NotificationType.INFO, f"Server started on {self.HOST}:{local_port}")
            )
        except OSError as e:
            raise OSError(f"Failed to start server on {self.HOST}:{self.PORT}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while starting the server: {e}") from e
        self._connected = True
        self.server_task = asyncio.create_task(serve(server))

    @validate_connection_state            
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
                await self.notification_queue.put(
                    Notification(NotificationType.INFO, f"Error send message to {peername}"))
    
    @validate_connection_state    
    async def add_message_to_send(self,message):
        await self.messages_to_send_queue.put(message)
        
    # @validate_connection_state
    async def get_message_in_queue(self):
        return await self.messages_queue.get()
    
    async def get_notification_in_queue(self):
        return await self.notification_queue.get()