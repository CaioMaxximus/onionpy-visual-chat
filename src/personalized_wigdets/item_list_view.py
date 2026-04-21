import customtkinter as ctk


#  tenho que decidir o design dessa classe por que eu preciso lidar
#  com retorno com mais de um campo

class ItemListView(ctk.CTkScrollableFrame):

    """
    A class represeting a wigdet of a list of elements. It stores all the elements
    with two callback funtions associated for each one of them. 

    This the callback functions allow personalizes behaviour when clicking and 
    exibiting an item.
    
    Attributes
    ----------
    master :  ctk
        the root tkinter object for the all aplication
    on_item_click : <function>
        callback function that is called once one element clicked
    on_exibit_item : <function>
        callback function that is called once one element rendered
    items : list
        items used to polute the wigdet
    buttons : {CTkButton}
        dictionary containing the buttons wigdets
    
    Methods
    ------
    render_items
        Instanciate the wigdets on the canvas
    update_items
        Allows lazy creation of the items on the list, and a update without the 
        need to destroy all the wigdet
    """

    def __init__(self, master, on_item_click, on_exibit_item , items=None):
        super().__init__(master)
        self.master = master
        self.on_item_click = on_item_click
        self.on_exibit_item = on_exibit_item
        self.items = items or []
        self.buttons = {}

        self.render_items()

    def render_items(self):

        for btn in self.buttons.values():
            btn.destroy()
        self.buttons.clear()

        for i, item in enumerate(self.items):
            btn = ctk.CTkButton(
                self,
                width=20,
                height=15,
                corner_radius=8,
                command=lambda e=item: self.on_item_click(e),
                text= self.on_exibit_item(item)
            )
            btn.pack(fill="x")
            self.buttons[i] = btn

    def update_items(self, items):
        self.items = items
        self.render_items()