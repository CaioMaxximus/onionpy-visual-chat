import queue
import asyncio
from models.notification import Notification , NotificationType
import threading
from connection.tor_service_manager import TorServiceManager
from data_base import db_service_manager  as db
import random
import socket
from .basic_async_controller import BasicAsyncController

DYNAMIC_PORT_MIN = 49152
DYNAMIC_PORT_MAX = 65535

# 
# Temporary


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

    # def __init__(self,
    #              connection,
    #              server_name
    #              ) -> None:

    #     self.connection = connection
    #     self.PORT = None
    #     self.running =  False
    #     self.max_attempts_retry = 2
    #     self.notification_routine = None
    #     self.message_routine = None
    #     self.main_task = None
    #     self.server_name = server_name
    #     self.message_queue = None
    #     self.notification_queue = None
    #     self.function_queue = None
    #     self.main_routine = None
    #     self.size = 0
    #     self.my_loop = None


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
            print("tabelas de dados prontas!")
            # self.main_task = asyncio.create_task(
            #     self.check_function_queue()
            # )
            await db.create_tables()
            self.gui_loop.after(100,callback)
            print("vou criar a rotina do dispatcher")
            self.main_routine = asyncio.create_task(self.dispatcher())
            await self.main_routine
        asyncio.run(start())


    def start_server(self, name , callback):
        self._enqueue(self._start_server, name ,callback = callback)
    
    def create_server(self ,name , callback):
        self._enqueue(self._create_server , name, callback = callback)
            
    async def _create_server(self , name):
                
        try:
            TorServiceManager.create_new_onion_server(name)
            await self.notification_queue.put(Notification(NotificationType.INFO , "Server directory created."))
            used_ports = await db.list_all_ports()
            local_port  = _generate_new_available_port(used_ports) # type: ignore
            used_ports.append(local_port)
            onion_port  = _generate_new_available_port(used_ports) # type: ignore
            await self.connection.start_server(local_port)
            await self.start_routines()
            onion_connection = TorServiceManager.start_onion_server(self.server_name, local_port , onion_port)
            await self.notification_queue.put(Notification(NotificationType.INFO , "Server started"))
            await db.save_new_server(self.server_name,local_port , 
                               onion_connection.hostname, onion_port)
        except Exception as e:
            raise e
        finally:
            # precisso  dps isso aq para desfazer as criacoes de arquivos e  elementos na tabela se houver algum erro 
            pass
            

    async def _start_server(self ,name) -> None:

        await self.notification_queue.put(Notification(NotificationType.INFO , "Starting server.."))
        server_info = await db.get_server_by_name(name)
        await self.connection.start_server(server_info["local_server_port"]) # type: ignore
        await self.start_routines()

        onion_connection = TorServiceManager.start_onion_server(self.server_name, 
                                                                server_info["local_server_port"] , # type: ignore
                                                                server_info["onion_port"]) # type: ignore
        await self.notification_queue.put(Notification(NotificationType.INFO , "Server started"))
        print("criou td o server sem problema!")


    # def _enqueue(self, func, *args, callback=None):
    #     try:
    #         self.my_loop.call_soon_threadsafe(self.function_queue.put_nowait, # type: ignore
    #                                        (func, args, callback)) # type: ignore
    #         # self.size = self.function_queue.qsize()
    #         # print(list(self.function_queue))
    #     except Exception as e:
    #         raise e


    # def send_message_to_web(self, message: str, callback = None) -> None:
    #     self._enqueue(self.connection.add_message_to_send, message, callback = callback)


    # def get_web_message(self, callback = None) -> None:
    #     self._enqueue(self._get_web_message, callback = callback)


    # def get_notification(self, callback = None) -> None:
    #     self._enqueue(self._get_notification, callback = callback)

    # async def _get_notification(self) :
    #     # if self.notification_queue is None:
    #     #     return 
    #     # print("ta pedidndo notificacao ja")
    #     return await self.notification_queue.get()

    # async def _get_web_message(self):
    #     print("ta pedidndo mensagem ja")

    #     return await self.message_queue.get()
    
    # async def _insert_web_message_in_queue(self, message: str) -> None:
    #     await self.message_queue.put(message)
    

    # async def _insert_notification_in_queue(self, notification: str) -> None:
    #     await self.notification_queue.put( notification)
        
    # async def _get_notification_on_connection_routine(self):
    #     while True:
    #         try :
    #             notification = await self.connection.get_notification_in_queue()
    #             await self.notification_queue.put(notification)
    #         except asyncio.CancelledError:
    #             pass
            
    # async def _get_messages_on_connection_routine(self):
        # while True:
        #     try :
        #         msg = await self.connection.get_message_in_queue()
        #         await self.message_queue.put(msg)
        #     except asyncio.CancelledError:
        #         pass

      
    # async def check_function_queue(self):
    #     async def wrapped(func ,args , callback):
    #         attempt = 0
    #         while self.running:
    #             if attempt < self.max_attempts_retry:
    #                 try :
    #                     res = await func(*args)
    #                 except RETRYABLE_ERRORS as e:
    #                     await self.notification_queue.put(
    #                         Notification(NotificationType.WARNING, f"{str(e)}")
    #                     )
    #                     attempt +=1
    #                     pass 
    #                 except Exception as e:
    #                     await self.notification_queue.put(
    #                         Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
    #                     )
    #                     attempt =  self.max_attempts_retry
    #                 else:
    #                     self._execute_callback(callback , res)
    #                     break
    #             else:
    #                 await self.notification_queue.put(Notification(NotificationType.INFO ,
    #                                                    f"Aborting execution of {func.__name__}:"))
    #                 break
                

    #     while True:

    #         # print(f"to no my_loop da task manager {self.function_queue.qsize()}")
    #         func, args ,  callback = await self.function_queue.get()
    #         # print("A FUNCTION QUEUE TA RODADNDO !!@!!")
    #         asyncio.create_task(wrapped(func , args ,  callback))
            

    # def _execute_callback(self,callback , *args):
    #     if callback is not None:
    #         self.gui_loop.after(10,callback,*args)


