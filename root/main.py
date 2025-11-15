import customtkinter as ctk
from views.ServerGUI import ServerGUI
from views.ClientGUI import ClientGUI
from views.PopUpGui import PopUPGui
ctk.set_appearance_mode("dark")       # "light" ou "system"
ctk.set_default_color_theme("dark-blue")# ou "green", "dark-blue", etc.
from connection.ServerConnection import ServerConnection
from connection.ClientConnection import ClientConnection
from connection.TorServiceManager import TorServiceManager


HOST = '127.0.0.1'
PORT = 8080

class App:

    def __init__(self,root):
        self.root = root
        self.root.geometry("600x600")
        
        self.label = ctk.CTkLabel(root, text="WELCOLME! what do you wanna do now?")
        self.label.pack(pady = 30)

        self.createServerBtn = ctk.CTkButton(root, text = "Create a new server",
                                             command= self.create_new_server_window)
        self.createServerBtn.pack(pady = 20)

        self.enterServerBtn = ctk.CTkButton(root, text = "Enter in a new server",
                                            command= self.create_new_client_window)
        self.enterServerBtn.pack(pady = 20)
        # ServerGUI(self.root,0)

    
    def create_new_server_window(self,server_name = "server_test"):
        
        TorServiceManager.create_new_onion_server(server_name)
        ServerGUI(self.root,server_name,0, ServerConnection,HOST,PORT)
        # pass
        
    def create_new_client_window(self):
        pop_w = PopUPGui(self.root,["Enter the Server Adress"],["onion_adress"])
        self.root.wait_window(pop_w)
        host_port = pop_w.registered_values["onion_adress"].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1  else 80
        TorServiceManager.start_tor_proxy()
        # print("============== sai do start do proxy")
        ClientGUI(self.root,0 ,ClientConnection, host, port)



if __name__ == '__main__':
    root = ctk.CTk()
    App(root)
    root.mainloop()    

    