import customtkinter as ctk

class PopUPGui(ctk.CTkToplevel):
    def __init__(self, master, labels , maps_of_inputs):
        super().__init__(master)

        self.master = master
        self.labels = labels
        self.maps_of_inputs = maps_of_inputs
        self.entrys = []
        self.inputs_canvas = ctk.CTkScrollableFrame(self)
        self.inputs_canvas.pack(expand = True, fill = "both" , padx = 10, pady =10)
        self.confirm_btn = ctk.CTkButton(self,text= "CONFIRM", command= self.confirm)
        self.confirm_btn.pack(side = "bottom" , pady = 8)
        self.generate_personalized_inputs()

    def generate_personalized_inputs(self):
        for label_text in self.labels:
            label = ctk.CTkLabel(self.inputs_canvas,text = label_text)
            label.pack(pady = 3)
            input_ = ctk.CTkEntry(self.inputs_canvas )
            input_.pack(pady = 5)
            self.entrys.append(input_)

    def confirm(self):
        values = [entry.get() for entry in self.entrys]
        keys = self.maps_of_inputs
        self.registered_values = dict(zip(keys , values))
        self.destroy()
        
