from customtkinter import (CTkFrame , CTkLabel ,
                           CTkScrollableFrame , CTkButton , CTkToplevel)




class ConfigurationGUI(CTkFrame):

    """
        Class  representing a view responsible to manage the stored servers and connections

    """

    def __init__(self, master , parent ,controller):
        super().__init__(parent)
        self.master = master
        self.parent = parent
        self.controller = controller
        # self.title("CONFIGURATION")
        self.height = 700
        self.width = 650
        self.dialog_pop_up = None
        self.build_interface()
        self.controller.get_servers(lambda x: self.update_servers_list(x))
        self.controller.get_discovered_servers(lambda x :self.update_discovered_servers_list(x))

    def build_interface(self):
        #  frame 1 content
        top_frame = CTkFrame(self,height=40)
        top_frame.pack(fill = "x")
        back_to_menu_btn = CTkButton(top_frame,height=30 , width=35,text="←" , command= lambda : self.return_to_menu())
        back_to_menu_btn.pack(side = "left",padx = 3.5 , pady = 4.5)
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
        for  wigdet in self.scroll_frame_servers.winfo_children():
            wigdet.destroy()
        # self.scroll_frame_servers.clear()
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

            attributes = [("server name",s.name) , ("hostname" ,s.hostname) ,
                           ("local server port" , s.local_server_port) ,("onion port" , s.onion_port)]
            actions = [("red" ,"DELETE SERVER" , lambda item = s : self._remove_discovered_server(item))]
            action = CTkButton(
                container,
                text="→",
                width=30,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#555555",
                command=lambda item = s ,att = attributes , act = actions: self.open_dialog_box( item , att,act )
            )
            action.pack(side="right", padx=6)
    

    ## There is a vusal bug here , a new object is created but the pop up window is the same
    def open_dialog_box(self, item, attributes, actions):
        print(f"abri o dialog box do intem {item.name}")
        if self.dialog_pop_up is not None:
            print("Tem uma janela ativa")
            self.dialog_pop_up.on_close()
            self.dialog_pop_up = None
        print("insatanciando a janela")
        self.dialog_pop_up = PopUpDialogItemList(self,item,attributes,actions)
        
        
    def update_discovered_servers_list(self , servers_info):
        for  wigdet in self.scroll_frame_discovered_server.winfo_children():
            wigdet.destroy()
        # self.scroll_frame_discovered_server.clear()
        for s in servers_info:
            container = CTkFrame(self.scroll_frame_discovered_server,height= 15)
            container.pack(fil = "x" ,pady = 3.5, padx = 3.5)
            info = CTkLabel(container,text= f"{s.name} - {(s.hostname)[0:35]}...")
            info.pack(fill = "x",side = "left")
            attributes = [("server name",s.name) , ("hostname" ,s.hostname) ,
                           ("port" , s.port)]
            actions = [("red" ,"DELETE CONNECTION" , lambda item = s : self._remove_discovered_server(item))]
            action = CTkButton(
                container,
                text="→",
                width=30,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#555555",command=lambda item = s : self.open_dialog_box(item,attributes,actions))
            action.pack(side="right", padx=6)

    def _remove_server(self, server):
        def update():
            self.controller.get_servers(lambda x: self.update_servers_list(x))
            self.dialog_pop_up.destroy()
            self.dialog_pop_up = None
        self.controller.remove_server(server.name,lambda _ : update())
    

    def _remove_discovered_server(self, server):
        def update():
            self.controller.get_discovered_servers(lambda x: self.update_discovered_servers_list(x))
            self.dialog_pop_up.destroy()
            self.dialog_pop_up = None
        self.controller.remove_discovered_server(server.hostname,lambda _ : update())
    
    def return_to_menu(self):
        self.destroy()
        # super().place_forget()

# Trying later
class PopUpDialogItemList(CTkToplevel):

    def __init__(self, parent, element , attributes, actions):
        super().__init__(parent)
        print(element.name)
        print(attributes)
        self.width = 350
        self.height = 350
        self.geometry(f"{self.height}x{self.width}")

        self.attributes = attributes
        self.actions = actions
        self.element = element
        self.main_container = CTkScrollableFrame(self)
        self.main_container.pack(fill = "both")
        self.build_attributes_info()
        self.build_actions()
    
    def build_attributes_info(self):
        for e in self.attributes:
            self.container = CTkFrame(self.main_container)
            self.container.pack(fill = "x")
            self.item = CTkLabel(self.container,text=e[0])
            self.item.pack(side = "left")
            self.value = CTkLabel(self.container,text=e[1])
            self.value.pack(side = "right",padx = 3.5)

    def on_close(self):
        print("to fechando")
        self.destroy()


    def build_actions(self):
        for e in self.actions:
            color = e[0]
            self.btn = CTkButton(self,40,30,fg_color=color,text=e[1],command= lambda e = e: e[2](self.element))
            self.btn.pack()