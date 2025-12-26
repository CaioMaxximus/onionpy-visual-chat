from customtkinter import CTkFrame , CTkButton , CTkLabel
from popups import PopUpChoiceGUI

class MessageFrame(CTkFrame):

    def __init__(self, master,user , content ,callback,*args, **kwargs):
        super().__init__(master,*args ,**kwargs)
        
        label1 = CTkLabel(self, text=f"UserName: {user}", font=("Arial", 8, "bold"))
        label1.pack(anchor="w", padx=10, pady=(10, 0))
        label1.configure(cursor="hand2")
        label1.bind("<ButtonRelease-1>", self.spaw_gui)
       
        label2 = CTkLabel(
            self,
            text=content,
            font=("Arial", 12),
            justify="left",
            wraplength=400  
        )
        label2.pack(anchor="w", padx=10, pady=(0, 10), fill="x")
        self.user_name = user
        self.callback = callback

    def spaw_gui(self , _event = None):
        warning = PopUpChoiceGUI(self,
                            f"Do you want to remove ({self.user_name}) this connection?",
                            deny_option = True)
        self.wait_window(warning)
        if warning.final_val:
            self.callback(self.user)

    

        
