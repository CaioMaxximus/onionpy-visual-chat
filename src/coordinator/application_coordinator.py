from controller import ClientController , ServerController ,MenuController
from connection import ClientConnection , ServerConnection
from views import MainMenuGUI , ClientGUI ,ServerGUI
import queue

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

        client_connection_instance = ClientConnection()
        client_controller_instance = ClientController(
            client_connection_instance)
        client_gui_instance = ClientGUI(
            master, 0 ,client_controller_instance , host ,port)

        return client_gui_instance
    
    @classmethod
    def server_chat(cls,master,server_name, mode):
        # server_connection(server_name , )
        server_connection = ServerConnection(server_name , "")
        server_controller = ServerController(server_connection , server_name)
        server_gui = ServerGUI(master, server_name,0,server_controller,mode)
        return server_gui
