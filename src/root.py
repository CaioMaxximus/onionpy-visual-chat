# from views.main_menu_gui import MainMenu
from coordinator.application_coordinator import ApplicationCoordinator
import customtkinter as ctk
ctk.set_appearance_mode("dark")       # "light" ou "system"
ctk.set_default_color_theme("dark-blue")# ou "green", "dark-blue", etc.
from src.infrastructure import ConfigLoader


if __name__ == "__main__":

    ConfigLoader.load_config_data()
    root = ctk.CTk()
    ApplicationCoordinator.main_menu(root)
    root.mainloop()
