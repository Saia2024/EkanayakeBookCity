import tkinter as tk
from tkinter import ttk, font
from .pages import (dashboard_page, publications_page, customers_page, 
                    orders_page, advertisements_page, stock_page, billing_page, reports_page, subscriptions_page)

class EBCManagementSystem(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Ekanayake Book City Management System")
        self.geometry("1280x720") 
        self.minsize(1100, 650)   

        # Styling
        self.style = ttk.Style(self)
        self.style.theme_use("clam") 
        self.configure(background='#F0F0F0')

        # Main Layout Frames
        sidebar = tk.Frame(self, bg='#2c3e50', width=200)
        sidebar.pack(side="left", fill="y")

        main_content_frame = tk.Frame(self)
        main_content_frame.pack(side="right", fill="both", expand=True)

        # Status Bar Implementation
        self.status_bar = tk.Label(main_content_frame, text="Welcome to EBC Management System", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10,
                                   font=("Arial", 10))
        self.status_bar.pack(side="bottom", fill="x")
        
        # content
        self.content_area = tk.Frame(main_content_frame, bg='#ecf0f1')
        self.content_area.pack(fill="both", expand=True)

        # Dictionar to page classes
        self.pages = {}
        
        # Sidebar Content
        logo_label = tk.Label(sidebar, text="EBC", bg='#2c3e50', fg='white', 
                              font=("Arial", 30, "bold"))
        logo_label.pack(pady=20, padx=10)

        # button text to page class
        nav_buttons = {
            "Dashboard": dashboard_page.DashboardPage,
            "Publications": publications_page.PublicationsPage,
            "Customers": customers_page.CustomersPage,
            "Orders": orders_page.OrdersPage,
            "Subscriptions": subscriptions_page.SubscriptionsPage,
            "Advertisements": advertisements_page.AdvertisementsPage,
            "Stock": stock_page.StockPage,
            "Billing": billing_page.BillingPage,
            "Reports":reports_page.ReportsPage
        }

        # navigation buttons
        for name, page_class in nav_buttons.items():
            button = tk.Button(sidebar, text=name, bg='#34495e', fg='white', 
                               font=("Arial", 12), relief='flat', anchor='w',
                               activebackground='#4e6a85', activeforeground='white',
                               command=lambda pc=page_class: self.show_page(pc))
            button.pack(fill='x', padx=10, pady=5, ipady=5)

        # Initial Page Display
        self.show_page(dashboard_page.DashboardPage)

    def show_page(self, page_class):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        page = page_class(self.content_area, self)
        page.pack(fill="both", expand=True, padx=10, pady=10)

    def show_status_message(self, message, duration_ms=4000):
        self.status_bar.config(text=message, fg='black')
        self.status_bar.after(duration_ms, self.clear_status_message)

    def show_status_error(self, message, duration_ms=5000):
        self.status_bar.config(text=message, fg='red')
        self.status_bar.after(duration_ms, self.clear_status_message)

    def clear_status_message(self):
        self.status_bar.config(text="")
