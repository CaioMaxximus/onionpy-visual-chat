import customtkinter as ctk
from coordinator.application_coordinator import ApplicationCoordinator
from views.popup_entry_gui import PopUPEntryGui
HOST = '127.0.0.1'
PORT = 8080

class MainMenuGUI:

    def __init__(self,root , controller
                 ):
        
        self.root = root
        self.root.geometry("600x600")
        self.controler.run(self.root.loop)
        self.start_screen()

        self.controler.start_proxy(None)

        self.label = ctk.CTkLabel(root, text="WELCOLME! what do you wanna do now?")
        self.label.pack(pady = 30)

        self.createServerBtn = ctk.CTkButton(root, text = "Create a new server",
                                             command= self.create_new_server_window)
        self.createServerBtn.pack(pady = 20)

        self.enterServerBtn = ctk.CTkButton(root, text = "Enter in a new server",
                                            command= self.create_new_client_window)
        self.enterServerBtn.pack(pady = 20)
        
        self.bottow_frame = ctk.CTkFrame(self.root)
        self.bottow_frame.pack(fill="both")

        self.my_servers_list = ElementList(self.bottow_frame,self.iniatiate_server_window)
        self.my_servers_list.pack(side = "left", fill = "y" , padx=10, pady=10)

        self.my_visited_servers_list = ElementList(self.bottow_frame,print)
        self.my_visited_servers_list.pack(side = "right", fill = "y", padx=10, pady=10)

        self.controler.get_my_servers(lambda servers_names: self.my_servers_list.set_list(servers_names) )
        self.controler.get_my_servers(lambda servers_names: self.my_visited_servers_list.set_list(servers_names) )



    def create_new_server_window(self,server_name = "server_test",):
        pop_w = PopUPEntryGui(self.root, ["Define a name for the new server"], ["server_name"])
        self.root.wait_window(pop_w)
        server_name = pop_w.registered_values["server_name"]
        self.control.create_new_onion_server(
            server_name , 
            lambda server_name : self.iniatiate_server_chat_window(server_name))
        
    def create_new_client_window(self):
        ApplicationCoordinator.client_chat((self.root , 0))
        # ClientGUI(self.root,0 ,ClientConnection, host, port)
    
    def iniatiate_server_chat_window(self,server_name):
        ApplicationCoordinator.(self.root,server_name,0, ServerConnection,HOST,PORT)

class ElementList(ctk.CTkScrollableFrame):

    def __init__(self, master, callback, items = None):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.items = items
        self.buttons = {}
        self.polute_frame()
    
    def polute_frame(self):
        for i, e in enumerate(self.items):
            btn =  ctk.CTkButton(self,20,15,corner_radius= 8,
                                             command= lambda e = e: self.callback(e),
                                             text=e)
            btn.pack(fill = "x")
            self.buttons[i] = btn

    def set_items(self,items):
        self.items = items
        self.polute_frame()


            