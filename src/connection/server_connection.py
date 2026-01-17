import asyncio
import re
# from connection.tor_service_manager import TorServiceManager
from models.notification import Notification , NotificationType
from typing import Any, Callable
from src.error.special_errors import ConnetionClosedError

## Temporary


class ServerConnection():
    def __init__(self, name  , pin = None):
        self.users = []
        self.name = name
        # self.max_number_of_connections = max_number_of_connections
        self.pin = pin

        self.onion_adress = ""
        self._active  = True
        self.PORT = None
        self.HOST = "127.0.0.1"
        self.my_connections = []
        self._connected = False
        self.broadcast_queue : asyncio.Queue
        self.message_queue: asyncio.Queue
        self.notification_queue : asyncio.Queue
        
        self.server_task : asyncio.Task  
        self.check_messages_for_web_task : asyncio.Task
        self.broadcast_messages_task : asyncio.Task 
        
    def validate_connection_state(func : Callable) -> Callable:
        async def inner_wrapper(self ,*args, **kwargs):
            if self._connected:
                return await func(self,*args, **kwargs)
            else:
                raise ConnetionClosedError("The connection didnt start yet!")
        return inner_wrapper
    

    @validate_connection_state    
    async def close_server(self):
        self._connected = False
        try:
            self.check_messages_for_web_task.cancel()
            await self.check_messages_for_web_task
        except asyncio.CancelledError:
            pass
        # print("fechei a web task!")

        for writer in self.my_connections:
            writer.close()
            await writer.wait_closed()
        # print("fechei os meu writers")

        self.server.close()
        await self.server.wait_closed()

    #to implement
    def delete_user(self, user_id):
        self.users.remove(user_id)
        self.local_black_list.append()
    
    
    async def start_server(self ,port):

        self.message_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()
        # self.messages_to_send_queue = asyncio.Queue()
        self.broadcast_queue = asyncio.Queue()
        self.PORT  = port
        self._connected = True
        await self.server_listener() 


    @validate_connection_state    
    async def check_messages_for_web(self):
        while self._connected:
            try:
                last_message = await self.broadcast_queue.get()
                await self.broadcast_message(last_message)
            except  asyncio.CancelledError :
                pass
   
    @validate_connection_state
    async def connection_handler(self,reader, writer):
        async def local_listerner(reader, writer):
            # print("acabou de conectar alguem!!")
            self.my_connections.append(writer)
            while True:
                try:

                    data = await reader.readuntil(separator=b'\0')

                except asyncio.exceptions.IncompleteReadError as e:
                    data = e.partial
                    if not data:
                        await self.notification_queue.put(
                            Notification(NotificationType.WARNING, f"User {writer.get_extra_info('peername')}"))
                        break
                except:
                    await self.notification_queue.put(
                                                Notification(NotificationType.WARNING, f"""Unexpected error from user: {writer.get_extra_info('peername')}
                                                             closing connection..."""))
                    break
                if not data: ## this block might be unecessary..
                    await self.notification_queue.put(
                    Notification(NotificationType.WARNING,f"User {writer.get_extra_info('peername')}"))
                    break

                message = data.decode().strip()
                msg_info = {
                    "entry": message,
                    "author_name": writer.get_extra_info('peername'), 
                    "owner": False
                }
                await self.message_queue.put(msg_info)
                await self.broadcast_queue.put(msg_info)

        await local_listerner(reader , writer)
    

    @validate_connection_state
    async def server_listener(self):
   
        async def serve(server):
            # print("to servindo pra sempre")
            async with server:
                print("servidor iniciado")
                await server.serve_forever()

        server = None
        try:
            server = await asyncio.start_server(self.connection_handler, self.HOST, 
                                                self.PORT,reuse_address = True)
            sock = server.sockets[0]
            self.server = server
            print("serviu na porta adequada")

            local_port = sock.getsockname()[1]
            # update address/port and notify success
            self.onion_adress = f"{self.HOST}:{local_port}"
            await self.notification_queue.put(
            Notification(NotificationType.SUCCESS, f"Server started on {self.HOST}:{local_port}")
            )
        except OSError as e:
            raise OSError(f"Failed to start server on {self.HOST}:{self.PORT}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while starting the server: {e}") from e
        
        self._connected = True
        # self.server_task = asyncio.create_task(serve(server))
        self.check_messages_for_web_task = asyncio.create_task(self.check_messages_for_web())
        # self.broadcast_messages_task = asyncio.create_task(self.broadcast_routine())


    @validate_connection_state            
    async def broadcast_message(self, message):
        data = message["entry"]
        print(f"a mensagem foi :{data}")
        data_encoded = (data + "\n").encode()



        for w in self.my_connections:
            peername = w.get_extra_info('peername')
            print(message, peername, sep="\n==========\n")

            try:
                if message["author_name"] != peername:
                    w.write(data_encoded)
                    await w.drain()
            except (ConnectionResetError , ConnectionRefusedError): 
                await self.notification_queue.put(
                    Notification(NotificationType.INFO, f"Error send message to {peername}"))
    
    @validate_connection_state    
    async def send_message(self,message):
        await self.broadcast_queue.put(message)
        
    # @validate_connection_state
    async def get_message_in_queue(self):
        return await self.message_queue.get()
    
    async def get_notification_in_queue(self):
        return await self.notification_queue.get()