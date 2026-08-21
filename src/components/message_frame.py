from customtkinter import CTkFrame , CTkButton , CTkLabel
from popups import PopUpChoiceGUI
from src.components import ScrollItem 

class MessageFrame(CTkFrame, ScrollItem):

    def __init__(self, master,*args, **kwargs):

        super().__init__(master,*args ,**kwargs)
        self.master = master
        # self.pack_propagate(False)
        self.label1 = CTkLabel(self, text=f"", font=("Arial", 10, "bold"),anchor="w")
        self.label1.pack(anchor="w", padx=10, pady=(10, 0),fill = "x")
        self.label1.configure(cursor="hand2")

        self.label2 = CTkLabel(
                    self,
                    text="",
                    font=("Arial", 15),
                    justify="left",
                    anchor = "w",
                    wraplength= 0
        )
        self.label2.pack(anchor="w", padx=10, pady=(0, 10), fill="x")

        

    def set_config(self,data):

        author_name, entry, width, callback ,column, fg_color , side_gap= (data["author_name"], data["entry"], data["width"], 
                                                      data["callback"],data["column"], data["fg_color"] , data["side_gap"])
        self.column = column
        self.side_gap = side_gap

        self.label1.configure(text = f" - {author_name}")
        self.label1.bind("<ButtonRelease-1>", self.spaw_gui)

        self.label2.configure(text = f" - {entry}",wraplength= int(width * 0.9))

        self.configure(width = width ,fg_color = fg_color)
        self.user_name = author_name
        self.callback = callback

    def set_pos(self, pos):
        padx = (5,self.side_gap) if self.column else (self.side_gap, 5)
        self.grid(row = pos , column = 0,padx = padx, pady = 10,sticky="ew")

    ## Not used
    def spaw_gui(self , _event = None):
        warning = PopUpChoiceGUI(self,
                            f"Do you want to remove ({self.user_name}) this connection?",
                            deny_option = True)
        self.wait_window(warning)
        if warning.final_val:
            self.callback(self.author_name)

    

        
