import asyncio
from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType
from src.models import Notification , NotificationType
from typing import Any, Callable ,Optional
from decorators import validate_connection_state
from infrastructure import client_connection_handshake,handle_server_response
from .base_connection import BaseConnection
from models import ServerMessage


## This will use an interface
class ClientConnection(BaseConnection):

    """
        This class represents a active asynchronous connection between a client and a server
        using tor as a proxy.

        The connection run in the same event loop from the controller in a asynchronous task
        stored in the object -server_task-.
        The class keeps the incomming messages and the notifications in itself, to be collected by
        the controller layer during his life cycle.

        Attributes
        ----------

        password (not implement yet!): str
            Credential used to connect with the server
        HOST : str
            Hostname of the server
        PORT : int
            Server open port for the connection
        PROXY_PORT : int (default = 9050)
            Port to connect to tor proxy
        sock : Proxy.socket.socket
            Socket that defines the connection
        writer : StreamWriter
            Object to send data to the server
        _connected : Bool
            Indicates wether there is a active connecition running
        message_queue : asyncio.Queue
            Asynchronus queue to store the messages incoming from the web
      
        server_task : asyncio.Task
            Stores the task responsible to run the asynchronous connection
        
        Methods
        --------

        run()
            Initialize the queues inside the asynchronous event loop context an start the 
            connection process
        close_connection()
            Shuts down the connection asynchronous task and define the state as not connected
        startup()
            Configure the proxy, define a socket and starts a asyncion TCP connection
        connection_handler():
        send_message()
            Send a message comming from the controller layer to the connected server
        get_message_in_queue()
            Function called by the controller layer to collect messages comming from the server
    
    """

    def __init__(self, notification_bus : Notification,password = None):

        self.password = password
        self.HOST  = None 
        self.PORT = None
        self.PROXY_PORT = 9050
        self.sock = None
        self.writer = None  
        self._connected = False
        self.messages_queue = None
        self.notification_bus= notification_bus
        self.server_task :  Optional[asyncio.Task] = None

    def initialize(self):
       
        self.messages_queue = asyncio.Queue()

    
    async def run(self, name ,host: str, port: int ) -> None:

        self.name = name
        self.HOST = host
        self.PORT = int(port)
        return await self.startup()
 
    @validate_connection_state
    async def close_connection(self):
      

        self._connected = False
        try:
            self.server_task.cancel()
            await self.server_task
            
        except asyncio.CancelledError :
            # logg here
            pass
        except Exception:
            ## logg here
            pass
        await  self.notify(NotificationType.WARNING,
                                          "Connection finished with the server.")
        
    
    async def _handshake(self, reader , writer,name):
        
        # await reader
        res = None
        try:
            handshake_data = client_connection_handshake(name ,self.password)
            writer.write(handshake_data)
            await writer.drain()
        except Exception :
            raise ConnectionError
        try:
            ## add a timer here
            res = await asyncio.wait_for(reader.readuntil(separator=b'\0'), timeout=6.0)
        except Exception as e :
            raise ConnectionError
        try:
            data = handle_server_response(res)
        except:
            raise ConnectionAbortedError
        else:
            return data
        # reader.read


    @validate_connection_state
    async def connection_handler(self,reader, writer):


        
        while self._connected:
            try:
                data = await reader.readuntil(separator=b'\0')

            except asyncio.IncompleteReadError as e:
                if e.partial:
                    data = e.partial
                    self._connected = False
                else:
                    await self.notify(NotificationType.WARNING, "Server closed connection.")
                    
                    break
            except asyncio.LimitOverrunError as e:
                await  self.notify(NotificationType.ERROR, 
                    f"Message too large (> than {e.consumed} bytes)")
                break

            except Exception:
                await  self.notify(NotificationType.WARNING, f"""Unexpected error from server: {writer.get_extra_info('peername')}
                                                        closing connection...""")
                break

            try:
                # message = data.decode().strip()
                message_obj = ServerMessage.from_stream(data)
                msg_info = {
                    "entry": message_obj.message,
                    "author_name": message_obj.author, 
                    "owner": False,
                    "from_server" : message_obj.from_server
                }
            except UnicodeDecodeError as e:
                await self.notify(NotificationType.ERROR, 
                        f"Failed to decode message  {str(e)}")
                break
            except ValueError as e:
                await self.notify(NotificationType.ERROR, 
                        f"Invalid message format f{str(e)}")
                break
            except Exception as e:
                await self.notify(NotificationType.ERROR, 
                        f"Unexpected error decoding message {str(e)}")
                break
            else:
                await self.messages_queue.put(msg_info)

        await self.close_connection()

    async def startup(self):

        try:
            self.proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = self.PROXY_PORT, rdns=True)
            self.sock  = await self.proxy.connect(dest_host = self.HOST,dest_port= self.PORT,timeout=20
            )   
        except TimeoutError as e:
            raise RuntimeError(f"Connection timeout in proxy connection {self.HOST}:{self.PORT}") from e
        except ConnectionError as e:
            raise ConnectionError(f"ConnectionError with proxy to the host {self.HOST}:{self.PORT}") from e
        
        try :
            reader,writer = await asyncio.open_connection( 
                sock = self.sock)
        except TimeoutError:
            raise RuntimeError(f"Connection timeout trying to connect to server {self.HOST}:{self.PORT}")
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to server {self.HOST}:{self.PORT}") from e

        ## The server connected

        self.writer = writer
        await self.notify(NotificationType.INFO, "Starting handshake")


        try:
            server_handshake_data = await self._handshake(reader, writer, self.name)
        except Exception as e:
            await self.notify(NotificationType.WARNING, "Server handshake failed.")
            await self.close_connection()
            raise e
        else:
            await self.notify(NotificationType.SUCCESS, "Handshake sucefully")
            self._connected = True
            self.server_task = asyncio.create_task(self.connection_handler(reader,writer))
            self.server_task.add_done_callback(self.handle_tasks_errors)

        return server_handshake_data
        
    @validate_connection_state
    async def send_message(self, message):
        
        data = message["entry"].replace("\x00", "")
        data_encoded = (data + "\n\0").encode()
        w = self.writer

        w.write(data_encoded)
        try:
            await w.drain()
        except (BrokenPipeError ,ConnectionResetError , ConnectionRefusedError) as e: 
            await self.notify(NotificationType.WARNING , 
                "Unable to send the message")
        

    # async def get_message_in_queue(self):
    #     msg = await self.messages_queue.get()
    #     return msg
    

    