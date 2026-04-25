from customtkinter import CTkFrame , CTkLabel ,CTkScrollableFrame , CTkButton




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
        self.controller.get_my_servers(lambda x: self.update_servers_list(x))
        self.controller.get_discovered_servers(lambda x :self.update_discovered_servers_list(x))

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
    
        # hover effect no container
    def on_enter(self,e,container):
        container.configure(fg_color="#3a3a3a")

    def on_leave(self,e,container):
        container.configure(fg_color="#2b2b2b")


    def update_servers_list(self , servers_info):
        for s in servers_info:
            container = CTkFrame(
                self.scroll_frame_servers,
                height=15,
                fg_color="#2b2b2b",       # fundo levemente destacado
                corner_radius=8
            )
            container.pack(fill="x", pady=4, padx=4)


            # container.bind("<Enter>", lambda e, container : self.on_enter(e,container))
            # container.bind("<Leave>", lambda e, container : self.on_leave(e,container))

            info = CTkLabel(
                container,
                text=f"{s.name} - {(s.hostname)[0:35]}...",
                anchor="w"   # alinhamento à esquerda
            )
            info.pack(fill="x", side="left", padx=(8, 4))

            port_info = CTkLabel(
                container,
                text=f"{s.onion_port}",
                text_color="#aaaaaa"   # mais suave
            )
            port_info.pack(side="left", padx=(0, 6))

            action = CTkButton(
                container,
                text="→",
                width=30,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#555555",
                command=lambda _: print("clicou")
            )
            action.pack(side="right", padx=6)

    def update_discovered_servers_list(self , servers_info):
        for s in servers_info:
            container = CTkFrame(self.scroll_frame_discovered_server,height= 15)
            container.pack(fil = "x" ,pady = 3.5, padx = 3.5)
            info = CTkLabel(container,text= f"{s.name} - {(s.hostname)[0:35]}...")
            info.pack(fill = "x",side = "left")
            action = CTkButton(container, text= "-->" , command=lambda x : print("clicou"),
                               width= 20 )
            action.pack(side = "right")

# Trying later
# class PopUpDialogItemList(CTkFrame):

#     def __init__(self, parent):
#         super().__init__(parent)
    
#     def build