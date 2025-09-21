# main.py
import tkinter as tk
from gui.login_page import LoginPage
from gui.main_app import EBCManagementSystem
from database.db_connector import Database

def main():
    """
    Main function to run the application with a login screen.
    """
    # Create a temporary hidden root window. This is necessary for the
    # Toplevel login window to function correctly.
    root = tk.Tk()
    root.withdraw()

    # Create the login window and wait for it to be closed.
    login_window = LoginPage(root)
    root.wait_window(login_window)

    # After the login window is closed, check if the login was successful.
    if login_window.login_successful:
        # If login was successful, destroy the temporary root window and
        # create the main application window.
        root.destroy()
        
        # Launch the main application
        app = EBCManagementSystem()
        app.protocol("WM_DELETE_WINDOW", lambda: on_app_closing(app))
        app.mainloop()
    else:
        # If login failed or the window was closed, the program will just exit.
        # Ensure the database connection is closed.
        print("Login failed or cancelled. Exiting.")
        Database.close_connection()

def on_app_closing(app):
    """
    Custom close function for the main app to ensure DB connection is closed.
    """
    if tk.messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        Database.close_connection()
        app.destroy()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Ensure the connection is closed even if an error occurs during startup
        Database.close_connection()