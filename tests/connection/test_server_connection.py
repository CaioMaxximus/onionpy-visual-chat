from src.connection import ServerConnection
import unittest
from unittest.mock import patch , MagicMock ,AsyncMock
from src.error.special_errors import ConnetionClosedError



class TestServerConnection(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        not_bus = MagicMock()
        self.inst = ServerConnection("test",not_bus, "")
        self.inst.PORT = 80


    def mock_server_listener(self,task_mock , server_mock):
        # self.inst._connected = True
        self.inst.check_messages_for_web = MagicMock()
        task_mock.return_value = True
        server_mock.return_value = AsyncMock()
        self.inst.notification_bus.send = AsyncMock()
        

    async def test_raises_error_if_connection_didnt_start_yet(self):

      
        with self.assertRaises(ConnetionClosedError):
            await self.inst.check_messages_for_web()
        
        with self.assertRaises(ConnetionClosedError):
            await self.inst.connection_handler()

        with self.assertRaises(ConnetionClosedError):
            await self.inst.broadcast_message()

        with self.assertRaises(ConnetionClosedError):
            await self.inst.send_message()

        with self.assertRaises(ConnetionClosedError):
            await self.inst.close_server()
    
    @patch("src.connection.server_connection.asyncio.start_server",new_callable=AsyncMock)
    @patch("src.connection.server_connection.asyncio.create_task")
    async def test_server_listener_starts_server(self,task_mock , server_mock):
        self.mock_server_listener(task_mock , server_mock)
        await self.inst.server_listener()
        server_mock.assert_called_once()
    
    
    @patch("src.connection.server_connection.asyncio.start_server",new_callable=AsyncMock)
    @patch("src.connection.server_connection.asyncio.create_task")
    async def test_server_listener_raises_specialized_OS_error(self,task_mock , server_mock):
        self.mock_server_listener(task_mock , server_mock)
        server_mock.side_effect = OSError()
        with self.assertRaises(OSError) as oserror:
            await self.inst.server_listener()
        
        self.assertEqual(str(oserror.exception) ,"Failed to start server on 127.0.0.1:80")

             

    @patch("src.connection.server_connection.asyncio.start_server",new_callable=AsyncMock)
    @patch("src.connection.server_connection.asyncio.create_task")
    async def test_server_listener_raises_specialized_RuntimeError_error(self,task_mock , server_mock):
        self.mock_server_listener(task_mock , server_mock)
        server_mock.side_effect = Exception()
        with self.assertRaises(RuntimeError) as rerror:
            await self.inst.server_listener()
        server_mock.assert_called_once()
        self.assertEqual(str(rerror.exception), "Unexpected error while starting the server")

    @patch("src.connection.server_connection.asyncio.start_server",new_callable=AsyncMock)
    @patch("src.connection.server_connection.asyncio.create_task")
    async def test_server_listener_send_notification_when_starts(self,task_mock , server_mock):
        print("testando o bus")
        self.mock_server_listener(task_mock , server_mock)
        await self.inst.server_listener()
        self.inst.notification_bus.send.assert_called_once()
    
