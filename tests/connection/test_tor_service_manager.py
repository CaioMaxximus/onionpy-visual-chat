from src.connection.tor_service_manager import TorServiceManager
import unittest
from unittest.mock import patch , MagicMock


manager = TorServiceManager()

class TestTorServiceManager(unittest.TestCase):

    @patch.object(TorServiceManager, "check_server_exists")
    def test_create_new_onion_server_raises_if_exists(self, mock_check):
        mock_check.return_value = True

        with self.assertRaises(ValueError):
            manager.create_new_onion_server("server_1")
    
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

    

import sys
print(sys.path)