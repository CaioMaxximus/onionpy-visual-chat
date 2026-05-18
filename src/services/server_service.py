import asyncio
import inspect
from src.models import Notification , NotificationType
from models import OnionServer
import random
import socket

DYNAMIC_PORT_MIN = 49152
DYNAMIC_PORT_MAX = 65535

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
## put this funciotn in a utility module
def _generate_new_available_port(used_ports: set[int]) -> int:
    while True:
        port = random.randint(DYNAMIC_PORT_MIN, DYNAMIC_PORT_MAX)

        if port in used_ports:
            continue

        if _is_port_free(port):
            return port

## put this funciotn in a utility module
def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False
class ServerService():

    def __init__(self, connection, database_service, tor_service, notification_bus):
        self.connection = connection
        self.database_service = database_service
        self.tor_service = tor_service
        self.notification_bus = notification_bus
        self.connected = False
        self.server_name = None



    async  def start(self):
        # self.message_queue = asyncio.Queue()
        # self.notification_queue = asyncio.Queue()
        # self.HOST = HOST
        # self.port = PORT
        self.connection.initialize()
        pass


    async def _close_connection(self) -> None:
        if self.connected:
            await self.connection.close_connection()
            self.connected = False
        else:
            raise ConnectionError("The connection is already closed!")
   

    @rollback        
    async def _create_server(self ,rollback_operations, name):
        
        """
            Establish the steps to create a new valid server, attaching a decorator rollback feature.

            Parameters
            ---------
            rollback_operations : list
                functions to be executed during the rollback process
            name : str
                name of the new server
            Returns
            -------
            Onion_connection 
                Object representing the created onion server connection.
            ------
            Exception
                Propagates any exception raised during the setup process after
                registering rollback steps.
            Notes
            -----
            This method contains multiple side effects:
            - Creates and remove onion services
            - Starts and stops a local server
            - Writes fundamental content to the databbase
            - Emits notificaitons
        """

        onion_connection = None
        self.tor_service.create_new_onion_server(name)
        self.server_name = name

        rollback_operations.append(lambda : self.tor_service.remove_onion_service(name))
        await self.notification_bus.send(Notification(NotificationType.WARNING , "Server directory created."))
        used_ports = await self.database_service.list_all_ports() 
        local_port  = _generate_new_available_port(used_ports) # type: ignore
        used_ports.append(local_port)
        onion_port  = _generate_new_available_port(used_ports) # type: ignore
        await self.connection.start_server(local_port)
        rollback_operations.append(lambda : self.connection.close_server())
        # Move this for the start of the controller
        # await self.start_routines()
        # rollback_operations.append(self.stop_routines)
        onion_hostname  = self.tor_service.start_onion_server(self.server_name, local_port , onion_port)
        rollback_operations.append(lambda : self.tor_service.stop_onion_server(self.server_name))
        await self.notification_bus.send(Notification(NotificationType.SUCCESS , "Server started"))
        await self.database_service.save_new_server(self.server_name,local_port , 
                            onion_hostname, onion_port)
        rollback_operations.append(lambda : self.database_service.remove_server(self.server_name))
        onion_server = OnionServer(name,onion_hostname,local_port,onion_port) 
            
        return onion_server

            
    async def _start_server(self,name) -> OnionServer:
        """
            Establish the steps to start a new valid server, attaching a decorator rollback feature.

            Parameters
            ---------
            rollback_operations : list
                functions to be executed during the rollback process
            name : str
                name of the target server
            Returns
            -------
            Onion_connection 
                Object representing the started onion server connection.
            ------
            Exception
                Propagates any exception raised during the setup process after
                registering rollback steps.
            Notes
            -----
            This method contains multiple side effects:
            - Creates and remove onion services
            - Starts and stops a local server
            - Emits notificaitons
        """
        self.server_name = name
        await self.notification_bus.send(Notification(NotificationType.WARNING , "Starting server.."))
        server_info = await self.database_service.get_server_by_name(name)
        await self.connection.start_server(server_info.local_server_port) # type: ignore
        # await self.start_routines()

        print("o seervidor local iniciou!!")

        self.tor_service.start_onion_server(self.server_name, 
                                            server_info.local_server_port , # type: ignore
                                            server_info.onion_port) # type: ignore
        await self.notification_bus.send(Notification(NotificationType.SUCCESS , "Server started"))

        # onion_connection = OnionConnection(onion_hostname ,
        #                                     server_info["onion_port"],name, server_info["local_server_port"])
        return server_info

    async def close_server(self):
        
        await self.connection.close_server()
        self.tor_service.stop_onion_server(self.server_name)
        
    
    async def get_message(self):
        return await self.connection.get_message_in_queue()
    
    async def send_message(self, message):
        await self.connection.send_message(message)