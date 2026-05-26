from src.connection.tor_service_manager import TorServiceManager
import unittest
from unittest.mock import patch , MagicMock




class TestTorServiceManager(unittest.TestCase):

    def setUp(self):
        self.manager = TorServiceManager()

    @patch.object(TorServiceManager, "check_server_exists")
    def test_create_new_onion_server_raises_if_already_exists(self, mock_check):
        mock_check.return_value = True

        with self.assertRaises(ValueError):
            self.manager .create_new_onion_server("server_1")
    
    def test_start_onion_server_raises_if_not_return(self):
        mocked_crt = MagicMock()
        mocked_crt.create_hidden_service.side_effect = Exception()

        mocked_context = MagicMock()
        mocked_context.__enter__.return_value = mocked_crt

        mocked_controller = MagicMock()
        mocked_controller.from_port.return_value = mocked_context

        with self.assertRaises(Exception):
            TorServiceManager._start_onion_server("teste" , 888 , 111,mocked_controller )
            # test_mock("teste" , 888 , 111,mocked_controller)


    @patch.object(TorServiceManager,"_start_onion_server")
    def test_global_controller_creation(self,mock_check):
        mock_check.return_value = ""
        self.assertEqual(self.manager.global_controller,None)
        self.manager .start_onion_server("","","")
        self.assertNotEqual(self.manager .global_controller,None)
    

    @patch.object(TorServiceManager, "check_server_exists")
    def test_stop_onion_server_raises_if_not_exists(self, mock_check):
        mock_check.return_value = False

        with self.assertRaises(ValueError):
            self.manager.stop_onion_server("Server")
        
    @patch.object(TorServiceManager, "check_server_exists")
    def test_remove_onion_server_raises_if_not_exists(self, mock_check):
        mock_check.return_value = False

        with self.assertRaises(FileNotFoundError):
            self.manager.remove_onion_service("Server")

    @patch("src.connection.tor_service_manager.subprocess.Popen")
    def test_start_tor_raises_if_invalid_path(self,mock_check):

        mock_check.side_effect = Exception()
        
        with self.assertRaises(ConnectionError):
            self.manager.start_tor(2)

import sys
print(sys.path)