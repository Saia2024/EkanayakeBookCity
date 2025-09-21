# gui/main_app.py
import tkinter as tk
from tkinter import ttk, font
from .pages import (dashboard_page, publications_page, customers_page, 
                    orders_page, advertisements_page, stock_page, billing_page)

class EBCManagementSystem(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Ekanayake Book City Management System")
        self.geometry("1200x700")
        
        # --- Styling ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam") # A modern theme
        self.configure(background='#F0F0F0')

        # --- Main Layout ---
        # Sidebar
        sidebar = tk.Frame(self, bg='#2c3e50', width=200)
        sidebar.pack(side="left", fill="y")
        
        # Content Area
        self.content_area = tk.Frame(self, bg='#ecf0f1')
        self.content_area.pack(side="right", fill="both", expand=True)

        self.pages = {}
        
        # --- Sidebar Content ---
        logo_label = tk.Label(sidebar, text="EBC", bg='#2c3e50', fg='white', font=("Arial", 30, "bold"))
        logo_label.pack(pady=20)

        # Navigation Buttons
        nav_buttons = {
            "Dashboard": dashboard_page.DashboardPage,
            "Publications": publications_page.PublicationsPage,
            "Customers": customers_page.CustomersPage,
            "Orders": orders_page.OrdersPage,
            "Advertisements": advertisements_page.AdvertisementsPage,
            "Stock": stock_page.StockPage,
            "Billing": billing_page.BillingPage,
        }

        for name, page_class in nav_buttons.items():
            button = tk.Button(sidebar, text=name, bg='#34495e', fg='white', 
                               font=("Arial", 12), relief='flat', anchor='w',
                               command=lambda pc=page_class: self.show_page(pc))
            button.pack(fill='x', padx=10, pady=5)
            self.pages[page_class] = None # Initialize as not created

        # --- Initial Page ---
        self.show_page(dashboard_page.DashboardPage)

    def show_page(self, page_class):
        # Destroy current page frame
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Create and show the new page
        if self.pages[page_class] is None or True: # Re-create page each time to refresh data
            page = page_class(self.content_area, self)
            self.pages[page_class] = page
            page.pack(fill="both", expand=True, padx=10, pady=10)
        else:
             self.pages[page_class].pack(fill="both", expand=True, padx=10, pady=10)