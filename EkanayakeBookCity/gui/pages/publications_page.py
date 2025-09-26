import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import PublicationDAO
from PIL import Image, ImageTk

class PublicationsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        try:
            self.add_icon_img = Image.open("assets/add.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.add_icon = ImageTk.PhotoImage(self.add_icon_img)
            
            self.update_icon_img = Image.open("assets/update.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.update_icon = ImageTk.PhotoImage(self.update_icon_img)
            
            self.delete_icon_img = Image.open("assets/delete.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.delete_icon = ImageTk.PhotoImage(self.delete_icon_img)
            
            self.clear_icon_img = Image.open("assets/clear.png").resize((16, 16), Image.Resampling.LANCZOS)
            self.clear_icon = ImageTk.PhotoImage(self.clear_icon_img)
        
        except FileNotFoundError as e:
            print(f"Error loading icons: {e}. Make sure the 'assets' folder is correct.")
            self.add_icon = self.update_icon = self.delete_icon = self.clear_icon = tk.PhotoImage()

        self.validate_price_cmd = self.register(self.validate_price)

        self.category_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.publisher_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.price_var = tk.StringVar()

        # Widgets
        entry_frame = ttk.LabelFrame(self, text="Publication Details")
        entry_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(entry_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(entry_frame, textvariable=self.category_var, values=['Newspaper', 'Magazine'], state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Title:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.title_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text="Publisher:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.publisher_var, width=30).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(entry_frame, textvariable=self.type_var, values=['Daily', 'Weekly', 'Monthly'], state='readonly').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Price:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        
        price_entry = ttk.Entry(entry_frame, textvariable=self.price_var, validate='key', validatecommand=(self.validate_price_cmd, '%P'))
        price_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        ttk.Button(button_frame, text="Add", image=self.add_icon, compound="left", command=self.add_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update", image=self.update_icon, compound="left", command=self.update_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", image=self.delete_icon, compound="left", command=self.delete_publication).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", image=self.clear_icon, compound="left", command=self.clear_fields).pack(side='left', padx=5)

        # Data Display
        list_frame = ttk.LabelFrame(self, text="List of Publications")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "category", "title", "publisher", "type", "price")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree_sort_reverse = {} 
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(), 
                              command=lambda _col=col: self.sort_treeview_column(_col))
            self.tree_sort_reverse[col] = False 

        self.tree.column("id", width=50, anchor='center')
        self.tree.column("price", width=80, anchor='e') 
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        self.load_publications()

    def validate_price(self, value_if_allowed):
        if value_if_allowed == "" or value_if_allowed == ".":
            return True
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def sort_treeview_column(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        def sort_key(item):
            try:
                return float(item[0])
            except ValueError:
                return item[0].lower()

        data.sort(key=sort_key, reverse=self.tree_sort_reverse[col])

        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

        self.tree_sort_reverse[col] = not self.tree_sort_reverse[col]

    # CRUD
    def load_publications(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        publications = PublicationDAO.get_all()
        if publications:
            for pub in publications:
                self.tree.insert('', 'end', values=(
                    pub['publication_id'], pub['category'], pub['title'], 
                    pub['publisher'], pub['publish_type'], f"{pub['price']:.2f}"
                ))

    def add_publication(self):
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
        
        self.controller.show_status_message("Publication added successfully.")
        self.load_publications()
        self.clear_fields()

    def update_publication(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a publication to update.")
            return
        
        pub_id = self.tree.item(selected_item)['values'][0]
        try:
            price = float(self.price_var.get())
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number.")
            return

        PublicationDAO.update(pub_id, self.category_var.get(), self.title_var.get(), self.publisher_var.get(), 
                              self.type_var.get(), price)
        
        self.controller.show_status_message("Publication updated successfully.") 
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
            self.controller.show_status_message("Publication deleted successfully.") # Use status bar
            self.load_publications()
            self.clear_fields()

    def clear_fields(self):
        self.category_var.set('')
        self.title_var.set('')
        self.publisher_var.set('')
        self.type_var.set('')
        self.price_var.set('')
        if self.tree.selection():
            self.tree.selection_remove(self.tree.focus())

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        item_data = self.tree.item(selected_item)['values']
        self.category_var.set(item_data[1])
        self.title_var.set(item_data[2])
        self.publisher_var.set(item_data[3])
        self.type_var.set(item_data[4])
        self.price_var.set(item_data[5])
