# from views.main_menu_gui import MainMenu
from coordinator.application_coordinator import ApplicationCoordinator
import customtkinter as ctk
ctk.set_appearance_mode("dark")       # "light" ou "system"
ctk.set_default_color_theme("dark-blue")# ou "green", "dark-blue", etc.

print("Starting app")


if __name__ == "__main__":

    root = ctk.CTk()
    ApplicationCoordinator.main_menu(root)
    root.mainloop()
    # import sys
    # print(sys.path)