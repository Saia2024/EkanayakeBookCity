# gui/pages/customers_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import CustomerDAO

class CustomersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Variables ---
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.type_var = tk.StringVar()

        # --- Widgets ---
        entry_frame = ttk.LabelFrame(self, text="Customer Details")
        entry_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(entry_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Address:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.address_var, width=40).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text="Contact No:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.contact_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Type:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.type_combo = ttk.Combobox(entry_frame, textvariable=self.type_var, values=['Prepaid', 'Postpaid'], state='readonly')
        self.type_combo.grid(row=1, column=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Customer", command=self.update_customer).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Customer", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        list_frame = ttk.LabelFrame(self, text="List of Customers")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "name", "address", "contact_no", "type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("address", text="Address")
        self.tree.heading("contact_no", text="Contact No.")
        self.tree.heading("type", text="Type")
        
        self.tree.column("id", width=50, anchor='center')
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        self.load_customers()

    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        customers = CustomerDAO.get_all()
        if customers:
            for cust in customers:
                self.tree.insert('', 'end', values=(
                    cust['customer_id'], cust['name'], cust['address'], 
                    cust['contact_no'], cust['customer_type']))

    def add_customer(self):
        if not all([self.name_var.get(), self.contact_var.get(), self.type_var.get()]):
            messagebox.showerror("Error", "Name, Contact No, and Type are required.")
            return
        
        CustomerDAO.add(self.name_var.get(), self.address_var.get(), 
                        self.contact_var.get(), self.type_var.get())
        messagebox.showinfo("Success", "Customer added successfully.")
        self.load_customers()
        self.clear_fields()

    def update_customer(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a customer to update.")
            return
        
        cust_id = self.tree.item(selected_item)['values'][0]
        CustomerDAO.update(cust_id, self.name_var.get(), self.address_var.get(),
                           self.contact_var.get(), self.type_var.get())
        messagebox.showinfo("Success", "Customer updated successfully.")
        self.load_customers()
        self.clear_fields()

    def delete_customer(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a customer to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure? This may affect existing orders."):
            cust_id = self.tree.item(selected_item)['values'][0]
            CustomerDAO.delete(cust_id)
            messagebox.showinfo("Success", "Customer deleted successfully.")
            self.load_customers()
            self.clear_fields()

    def clear_fields(self):
        self.name_var.set('')
        self.address_var.set('')
        self.contact_var.set('')
        self.type_var.set('')
        if self.tree.selection():
            self.tree.selection_remove(self.tree.focus())

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        item_data = self.tree.item(selected_item)['values']
        self.name_var.set(item_data[1])
        self.address_var.set(item_data[2])
        self.contact_var.set(item_data[3])
        self.type_var.set(item_data[4])