# from views.main_menu_gui import MainMenu
from coordinator.application_coordinator import ApplicationCoordinator
import customtkinter as ctk
ctk.set_appearance_mode("dark")       # "light" ou "system"
ctk.set_default_color_theme("dark-blue")# ou "green", "dark-blue", etc.
from src.infrastructure import ConfigLoader
from src.configuration import setup_logging
import logging

if __name__ == "__main__":

    ConfigLoader.load_config_data()
    setup_logging(app_root = ConfigLoader.get_application_root())
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    root = ctk.CTk()
    ApplicationCoordinator.main_menu(root)
    root.mainloop()
