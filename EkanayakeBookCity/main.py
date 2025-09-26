import tkinter as tk
from gui.login_page import LoginPage
from gui.main_app import EBCManagementSystem
from database.db_connector import Database

def main():
    root = tk.Tk()
    root.withdraw()

    login_window = LoginPage(root)
    root.wait_window(login_window)

    if login_window.login_successful:
        root.destroy()
        
        app = EBCManagementSystem()
        app.protocol("WM_DELETE_WINDOW", lambda: on_app_closing(app))
        app.mainloop()
    else:
        print("Login failed or cancelled. Exiting.")
        Database.close_connection()

def on_app_closing(app):
    if tk.messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        Database.close_connection()
        app.destroy()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        Database.close_connection()
