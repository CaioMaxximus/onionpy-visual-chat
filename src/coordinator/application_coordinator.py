from controller import ClientController , ServerController ,MenuController
from connection import ClientConnection , ServerConnection , TorServiceManager
from views import MainMenuGUI , ClientGUI ,ServerGUI
from services import ClientService, ServerService
from data_base import repository
from infrastructure import NotificationBus

class ApplicationCoordinator():

    """
        This class is a Factory/Coordinator service, it establishes the workflow format injecting the dependecies
        for the UI components, and prevents tight coupling  and circular dependency

        Methods
        -------
        main_menu
            Instanciate the main aplication UI 
        client_chat
            Instanciate a client view window 
        server_chat
            Instanciate a server view window
        

    """

    @classmethod
    def main_menu(cls, root):

        menu_controller_instance = MenuController()
        main_menu_gui_instance = MainMenuGUI(
            root,menu_controller_instance ,cls.client_chat , cls.server_chat)

        return main_menu_gui_instance
    
    @classmethod
    def client_chat(cls, master, index, host  , port):

        notification_bus = NotificationBus() 
        client_connection_instance = ClientConnection(notification_bus)
        client_service_instance = ClientService(client_connection_instance,repository,TorServiceManager,notification_bus)
        client_controller_instance = ClientController(
            client_service_instance,notification_bus)
        client_gui_instance = ClientGUI(
            master, 0 ,client_controller_instance , host ,port)

        return client_gui_instance
    
    @classmethod
    def server_chat(cls,master,server_name, mode):
        # server_connection(server_name , )
        notification_bus = NotificationBus() 
        server_connection_instance = ServerConnection(server_name ,notification_bus, "")
        server_service_instance = ServerService(server_connection_instance,repository,TorServiceManager,notification_bus)
        server_controller_instance = ServerController(server_service_instance , server_name,notification_bus)
        server_gui = ServerGUI(master, server_name,0,server_controller_instance,mode)
        return server_gui
