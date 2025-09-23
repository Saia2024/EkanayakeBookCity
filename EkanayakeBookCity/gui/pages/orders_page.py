import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import CustomerDAO, PublicationDAO, OrderDAO
from datetime import date
from PIL import Image, ImageTk

class OrdersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_order_items = []
        self.total_amount = 0.0

        try:
            self.search_icon_img = Image.open("assets/search.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.search_icon = ImageTk.PhotoImage(self.search_icon_img)
            self.add_icon_img = Image.open("assets/add.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.add_icon = ImageTk.PhotoImage(self.add_icon_img)
        except FileNotFoundError:
            print("Warning: Order page icons not found in 'assets/' folder.")
            self.search_icon = self.add_icon = tk.PhotoImage()

        self.customer_id_var = tk.StringVar()
        self.order_date_var = tk.StringVar(value=date.today().isoformat())
        self.delivery_status_var = tk.StringVar(value='Pending')
        self.payment_status_var = tk.StringVar(value='Unpaid')
        self.search_pub_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=1)

        # Main Layout
        top_frame = ttk.LabelFrame(self, text="Order Details")
        top_frame.pack(fill='x', padx=10, pady=10)

        middle_frame = ttk.LabelFrame(self, text="Add Publications to Order")
        middle_frame.pack(fill='both', expand=True, padx=10, pady=5)

        bottom_frame = ttk.LabelFrame(self, text="Publications in Current Order")
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Widgets
        customers = CustomerDAO.get_all()
        customer_choices = [f"{c['customer_id']} - {c['name']}" for c in customers] if customers else []
        
        ttk.Label(top_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.customer_combo = ttk.Combobox(top_frame, textvariable=self.customer_id_var, values=customer_choices, width=40, state='readonly')
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top_frame, text="Order Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(top_frame, textvariable=self.order_date_var).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(top_frame, text="Delivery Status:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(top_frame, textvariable=self.delivery_status_var, values=['Pending', 'Delivered'], state='readonly').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(top_frame, text="Payment Status:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        ttk.Combobox(top_frame, textvariable=self.payment_status_var, values=['Unpaid', 'Paid'], state='readonly').grid(row=1, column=3, padx=5, pady=5)

        search_frame = ttk.Frame(middle_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="Search Publication Name:").pack(side='left')
        ttk.Entry(search_frame, textvariable=self.search_pub_var, width=50).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", image=self.search_icon, compound='left', command=self.search_publications).pack(side='left')
        
        self.search_tree = self.create_treeview(middle_frame, ("id", "title", "publisher", "price"))
        self.search_tree.pack(fill='both', expand=True, padx=5, pady=5)

        add_item_frame = ttk.Frame(middle_frame)
        add_item_frame.pack(fill='x', padx=5, pady=10)
        ttk.Label(add_item_frame, text="Quantity:").pack(side='left')
        ttk.Entry(add_item_frame, textvariable=self.quantity_var, width=10).pack(side='left', padx=5)
        ttk.Button(add_item_frame, text="Add to Order", image=self.add_icon, compound='left', command=self.add_item_to_order).pack(side='left')

        self.order_tree = self.create_treeview(bottom_frame, ("id", "title", "quantity", "price", "total"))
        self.order_tree.pack(fill='both', expand=True, padx=5, pady=5)

        action_bar_frame = ttk.Frame(bottom_frame)
        action_bar_frame.pack(fill='x', pady=5)

        action_bar_frame.columnconfigure(0, weight=1) 
        
        self.total_label = ttk.Label(action_bar_frame, text="Total Amount: 0.00", font=("Arial", 12, "bold"))
        self.total_label.grid(row=0, column=0, sticky='e', padx=10)
        
        ttk.Button(action_bar_frame, text="Clear Order", command=self.clear_order).grid(row=0, column=1, padx=5)
        ttk.Button(action_bar_frame, text="Create Order", command=self.create_order).grid(row=0, column=2, padx=10)
        
    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        headings = {"id": "Pub ID", "title": "Title", "publisher": "Publisher", "price": "Price", "quantity": "Qty", "total": "Subtotal"}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=100 if col not in ['title', 'publisher'] else 250)
        return tree

    def search_publications(self):
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        results = PublicationDAO.search_by_name(self.search_pub_var.get())
        if results:
            for pub in results:
                self.search_tree.insert('', 'end', values=(
                    pub['publication_id'], pub['title'], pub['publisher'], f"{pub['price']:.2f}"
                ))

    def add_item_to_order(self):
        selected_item = self.search_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a publication from the search results.")
            return
        
        item_data = self.search_tree.item(selected_item)['values']
        pub_id, title, _, price_str = item_data
        price = float(price_str)
        
        try:
            quantity = self.quantity_var.get()
            if quantity <= 0:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "Quantity must be a positive number.")
            return

        self.current_order_items.append({"pub_id": pub_id, "title": title, "quantity": quantity, "price": price})
        self.total_amount += quantity * price
        
        self.refresh_order_tree()
        self.quantity_var.set(1) 

    def refresh_order_tree(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        for item in self.current_order_items:
            total_price = item['quantity'] * item['price']
            self.order_tree.insert('', 'end', values=(
                item['pub_id'], item['title'], item['quantity'], f"{item['price']:.2f}", f"{total_price:.2f}"
            ))
        
        self.total_label.config(text=f"Total Amount: {self.total_amount:.2f}")

    def create_order(self):
        cust_selection = self.customer_id_var.get()
        if not cust_selection:
            messagebox.showerror("Error", "Please select a customer.")
            return
        if not self.current_order_items:
            messagebox.showerror("Error", "Order must contain at least one publication.")
            return
        
        cust_id = int(cust_selection.split(' - ')[0])
        
        order_id = OrderDAO.create_order(
            customer_id=cust_id,
            order_date=self.order_date_var.get(),
            total_amount=self.total_amount,
            items=self.current_order_items,
            delivery_status=self.delivery_status_var.get(),
            payment_status=self.payment_status_var.get()
        )
        
        if order_id:
            self.controller.show_status_message(f"Order #{order_id} created successfully.")
            self.clear_order()
        else:
            messagebox.showerror("Error", "Failed to create order.")

    def clear_order(self):
        self.current_order_items = []
        self.total_amount = 0.0
        self.refresh_order_tree()
        self.customer_id_var.set('')
        self.order_date_var.set(date.today().isoformat())
        self.delivery_status_var.set('Pending')
        self.payment_status_var.set('Unpaid')
        self.search_pub_var.set('')
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
