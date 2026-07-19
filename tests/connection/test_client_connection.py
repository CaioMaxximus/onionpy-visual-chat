from src.connection import ClientConnection
import unittest
from unittest.mock import patch , MagicMock ,AsyncMock
from src.error.special_errors import ConnectionClosedError
import asyncio


class TestClientConnection(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):

        not_bus = AsyncMock()
        self.inst = ClientConnection("test",not_bus)
        self.inst.PORT = 80
        self.inst.HOST  = "example.onion"
        self.inst.notify = AsyncMock()
        self.inst.notify.return_value = None


    async def test_raises_error_if_connection_didnt_start_yet(self):

              
        with self.assertRaises(ConnectionClosedError):
            await self.inst.connection_handler()


        with self.assertRaises(ConnectionClosedError):
            await self.inst.send_message()

        with self.assertRaises(ConnectionClosedError):
            await self.inst.close_connection()
    
    
    # STARTUP

    
    @patch("src.connection.client_connection.Proxy",new_callable=MagicMock())
    async def test_startup_handles_timeout_error_on_proxy_connect(self,proxy_mock):
        
        async_sock_mock = AsyncMock()
        async_sock_mock.side_effect = [TimeoutError]
        proxy_connection_mock = AsyncMock()
        proxy_connection_mock.connect = async_sock_mock
        proxy_mock.return_value = proxy_connection_mock

        # proxy_mock.connect.return_value = async_sock_mock

        with self.assertRaises(RuntimeError) as runtime_error:
            await self.inst.startup()
        
        self.assertEqual(str(runtime_error.exception) ,"Connection timeout in proxy connection example.onion:80")

    @patch("src.connection.client_connection.Proxy",new_callable=MagicMock())
    async def test_startup_handles_connection_error_on_proxy_connect(self,proxy_mock):
        
        async_sock_mock = AsyncMock()
        async_sock_mock.side_effect = [ConnectionError]
        proxy_connection_mock = AsyncMock()
        proxy_connection_mock.connect = async_sock_mock
        proxy_mock.return_value = proxy_connection_mock

        # proxy_mock.connect.return_value = async_sock_mock

        with self.assertRaises(ConnectionError) as connection_error:
            await self.inst.startup()
        
        self.assertEqual(str(connection_error.exception) ,"ConnectionError with proxy to the host example.onion:80")

    @patch("src.connection.client_connection.Proxy",new_callable=MagicMock())
    @patch("src.connection.client_connection.asyncio.open_connection",new_callable=MagicMock())
    async def test_startup_handles_timeout_error_on_open_connection(self,connection_mock, proxy_mock):
        
        proxy_connection_mock = AsyncMock()
        proxy_connection_mock.connect = AsyncMock()
        proxy_mock.return_value = proxy_connection_mock

        connection_mock.side_effect = [TimeoutError]
        # proxy_mock.connect.return_value = async_sock_mock

        with self.assertRaises(RuntimeError) as runtime_error:
            await self.inst.startup()
        
        self.assertEqual(str(runtime_error.exception) ,"Connection timeout trying to connect to server example.onion:80")

            
    @patch("src.connection.client_connection.Proxy",new_callable=MagicMock())
    @patch("src.connection.client_connection.asyncio.open_connection",new_callable=MagicMock())
    async def test_startup_handles_connection_error_on_open_connection(self,connection_mock, proxy_mock):
        
        proxy_connection_mock = AsyncMock()
        proxy_connection_mock.connect = AsyncMock()
        proxy_mock.return_value = proxy_connection_mock

        connection_mock.side_effect = [ConnectionError]
        # proxy_mock.connect.return_value = async_sock_mock

        with self.assertRaises(ConnectionError) as connection_error:
            await self.inst.startup()
        
        self.assertEqual(str(connection_error.exception) ,"Error! Unable to connect to server example.onion:80")

    # CONNECTION HANDLER

    @patch.object(ClientConnection , "_handshake", new_callable = AsyncMock)
    @patch.object(ClientConnection, "close_connection", new_callable=AsyncMock)
    async def test_connection_handler_dont_break_with_an_incompleted_input(self,close_connection_mock , handshake_mock ):

        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = AsyncMock()
        incompleted_exception = asyncio.exceptions.IncompleteReadError(MagicMock() , MagicMock())
        incompleted_exception.partial =  None
        mocked_reader.readuntil.side_effect = [True ,incompleted_exception]


        await self.inst.connection_handler(mocked_reader, mocked_writer)

        # self.assertEqual(self.inst.notify.call_count , 3)
        self.assertEqual(self.inst.close_connection.call_count , 1)

    @patch.object(ClientConnection , "_handshake", new_callable = AsyncMock)
    @patch.object(ClientConnection, "close_connection", new_callable=AsyncMock)
    async def test_connection_handler_dont_break_with_limit_overrun(self,close_connection_mock , handshake_mock ):

        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = AsyncMock()
        incompleted_exception = asyncio.exceptions.LimitOverrunError(MagicMock() , MagicMock())
        incompleted_exception.partial =  None
        mocked_reader.readuntil.side_effect = [True ,incompleted_exception]


        await self.inst.connection_handler(mocked_reader, mocked_writer)

        # self.assertEqual(self.inst.notify.call_count , 3)
        self.assertEqual(self.inst.close_connection.call_count , 1)


    async def send_message_handle_connection_related_errors(self):

        exceptions_to_handle = [BrokenPipeError ,ConnectionResetError , ConnectionRefusedError]
        writer_mocked = MagicMock()
        writer_mocked.drain = AsyncMock()
        writer_mocked.drain.side_effect = exceptions_to_handle
        self.inst.writer = writer_mocked

        for _ in exceptions_to_handle:

            self.inst.send_message(MagicMock())
        
        # self.assertEqual(self.inst.notify.call_count, 3)

    async def close_connection_handles_canceled_error(self):

        server_task_mock = MagicMock()
        server_task_mock.cancel.side_effect = asyncio.CancelledError

        # self.assertEqual(self.inst.notify.call_count , 1)
        self.assertAlmostEqual(self.inst._connected , False)

    async def close_connection_handles_generic_exception(self):

        server_task_mock = MagicMock()
        server_task_mock.cancel.side_effect = Exception

        # self.assertEqual(self.inst.notify.call_count , 1)
        self.assertAlmostEqual(self.inst._connected , False)