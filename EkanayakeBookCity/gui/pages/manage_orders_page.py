import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import OrderDAO

class ManageOrdersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main Layout
        top_frame = ttk.LabelFrame(self, text="All Orders")
        top_frame.pack(fill='both', expand=True, padx=10, pady=(10, 5))

        bottom_frame = ttk.LabelFrame(self, text="Details for Selected Order")
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # List of All Orders
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(fill='x', pady=5, padx=5)
        
        self.mark_delivered_btn = ttk.Button(controls_frame, text="Mark as Delivered", 
                                             command=self.mark_as_delivered, state='disabled')
        self.mark_delivered_btn.pack(side='right')

        # Treeview for all orders
        order_cols = ("id", "customer", "date", "amount", "delivery_status", "payment_status")
        self.order_tree = ttk.Treeview(top_frame, columns=order_cols, show='headings')
        for col in order_cols: self.order_tree.heading(col, text=col.replace('_', ' ').title())
        self.order_tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.order_tree.bind('<<TreeviewSelect>>', self.on_order_select)

        # Bottom Frame
        item_cols = ("title", "quantity", "unit_price", "subtotal")
        self.item_tree = ttk.Treeview(bottom_frame, columns=item_cols, show='headings')
        for col in item_cols: self.item_tree.heading(col, text=col.replace('_', ' ').title())
        self.item_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.load_orders()

    def load_orders(self):
        for item in self.order_tree.get_children(): self.order_tree.delete(item)
        orders = OrderDAO.get_all_with_details()
        if orders:
            for order in orders:
                self.order_tree.insert('', 'end', values=list(order.values()))
        self.on_order_select(None) 

    def on_order_select(self, event):
        for item in self.item_tree.get_children(): self.item_tree.delete(item)

        selected = self.order_tree.focus()
        if not selected:
            self.mark_delivered_btn.config(state='disabled')
            return

        item_data = self.order_tree.item(selected)['values']
        order_id = item_data[0]
        delivery_status = item_data[4]

        self.mark_delivered_btn.config(state='normal' if delivery_status == 'Pending' else 'disabled')

        order_items = OrderDAO.get_order_items(order_id)
        if order_items:
            for item in order_items:
                self.item_tree.insert('', 'end', values=list(item.values()))

    def mark_as_delivered(self):
        selected = self.order_tree.focus()
        if not selected: return

        order_id = self.order_tree.item(selected)['values'][0]
        if messagebox.askyesno("Confirm", f"Mark Order #{order_id} as Delivered?"):
            OrderDAO.update_delivery_status(order_id, 'Delivered')
            self.controller.show_status_message(f"Order #{order_id} marked as Delivered.")
            self.load_orders() 
