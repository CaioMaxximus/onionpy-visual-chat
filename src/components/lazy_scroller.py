from abc import ABC, abstractmethod
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")



class ScrollItem(ABC):

    """
        This is the interface that a element needs to implement to be rendered inside the LazyScroller

        Methods
        ------
        set_config : changes the wigdet object information and appearence based in a brand new data
        set_pos : set the row position where the element needs to be settled 
    """
    @abstractmethod
    def set_config(self, data):
        pass

    @abstractmethod
    def set_pos(self, pos):
        pass


## Just for local test
class WidgetElement(ctk.CTkFrame, ScrollItem):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.pos = 0

        self.configure(fg_color="#2b2b2b")
        self.label = ctk.CTkLabel(
                            self, text="", font=("Arial", 18), text_color="#2ecc71"
                        )

        
    def set_config(self, data):
        self.data = data
        
        self.label.configure(text=str(self.data))

        self.label.pack(pady=15, padx=20)

    def set_pos(self, pos):
        self.pos = pos
        self.grid(row=pos, column=1, sticky="ew", padx=10, pady=5)

    def __str__(self):
        return f"Sou o {self.data} na pos : {self.pos}"


class LazyScroller(ctk.CTkScrollableFrame):

    """
        This class represents a personalized scrollable frame build over 
        a standard CTkScrollableFrame using a circular list. Different from the default class,
        it allows a huge number of elements inside itself without the memory and
        processing usage explosion

        Attributes
        master : ctk
            the parent tkinter class
        max_element : Int
            The maximum number of elements that can be stored inside the view, 
            the first elements will be removed automatic if the limits exceeds.
        window_size: Int
            The maximum number of tkinter visual elements that can be stored inside
            the view, reflecting in the performance.
        wigdet_mode: ScrollItem
            The class that represents the element that will be rendered inside the view


    """

    def __init__(
        self, master, max_elements, window_size, wigdet_model, *args, **kwargs
    ):
        super().__init__(master, *args, **kwargs)

        if max_elements <= window_size:
            raise ValueError("max_elements must be bigger than window_size! ")

        self.grid_columnconfigure(0, weight=1)


        self.max_elements = max_elements
        self.window_size = window_size
        self.wigdet_model = wigdet_model
        self.children_ele = []
        self.wigdets_ele = []

        # This represents the head and tail of the total elements list
        self.h_window_p = 0
        self.t_window_p = -1

        # This represents the head and tail from the visual window related with the elements list
        self.h_children_p = 0
        self.t_children_p = -1

        # This represents the head and tail for the dedicated list of visual elements
        self.h_internal_window = 0
        self.t_internal_window = -1
        self.last_w_pos = 0


    def add_children(self, child: ScrollItem):

        move_to_bottom = False
        if self.t_window_p == self.t_children_p and self.is_at_bottom():
            move_to_bottom = True

        lay_pos = (self.t_children_p + 1) % self.max_elements
        if len(self.children_ele) < self.max_elements:
            self.children_ele.append(child)
            self.t_children_p = (self.t_children_p + 1) % self.max_elements
            if len(self.children_ele) <= self.window_size:
                self.render_new_elem(child)
        else:
            self.children_ele[lay_pos] = child
            self.move_circular_list()
            if lay_pos == self.h_window_p:
                self.move_window_down()
        
        if move_to_bottom:

            self.move_window_down()
            self._jump_to_end()

    def render_new_elem(self, child):

        new_e = self.wigdet_model(self)
        new_e.set_config(child)
        self.wigdets_ele.append(new_e)
        new_e.set_pos(len(self.wigdets_ele) - 1)
        self.t_internal_window += 1
        self.t_window_p += 1

    def _jump_to_end(self):

        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        self._parent_canvas.update_idletasks()
        self._parent_canvas.yview_moveto(1.0)
        

    def move_window_down(self):

        if not self.is_at_bottom():
            self._parent_canvas.yview_scroll(1, "units")
            return

        if self.t_window_p == self.t_children_p :
            return
        self.h_window_p = (self.h_window_p + 1) % self.max_elements
        self.t_window_p = (self.t_window_p + 1) % self.max_elements

        self.wigdets_ele[self.h_internal_window].set_config(
            self.children_ele[self.t_window_p]
        )
        self.h_internal_window = (
            self.h_internal_window + 1
        ) % self.window_size
        self.t_internal_window = (
            self.t_internal_window + 1
        ) % self.window_size

        i = self.h_internal_window
        counter = 0
        while i != self.t_internal_window:
            self.wigdets_ele[i].set_pos(counter)
            i = (i + 1) % len(self.wigdets_ele)
            counter += 1
        self.wigdets_ele[i].set_pos(counter)

    def move_window_up(self):

        if  not self.is_at_top():
            self._parent_canvas.yview_scroll(-1, "units")
            return

        if self.h_window_p == self.h_children_p:
            return
        self.h_window_p = (self.h_window_p - 1) % self.max_elements
        self.t_window_p = (self.t_window_p - 1) % self.max_elements

        self.wigdets_ele[self.t_internal_window].set_config(
            self.children_ele[self.h_window_p]
        )
        self.h_internal_window = (
            self.h_internal_window - 1
        ) % self.window_size
        self.t_internal_window = (
            self.t_internal_window - 1
        ) % self.window_size

        i = self.h_internal_window
        counter = 0
        while i != self.t_internal_window:
            self.wigdets_ele[i].set_pos(counter)
            i = (i + 1) % len(self.wigdets_ele)
            counter += 1
        self.wigdets_ele[i].set_pos(counter)

    def move_circular_list(self):

        self.h_children_p = (self.h_children_p + 1) % self.max_elements
        self.t_children_p = (self.t_children_p + 1) % self.max_elements

    def _on_mousewheel(self, event):
        
        if event.num == 5 or event.delta < 0:
            self.move_window_down()
        elif event.num == 4 or event.delta > 0:
            self.move_window_up()

    def is_at_bottom(self, tolerancia=0.01) -> bool:
        _, bottom = self._parent_canvas.yview()
        return bottom >= (1.0 - tolerancia)

    def is_at_top(self, tolerancia=0.01) -> bool:

        top, _ = self._parent_canvas.yview()
        return top <= tolerancia


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Elemento Preenchendo Tudo")
        self.geometry("600x400")
        self.N = 0

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll = LazyScroller(self, 1000, 50, WidgetElement)
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.after(2000, self.scroll_up)


        self.bind("<Button-4>", self.scroll._on_mousewheel)
        self.bind("<Button-5>", self.scroll._on_mousewheel)


    def scroll_up(self):
            self.scroll.add_children(self.N)
            self.N += 1
            self.after(1200, self.scroll_up)


if __name__ == "__main__":
    app = App()
    app.mainloop()