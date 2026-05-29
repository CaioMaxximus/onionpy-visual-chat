from src.connection import ServerConnection
import unittest
from unittest.mock import patch , MagicMock ,AsyncMock
from src.error.special_errors import ConnetionClosedError



class TestServerConnection(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        not_bus = MagicMock()
        self.inst = ServerConnection("test",not_bus, "")

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
    
        