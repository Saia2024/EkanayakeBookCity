# gui/pages/stock_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import StockDAO, PublicationDAO

class StockPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Variables ---
        self.publication_id_var = tk.StringVar()
        self.quantity_var = tk.IntVar()

        # --- Widgets ---
        entry_frame = ttk.LabelFrame(self, text="Manage Stock")
        entry_frame.pack(fill="x", padx=10, pady=10)

        publications = PublicationDAO.get_all()
        pub_choices = [f"{p['publication_id']} - {p['title']}" for p in publications] if publications else []

        ttk.Label(entry_frame, text="Publication:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.pub_combo = ttk.Combobox(entry_frame, textvariable=self.publication_id_var, values=pub_choices, width=40, state='readonly')
        self.pub_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="New Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.quantity_var).grid(row=0, column=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Update Stock", command=self.update_stock).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        list_frame = ttk.LabelFrame(self, text="Current Stock Levels")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "title", "quantity", "last_updated")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading("id", text="Pub ID")
        self.tree.heading("title", text="Publication Title")
        self.tree.heading("quantity", text="Current Quantity")
        self.tree.heading("last_updated", text="Last Updated")
        
        self.tree.column("id", width=80, anchor='center')
        self.tree.column("quantity", width=120, anchor='center')
        self.tree.column("last_updated", width=180, anchor='center')
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        self.load_stock()

    def load_stock(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        stock_list = StockDAO.get_all_with_details()
        if stock_list:
            for item in stock_list:
                self.tree.insert('', 'end', values=(
                    item['publication_id'], item['title'], item['quantity'], item['last_updated']
                ))

    def update_stock(self):
        pub_selection = self.publication_id_var.get()
        if not pub_selection:
            messagebox.showerror("Error", "Please select a publication.")
            return
        
        try:
            quantity = self.quantity_var.get()
            if quantity < 0:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "Please enter a valid non-negative integer for quantity.")
            return
            
        publication_id = int(pub_selection.split(' - ')[0])
        StockDAO.update(publication_id, quantity)
        messagebox.showinfo("Success", "Stock updated successfully.")
        self.load_stock()
        self.clear_fields()

    def clear_fields(self):
        self.publication_id_var.set('')
        self.quantity_var.set(0)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.focus())

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        item_data = self.tree.item(selected_item)['values']
        pub_id, title, quantity, _ = item_data
        
        self.publication_id_var.set(f"{pub_id} - {title}")
        self.quantity_var.set(quantity)