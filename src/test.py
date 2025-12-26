import tkinter as tk
from queue import Empty, Queue
from threading import Event, Thread
import sys

class _GUICallData:

    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.reply = None
        self.reply_event = Event()

class App(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_text)
        self.entry.pack()
        self.call_queue = Queue()
        self.bind("<<gui_call>>", self.gui_call_handler)
        self.thread = Thread(target=self.threadFn, daemon=True)

    def get_entry_text(self):
        return self.entry_text.get()

    def set_entry_text(self, text):
        self.entry_text.set(text)

    def make_gui_call(self, fn, *args, **kwargs):
        data = _GUICallData(fn, args, kwargs)
        self.call_queue.put(data)
        self.event_generate("<<gui_call>>", when="tail")
        data.reply_event.wait()
        return data.reply

    def gui_call_handler(self, event):
        try:
            while True:
                data = self.call_queue.get_nowait()
                data.reply = data.fn(*data.args, *data.kwargs)
                data.reply_event.set()
        except Empty:
            pass

    def threadFn(self):
        self.make_gui_call(self.set_entry_text, "hello world")
        print(
            "self.get_entry_text() returns:",
            self.make_gui_call(self.get_entry_text)
        )

root = tk.Tk()
app = App(master=root)
app.thread.start()
app.mainloop()