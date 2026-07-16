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

     