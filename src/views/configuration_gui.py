from customtkinter import CTkFrame , CTkLabel ,CTkScrollableFrame




class ConfigurationGUI(CTkFrame):

    """
        Class represinting responsible to manage the stored servers and connectiio

    """

    def __init__(self, master , parent ,controller):
        super().__init__(parent)
        self.master = master
        self.parent = parent
        self.controller = controller
        # self.title("CONFIGURATION")
        self.height = 700
        self.width = 650
        self.build_interface()

    def build_interface(self):
        #  frame 1 content
        self.frame_1 = CTkFrame(self,height = self.height // 2)
        self.frame_1.pack(pady = 3.5, padx = 3.5, fill ="x")
        self.servers_label = CTkLabel(self.frame_1, text = "MY SERVERS")
        self.servers_label.pack(pady= 3.5)
        self.scroll_frame_servers = CTkScrollableFrame(self.frame_1, label_text="Local servers available")
        self.scroll_frame_servers.pack(fill="both", padx=7, pady=7)
        # frame 2 content
        self.frame_2 = CTkFrame(self,height = self.height // 2)
        self.discovered_server_labels = CTkLabel(self.frame_2 , text = "RECENTLY CONNECTED SERVERS")
        self.discovered_server_labels.pack(pady= 3.5)
        self.frame_2.pack(pady = 3.5, padx = 3.5, fill ="x")
        self.scroll_frame_discovered_server = CTkScrollableFrame(self.frame_2, label_text="Connections available")
        self.scroll_frame_discovered_server.pack(fill="both", padx=7, pady=7)