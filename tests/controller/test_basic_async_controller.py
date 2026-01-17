import asyncio
import unittest 
from src.controller import BasicAsyncController
from unittest.mock import MagicMock  , AsyncMock




class TestBasicAsyncController(unittest.IsolatedAsyncioTestCase):

    def mocked_gui_loop_after(self,time , callback ,*args):
        callback(*args)


    async def asyncSetUp(self) -> None:
        self.controller = BasicAsyncController(connection= MagicMock())
        self.controller.running = True
        moked_gui_loop = MagicMock()
        moked_gui_loop.after = self.mocked_gui_loop_after
        self.controller.gui_loop = moked_gui_loop
        self.controller.notification_queue = asyncio.Queue()
        
        

    async def test_dispatcher_callback(self):
        cb_function = MagicMock()
        exe_function = AsyncMock(return_value="ok")
        exe_function.configure_mock(__name__="mocked_exec")


        await self.controller.dispatcher_executer(exe_function ,
                                                         ("payload",) , cb_function)

        cb_function.assert_called_once_with("ok")


    async def test_dispatcher_schedule(self):
        exe_function = AsyncMock(return_value="ok")
        exe_function.configure_mock(__name__="mocked_exec")


        await self.controller.dispatcher_executer(exe_function , ("payload",) , None)


        exe_function.assert_called_once_with("payload")

    async def test_dispatcher_try_again_a_retryable_error(self):

        exe_function = AsyncMock(side_effect = [TimeoutError, ConnectionError , 
                                                ConnectionAbortedError , "ok"])
        exe_function.configure_mock(__name__="mocked_exec")
        cb_function = MagicMock()

        self.controller.max_attempts_retry = 4
        await self.controller.dispatcher_executer(exe_function ,
                                            ("payload",) , cb_function)
        
        self.assertEqual(exe_function.call_count, 4)

            

    async def test_dispacther_aborts_immediately_when_a_non_retryable_error_is_raised(self):

        exe_function = AsyncMock(side_effect = [ValueError, "ok"])
        exe_function.configure_mock(__name__="exe_function")

        cb_function = MagicMock()

        await self.controller.dispatcher_executer(exe_function, ("payload",), cb_function)
        exe_function.assert_called_once()
        cb_function.assert_not_called()
