from src.connection import ServerConnection
import unittest
from unittest.mock import patch , MagicMock ,AsyncMock
from src.error.special_errors import ConnectionClosedError
import asyncio


class TestServerConnection(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        not_bus = MagicMock()
        self.inst = ServerConnection("test",not_bus)
        self.inst.PORT = 80
        self.inst.notification_bus.send = AsyncMock()


    def mock_server_listener(self,task_mock , server_mock):
        # self.inst._connected = True
        self.inst.check_messages_for_web = MagicMock()
        task_mock.return_value = True
        server_mock.return_value = AsyncMock()
        

    async def test_raises_error_if_connection_didnt_start_yet(self):

      
        with self.assertRaises(ConnectionClosedError):
            await self.inst.check_messages_for_web()
        
        with self.assertRaises(ConnectionClosedError):
            await self.inst.connection_handler()

        with self.assertRaises(ConnectionClosedError):
            await self.inst.broadcast_message()

        with self.assertRaises(ConnectionClosedError):
            await self.inst.send_message()

        with self.assertRaises(ConnectionClosedError):
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


    @patch("src.connection.server_connection.server_connection_handshake", new_callable = AsyncMock)
    async def test_connection_handler_dont_break_in_invalid_messages_with_excessive_size(self,handshake_mock):
        
        # handshake_mock.side_effect
        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = MagicMock()
        mocked_reader.readuntil.side_effect = [True ,asyncio.exceptions.LimitOverrunError]

        await self.inst.connection_handler(mocked_reader, mocked_writer)

        self.assertEqual(self.inst.notification_bus.send.call_count , 2)
        self.assertEqual(len(self.inst.my_connections) , 0)

    @patch("src.connection.server_connection.server_connection_handshake", new_callable = AsyncMock)
    async def test_connection_handler_dont_break_with_an_incompleted_input(self,handshake_mock):

        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = MagicMock()
        incompleted_exception = asyncio.exceptions.IncompleteReadError(MagicMock() , MagicMock())
        incompleted_exception.partial =  None
        mocked_reader.readuntil.side_effect = [True ,incompleted_exception]


        await self.inst.connection_handler(mocked_reader, mocked_writer)

        self.assertEqual(self.inst.notification_bus.send.call_count , 2)
        self.assertEqual(len(self.inst.my_connections) , 0)

    @patch("src.connection.server_connection.server_connection_handshake", new_callable = AsyncMock)
    async def test_connection_handler_dont_break_with_an_incompleted_input_with_partial_data(self,handshake_mock):

        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = MagicMock()
        incompleted_exception = asyncio.exceptions.IncompleteReadError(MagicMock() , MagicMock())
        incompleted_exception.partial =  "xxx"
        mocked_reader.readuntil.side_effect = [True, incompleted_exception, ValueError]

        await self.inst.connection_handler(mocked_reader, mocked_writer)

        self.assertEqual(self.inst.notification_bus.send.call_count , 2)
        self.assertEqual(len(self.inst.my_connections) , 0)

    @patch("src.connection.server_connection.server_connection_handshake", new_callable = AsyncMock)
    async def test_connection_handler_dont_break_with_bad_formed_input(self,handshake_mock):

        self.inst._connected = True
        mocked_reader = AsyncMock()
        mocked_writer = MagicMock()
        mocked_data = MagicMock()
        mocked_data.decode.side_effect = UnicodeDecodeError
        mocked_reader.readuntil.return_value = [True , mocked_data]

        await self.inst.connection_handler(mocked_reader, mocked_writer)

        self.assertEqual(self.inst.notification_bus.send.call_count , 2)
        self.assertEqual(len(self.inst.my_connections) , 0)

    async def test_close_server_finish_connection_even_if_check_messages_for_web_task_rises_exception(self):
        
        self.inst._connected = True
        writer_mock = AsyncMock()
        server_mock = AsyncMock()
        server_mock.close = MagicMock()
        server_mock.wait_closed = AsyncMock()
        self.my_connections = [writer_mock]
        self.inst.server = server_mock
        self.inst.check_messages_for_web_task = MagicMock()
        self.inst.check_messages_for_web_task.cancel.side_effect = asyncio.CancelledError

        await self.inst.close_server()

        self.assertEqual(len(self.inst.my_connections),0)
        server_mock.close.assert_called_once()
        server_mock.wait_closed.assert_called_once()
    
    async def test_close_server_finish_connection_even_if_a_writer_rises_exception(self):


        class AwaitableMock(AsyncMock):
            def __await__(self):
                return self().__await__()
            
            def cancel(self):
                return None
                
        self.inst._connected = True
        writer_mock1 = AsyncMock()
        writer_mock2 = AsyncMock()
        writer_mock2.close.side_effect = asyncio.CancelledError
        server_mock = AsyncMock()
        server_mock.close = MagicMock()
        server_mock.wait_closed = AsyncMock()
        self.my_connections = [writer_mock1,writer_mock2]
        self.inst.server = server_mock
        self.inst.check_messages_for_web_task = AwaitableMock()
        # self.inst.check_messages_for_web_task.return_value = AsyncMock()
        # self.inst.check_messages_for_web_task.wait_closed = AsyncMock()

        await self.inst.close_server()

        self.assertEqual(len(self.inst.my_connections),0)
        server_mock.close.assert_called_once()
        server_mock.wait_closed.assert_called_once()
    
