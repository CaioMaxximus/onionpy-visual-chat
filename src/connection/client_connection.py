import asyncio
from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType
from src.models import Notification , NotificationType
from typing import Any, Callable ,Optional
from decorators import validate_connection_state
from infrastructure import client_connection_handshake




## This will use an interface
class ClientConnection():

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
        start_connection()
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
       
        self.notification_bus.start()
        self.messages_queue = asyncio.Queue()



    
    async def run(self, host: str, port: int ) -> None:


        self.HOST = host
        self.PORT = int(port)
        await self.start_connection()
 
    @validate_connection_state
    async def close_connection(self):
        ## NEED TO WORK TO CLOSE WEB CONNECTION
        ## AND GARATEE THE END OF ALL PENDING TASKS
        self._connected = False
        try:
            self.server_task.cancel()
            await self.server_task
        except asyncio.CancelledError :
            pass
        except Exception:
            ## logg here
            pass
        await self.notification_bus.send(Notification(NotificationType.WARNING,
                                          "Connection finished with the server."))
        

    @validate_connection_state
    async def connection_handler(self,reader, writer):

        await self.notification_bus.send(Notification(NotificationType.INFO, "Starting handshake"))
        self.writer = writer
        handshake_data = client_connection_handshake("user novo" ,self.password)
        self.writer .write(handshake_data)
        await self.writer.drain()
        
        while self._connected:
            try:
                data = await reader.readuntil(separator=b'\0')

            except asyncio.IncompleteReadError as e:
                if e.partial:
                    data = e.partial
                    self._connected = False
                else:
                    await self.notification_bus.send(
                        Notification(NotificationType.WARNING, "Server closed connection.")
                    )
                    break
            except asyncio.LimitOverrunError as e:
                await self.notification_bus.send( Notification(NotificationType.ERROR, 
                    f"Message too large (> than {e.consumed} bytes)"))
                break

            except Exception:
                await self.notification_bus.send(
                                            Notification(NotificationType.WARNING, f"""Unexpected error from server: {writer.get_extra_info('peername')}
                                                        closing connection..."""))
                break

            try:
                message = data.decode().strip()
                msg_info = {
                    "entry": message,
                    "author_name": writer.get_extra_info('peername'), 
                    "owner": False
                }
            except UnicodeDecodeError as e:
                await self.notification_bus.send(
                    Notification(NotificationType.ERROR, 
                        f"Failed to decode message  {str(e)}"))
                break
            except ValueError as e:
                await self.notification_bus.send(
                    Notification(NotificationType.ERROR, 
                        f"Invalid message format f{str(e)}"))
                break
            except Exception as e:
                await self.notification_bus.send(
                    Notification(NotificationType.ERROR, 
                        f"Unexpected error decoding message {str(e)}"))
                break
            else:
                await self.messages_queue.put(msg_info)

        await self.close_connection()

    async def start_connection(self):

        try:
            self.proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = self.PROXY_PORT, rdns=True)
            self.sock  = await self.proxy.connect(dest_host = self.HOST,dest_port= self.PORT,timeout=10
            )   
        except TimeoutError as e:
            raise RuntimeError(f"Connection timeout in proxy connection {self.HOST}:{self.PORT}") from e
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to proxy {self.HOST}:{self.PORT}") from e
        
        try :
            reader,writer = await asyncio.open_connection( 
                sock = self.sock)
        except TimeoutError:
            raise RuntimeError(f"Connection timeout trying to connect to server {self.HOST}:{self.PORT}")
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to server {self.HOST}:{self.PORT}") from e
        else:

            self._connected = True
            self.server_task = asyncio.create_task(self.connection_handler(reader,writer))
        
    @validate_connection_state
    async def send_message(self, message):
        
        data = message["entry"].replace("\x00", "")
        data_encoded = (data + "\n\0").encode()
        w = self.writer

        w.write(data_encoded)
        try:
            await w.drain()
        except (ConnectionResetError , ConnectionRefusedError) as e: 
            await self.notification_bus.send(
                Notification(NotificationType.WARNING , 
                "Unable to send the message"))
        

    async def get_message_in_queue(self):
        msg = await self.messages_queue.get()
        return msg
    

    