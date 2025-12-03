from root.views.main_menu_gui import MainMenu
import customtkinter as ctk
ctk.set_appearance_mode("dark")       # "light" ou "system"
ctk.set_default_color_theme("dark-blue")# ou "green", "dark-blue", etc.

print("Starting app")


if __name__ == "__main__":
    root = ctk.CTk()
    MainMenu(root)
    root.mainloop()
