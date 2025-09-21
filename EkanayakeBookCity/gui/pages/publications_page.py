# gui/pages/publications_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import PublicationDAO # Import the specific DAO

class PublicationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Variables ---
        self.category_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.publisher_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.price_var = tk.StringVar()

        # --- Widgets ---
        # Top Frame for data entry
        entry_frame = ttk.LabelFrame(self, text="Publication Details")
        entry_frame.pack(fill="x", padx=10, pady=10)
        
        # Fields
        ttk.Label(entry_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.category_combo = ttk.Combobox(entry_frame, textvariable=self.category_var, values=['Newspaper', 'Magazine'], state='readonly')
        self.category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Title:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.title_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text="Publisher:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.publisher_var, width=30).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.type_combo = ttk.Combobox(entry_frame, textvariable=self.type_var, values=['Daily', 'Weekly', 'Monthly'], state='readonly')
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Price:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.price_var).grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        ttk.Button(button_frame, text="Add Publication", command=self.add_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Publication", command=self.update_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Publication", command=self.delete_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        # Bottom Frame for Treeview list
        list_frame = ttk.LabelFrame(self, text="List of Publications")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "category", "title", "publisher", "type", "price")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading("id", text="ID")
        self.tree.heading("category", text="Category")
        self.tree.heading("title", text="Title")
        self.tree.heading("publisher", text="Publisher")
        self.tree.heading("type", text="Type")
        self.tree.heading("price", text="Price")
        
        self.tree.column("id", width=50)
        # ... set other column widths

        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Load initial data
        self.load_publications()

    def load_publications(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Fetch and insert new data
        publications = PublicationDAO.get_all()
        if publications:
            for pub in publications:
                self.tree.insert('', 'end', values=(pub['publication_id'], pub['category'], 
                                   pub['title'], pub['publisher'], pub['publish_type'], pub['price']))

    def add_publication(self):
        # Validation
        if not all([self.category_var.get(), self.title_var.get(), self.type_var.get(), self.price_var.get()]):
            messagebox.showerror("Error", "All fields except Publisher are required.")
            return
        try:
            price = float(self.price_var.get())
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number.")
            return

        PublicationDAO.add(self.category_var.get(), self.title_var.get(), self.publisher_var.get(),
                           self.type_var.get(), price)
        messagebox.showinfo("Success", "Publication added successfully.")
        self.load_publications()
        self.clear_fields()

    def update_publication(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a publication to update.")
            return
        
        pub_id = self.tree.item(selected_item)['values'][0]
        category = self.category_var.get()
        title = self.title_var.get()
        publisher = self.publisher_var.get()
        publish_type = self.type_var.get()
        price_str = self.price_var.get()

        if not all ([category, title, publish_type, price_str]):
            messagebox.showerror("Error", "All fields except Publisher are required.")
            return
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number.")
            return

        PublicationDAO.update(pub_id, category, title, publisher, publish_type, price)
        
        messagebox.showinfo("Success", "Publication updated successfully.")
        self.load_publications()
        self.clear_fields()

    def delete_publication(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a publication to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this publication?"):
            pub_id = self.tree.item(selected_item)['values'][0]
            PublicationDAO.delete(pub_id)
            messagebox.showinfo("Success", "Publication deleted successfully.")
            self.load_publications()
            self.clear_fields()

    def clear_fields(self):
        self.category_var.set('')
        self.title_var.set('')
        self.publisher_var.set('')
        self.type_var.set('')
        self.price_var.set('')
        self.tree.selection_remove(self.tree.focus())

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        item_data = self.tree.item(selected_item)['values']
        self.clear_fields() # Clear first
        self.category_var.set(item_data[1])
        self.title_var.set(item_data[2])
        self.publisher_var.set(item_data[3])
        self.type_var.set(item_data[4])
        self.price_var.set(item_data[5])