from  controller import client_controler , menu_controller
from connection import client_connection ,server_connection ,tor_service_manager
from root.views import main_menu_gui, server_gui
from views import client_gui , main_menu_gui, server_gui
import queue

class ApplicationCoordinator:

    @classmethod
    def main_menu(cls, root):

        data_queue = queue.Queue()
        notification_queue = queue.Queue()
        menu_controller_instance = menu_controller.MenuController(
            tor_service_manager,data_queue,notification_queue)
        main_menu_gui_instance = main_menu_gui.MainMenuGUI(
            root,menu_controller_instance ,
            tor_service_manager)

        return main_menu_gui_instance
    

    @classmethod
    def client_chat(cls, master, index):

        data_queue = queue.Queue()
        notification_queue = queue.Queue()
        client_connection_instance = client_connection.ClientConnection()
        client_controller_instance = client_controler.ClientController(
            index, data_queue, notification_queue)
        client_connection_instance.set_callbacks(
            client_controller_instance._insert_message_in_queue,
            client_controller_instance._insert_notification_in_queue)
            
        client_gui_instance = client_gui.ClientGUI(
            master, client_controller_instance)

        return client_gui_instance
    
    @classmethod
    def server_chat(cls,master,server_name,hostname):
        
    
