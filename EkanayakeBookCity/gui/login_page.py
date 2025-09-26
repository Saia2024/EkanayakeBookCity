import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import UserDAO

class LoginPage(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.login_successful = False

        self.title("EBC Login")
        self.geometry("400x300")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grab_set()

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self.create_widgets()
        self.center_window()

        self.bind('<Return>', self.attempt_login)

    def center_window(self):
        """Centers the Toplevel window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(main_frame, text="Ekanayake Book City PaperTrack", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Username
        ttk.Label(main_frame, text="Username:").pack(fill='x')
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, font=("Arial", 12))
        username_entry.pack(fill='x', pady=(0, 10))
        username_entry.focus_set() 

        # Password
        ttk.Label(main_frame, text="Password:").pack(fill='x')
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", font=("Arial", 12))
        self.password_entry.pack(fill='x', pady=(0, 10))

        # Login Button
        login_button = ttk.Button(main_frame, text="Login", command=self.attempt_login)
        login_button.pack(pady=10, fill='x')

        # Status Label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack()

    def attempt_login(self, event=None):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            self.status_label.config(text="Username and password are required.")
            return

        if UserDAO.verify_user(username, password):
            self.login_successful = True
            self.destroy() 
        else:
            self.status_label.config(text="Invalid username or password.")
            self.password_entry.delete(0, 'end')

    def on_closing(self):
        self.login_successful = False
        self.destroy()
