import unittest
from unittest.mock import MagicMock
from src.controller.menu_controller import MenuController


class TestMenuController(unittest.TestCase):


    def mocked_gui_loop_after(self,time , callback ,*args):
        callback(*args)

    def setUp(self):
        self.controller = MenuController()
        moked_gui_loop = MagicMock()
        moked_gui_loop.after = self.mocked_gui_loop_after
        self.controller.gui_loop = moked_gui_loop


    def test_function_executer_callback(self):

        exe_func = MagicMock(return_value="ok")
        cb_func = MagicMock(return_value = "cb_ok")
        self.controller.function_executer(exe_func,() ,callback=cb_func)
        cb_func.assert_called_once_with("ok")


    def test_function_executer_error_handler(self):
        exe_func = MagicMock(side_effect = [TimeoutError] )
        cb_func = MagicMock(return_value = "cb_ok")
        self.controller.function_executer(exe_func,() ,callback=cb_func)
        cb_func.assert_not_called()
        self.assertEqual(self.controller.notification_queue.qsize(), 1)
