import queue
import asyncio
from src.models.notification import Notification , NotificationType
import threading
from src.connection import TorServiceManager
from data_base import db_service_manager  as db
import random
import socket
from .basic_async_controller import BasicAsyncController
import inspect
# from threading import Thread
from src.error.special_errors import ConnetionClosedError

DYNAMIC_PORT_MIN = 49152
DYNAMIC_PORT_MAX = 65535

# 
# Temporary


# create a class for this   
def rollback(func):
    async def inner_wrapper(self,*args , **kwargs):
        rollback_operations = []
        try:
            return await func(self,rollback_operations ,*args ,**kwargs)
        except Exception as e:
            for op in reversed(rollback_operations):
                    try :
                        res = op
                        if inspect.isawaitable(res):
                            await res()
                        else:
                            res()

                    except:
                        pass
            raise e

            
    return inner_wrapper

## Move this class to his own file
class OnionConnection():
    def __init__(self, onion_address, onion_port, server_name, local_port):
        self.hostname = onion_address
        self.onion_port = onion_port
        self.server_name = server_name
        self.local_port = local_port
        # self.id = id(self)
        # self.connected = False

## put this funciotn in a utility module
def _generate_new_available_port(used_ports: set[int]) -> int:
    while True:
        port = random.randint(DYNAMIC_PORT_MIN, DYNAMIC_PORT_MAX)

        if port in used_ports:
            continue

        if _is_port_free(port):
            return port

def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


class ServerController(BasicAsyncController):

    def __init__(self, connection , server_name):
        super().__init__(connection)
        self.server_name = server_name



    def run(self, gui_root , callback) -> None:
        
        if not self.running:
            self.gui_loop = gui_root
            # self.PORT = port
            self.running = True
            thread = threading.Thread(
                target=self.start_event_loop,
                args=(callback,),   
                daemon=True)

            thread.start()
            
        
    def start_event_loop(self ,callback):
    
        async def start():
            self.message_queue = asyncio.Queue()
            self.notification_queue = asyncio.Queue()
            self.function_queue = asyncio.Queue()
            self.my_loop = asyncio.get_running_loop()
            await db.create_tables()
            self.gui_loop.after(100,callback)
            self.running =  True
            self.main_routine = asyncio.create_task(self.dispatcher())
            await self.main_routine
        try:
            asyncio.run(start())
        except asyncio.CancelledError:
            pass
        print("==========")
        print("este controle foi encerrado com sucesso a thread acaba de moerrer filhote !!!")


    def start_server(self, name , callback):
        self._enqueue(self._start_server, name ,callback = callback)
    
    def create_server(self ,name , callback):
        self._enqueue(self._create_server , name, callback = callback)

    def close_server(self ,callback):
        self._enqueue(func=self._close_server,callback=callback)



    def close_controller(self):
        print("chamei da thread principal")
        self.my_loop.call_soon_threadsafe( # type: ignore
            lambda: asyncio.create_task(self._close_controller())  # type: ignore
        )
    
    async def _close_server(self):
        TorServiceManager.stop_onion_server(self.onion_controller)
        await self.connection.close_server()
    
    async def _close_controller(self):
        print("chamei o close controller!!")

        try: 
            await self._close_server()
        except ConnetionClosedError:
            pass 
        await self.stop_routines()
    



    @rollback        
    async def _create_server(self ,rollback_operations, name):
                

        onion_connection = None
        TorServiceManager.create_new_onion_server(name)

        rollback_operations.append(lambda : TorServiceManager.remove_onion_service(name))
        await self.notification_queue.put(Notification(NotificationType.WARNING , "Server directory created."))
        used_ports = await db.list_all_ports() 
        local_port  = _generate_new_available_port(used_ports) # type: ignore
        used_ports.append(local_port)
        onion_port  = _generate_new_available_port(used_ports) # type: ignore
        await self.connection.start_server(local_port)
        rollback_operations.append(lambda : self.connection.close_server())
        await self.start_routines()
        rollback_operations.append(self.stop_routines)
        onion_hostname , onion_controller = TorServiceManager.start_onion_server(self.server_name, local_port , onion_port)
        self.onion_controller = onion_controller
        rollback_operations.append(lambda : TorServiceManager.stop_onion_server(self.onion_controller))
        await self.notification_queue.put(Notification(NotificationType.SUCCESS , "Server started"))
        await db.save_new_server(self.server_name,local_port , 
                            onion_hostname, onion_port)
        rollback_operations.append(lambda : db.remove_server(self.onion_controller))
        onion_connection = OnionConnection(onion_hostname,onion_port,
                                            name,local_port) 
            
        return onion_connection

            
    async def _start_server(self,name) -> OnionConnection:

        await self.notification_queue.put(Notification(NotificationType.WARNING , "Starting server.."))
        server_info = await db.get_server_by_name(name)
        await self.connection.start_server(server_info["local_server_port"]) # type: ignore
        await self.start_routines()

        onion_hostname  ,  onion_controller= TorServiceManager.start_onion_server(self.server_name, 
                                                                server_info["local_server_port"] , # type: ignore
                                                                server_info["onion_port"]) # type: ignore
        await self.notification_queue.put(Notification(NotificationType.SUCCESS , "Server started"))
        self.onion_controller = onion_controller

        onion_connection = OnionConnection(onion_hostname ,
                                            server_info["onion_port"],name, server_info["local_server_port"])
        return onion_connection