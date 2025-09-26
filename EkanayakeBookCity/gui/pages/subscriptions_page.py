import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database.dao import CustomerDAO, PublicationDAO, SubscriptionDAO
from datetime import date

class SubscriptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_subscription_items = []

        # Variables
        self.customer_var = tk.StringVar()
        self.start_date_var = tk.StringVar(value=date.today().isoformat())
        self.end_date_var = tk.StringVar()
        self.frequency_var = tk.StringVar(value='Daily')
        self.search_pub_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=1)

        # Main Layout
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x')

        details_frame = ttk.LabelFrame(top_frame, text="Subscription Details")
        details_frame.pack(side='left', fill='x', expand=True, padx=10, pady=10)

        add_item_frame = ttk.LabelFrame(top_frame, text="Add Publications")
        add_item_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        bottom_frame = ttk.LabelFrame(self, text="Current Subscriptions")
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Widgets
        customers = CustomerDAO.get_all()
        customer_choices = [f"{c['customer_id']} - {c['name']}" for c in customers] if customers else []
        
        ttk.Label(details_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(details_frame, textvariable=self.customer_var, values=customer_choices, width=30, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(details_frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        DateEntry(details_frame, textvariable=self.start_date_var, date_pattern='y-mm-dd').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(details_frame, text="End Date:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        DateEntry(details_frame, textvariable=self.end_date_var, date_pattern='y-mm-dd').grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(details_frame, text="Frequency:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(details_frame, textvariable=self.frequency_var, values=['Daily', 'Weekly', 'Monthly'], state='readonly').grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(details_frame, text="Create Subscription", command=self.create_subscription).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(details_frame, text="Clear Form", command=self.clear_form).grid(row=5, column=0, columnspan=2)

        search_frame = ttk.Frame(add_item_frame)
        search_frame.pack(fill='x', pady=5)
        ttk.Entry(search_frame, textvariable=self.search_pub_var, width=30).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_publications).pack(side='left')

        self.search_tree = ttk.Treeview(add_item_frame, columns=("id", "title"), show='headings', height=4)
        self.search_tree.heading("id", text="ID")
        self.search_tree.heading("title", text="Title")
        self.search_tree.pack(fill='x', pady=5)
        
        add_controls = ttk.Frame(add_item_frame)
        add_controls.pack(fill='x')
        ttk.Label(add_controls, text="Qty:").pack(side='left')
        ttk.Entry(add_controls, textvariable=self.quantity_var, width=5).pack(side='left', padx=5)
        ttk.Button(add_controls, text="Add to Subscription", command=self.add_item_to_subscription).pack(side='left')

        self.items_tree = ttk.Treeview(add_item_frame, columns=("id", "title", "qty"), show='headings', height=4)
        self.items_tree.heading("id", text="ID")
        self.items_tree.heading("title", text="Title")
        self.items_tree.heading("qty", text="Quantity")
        self.items_tree.pack(fill='x', pady=5)

        list_controls = ttk.Frame(bottom_frame)
        list_controls.pack(fill='x', pady=5)
        ttk.Button(list_controls, text="Cancel Selected", command=self.cancel_subscription).pack(side='right')

        columns = ("id", "customer", "start_date", "end_date", "frequency", "status")
        self.sub_list_tree = ttk.Treeview(bottom_frame, columns=columns, show='headings')
        for col in columns: self.sub_list_tree.heading(col, text=col.replace('_', ' ').title())
        self.sub_list_tree.pack(fill='both', expand=True)
        
        self.load_subscriptions()

    # GUI
    def search_publications(self):
        for item in self.search_tree.get_children(): self.search_tree.delete(item)
        results = PublicationDAO.search_by_name(self.search_pub_var.get())
        if results:
            for pub in results: self.search_tree.insert('', 'end', values=(pub['publication_id'], pub['title']))

    def add_item_to_subscription(self):
        selected = self.search_tree.focus()
        if not selected: return
        
        item_data = self.search_tree.item(selected)['values']
        pub_id, title = item_data
        quantity = self.quantity_var.get()
        
        self.current_subscription_items.append({'pub_id': pub_id, 'title': title, 'quantity': quantity})
        self.refresh_items_tree()
        self.quantity_var.set(1)

    def refresh_items_tree(self):
        for item in self.items_tree.get_children(): self.items_tree.delete(item)
        for item in self.current_subscription_items:
            self.items_tree.insert('', 'end', values=(item['pub_id'], item['title'], item['quantity']))
            
    def load_subscriptions(self):
        for item in self.sub_list_tree.get_children(): self.sub_list_tree.delete(item)
        subscriptions = SubscriptionDAO.get_all_with_details()
        if subscriptions:
            for sub in subscriptions: self.sub_list_tree.insert('', 'end', values=list(sub.values()))

    def clear_form(self):
        self.customer_var.set('')
        self.start_date_var.set(date.today().isoformat())
        self.end_date_var.set('')
        self.frequency_var.set('Daily')
        self.current_subscription_items = []
        self.refresh_items_tree()

    def create_subscription(self):
        if not all([self.customer_var.get(), self.start_date_var.get(), self.end_date_var.get()]) or not self.current_subscription_items:
            messagebox.showerror("Error", "Customer, dates, and at least one item are required.")
            return

        customer_id = int(self.customer_var.get().split(' - ')[0])
        SubscriptionDAO.create_subscription(customer_id, self.start_date_var.get(), self.end_date_var.get(),
                                            self.frequency_var.get(), self.current_subscription_items)
        
        self.controller.show_status_message("Subscription created successfully.")
        self.load_subscriptions()
        self.clear_form()

    def cancel_subscription(self):
        selected = self.sub_list_tree.focus()
        if not selected: return
        
        sub_id = self.sub_list_tree.item(selected)['values'][0]
        if messagebox.askyesno("Confirm", "Cancel this subscription? This cannot be undone."):
            SubscriptionDAO.update_status(sub_id, 'Cancelled')
            self.controller.show_status_message("Subscription cancelled.")
            self.load_subscriptions()
            
