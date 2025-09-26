import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database.dao import CustomerDAO, PublicationDAO, AdvertisementDAO
from config import AD_RATE_PER_WORD
from datetime import date

class AdvertisementsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables
        self.customer_id_var = tk.StringVar()
        self.publication_id_var = tk.StringVar()
        self.publication_date_var = tk.StringVar(value=date.today().isoformat())

        # Widgets
        entry_frame = ttk.LabelFrame(self, text="Advertisement Details")
        entry_frame.pack(fill="x", padx=10, pady=10)

        customers = CustomerDAO.get_all()
        customer_choices = [f"{c['customer_id']} - {c['name']}" for c in customers] if customers else []
        publications = PublicationDAO.get_all()
        pub_choices = [f"{p['publication_id']} - {p['title']}" for p in publications] if publications else []
        
        ttk.Label(entry_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Combobox(entry_frame, textvariable=self.customer_id_var, values=customer_choices, width=30).grid(row=0, column=1)
        
        ttk.Label(entry_frame, text="Publication:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Combobox(entry_frame, textvariable=self.publication_id_var, values=pub_choices, width=30).grid(row=0, column=3)
        
        ttk.Label(entry_frame, text="Publication Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(entry_frame, textvariable=self.publication_date_var).grid(row=1, column=1)

        ttk.Label(entry_frame, text="Content:").grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.content_text = scrolledtext.ScrolledText(entry_frame, width=80, height=10, wrap=tk.WORD)
        self.content_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Add Ad", command=self.add_ad).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Ad", command=self.delete_ad).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        list_frame = ttk.LabelFrame(self, text="List of Advertisements")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "customer", "publication", "date", "cost")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading("id", text="Ad ID")
        self.tree.heading("customer", text="Customer")
        self.tree.heading("publication", text="Publication")
        self.tree.heading("date", text="Date")
        self.tree.heading("cost", text="Cost")
        self.tree.pack(fill="both", expand=True)
        
        self.load_ads()

    def load_ads(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        ads = AdvertisementDAO.get_all_with_details()
        if ads:
            for ad in ads:
                self.tree.insert('', 'end', values=(
                    ad['ad_id'], ad['customer_name'], ad['publication_title'], 
                    ad['publication_date'], f"{ad['cost']:.2f}"
                ))

    def add_ad(self):
        cust_selection = self.customer_id_var.get()
        pub_selection = self.publication_id_var.get()
        content = self.content_text.get("1.0", "end-1c").strip()

        if not all([cust_selection, pub_selection, content]):
            messagebox.showerror("Error", "Customer, Publication, and Content are required.")
            return
        
        customer_id = int(cust_selection.split(' - ')[0])
        publication_id = int(pub_selection.split(' - ')[0])
        
        # Calculate cost
        word_count = len(content.split())
        cost = word_count * AD_RATE_PER_WORD
        
        if messagebox.askyesno("Confirm Cost", f"The calculated cost is {cost:.2f} ({word_count} words). Proceed?"):
            AdvertisementDAO.add(customer_id, publication_id, self.publication_date_var.get(), content, cost)
            messagebox.showinfo("Success", "Advertisement added successfully.")
            self.load_ads()
            self.clear_fields()

    def delete_ad(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an advertisement to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ad?"):
            ad_id = self.tree.item(selected_item)['values'][0]
            AdvertisementDAO.delete(ad_id)
            messagebox.showinfo("Success", "Advertisement deleted.")
            self.load_ads()

    def clear_fields(self):
        self.customer_id_var.set('')
        self.publication_id_var.set('')
        self.publication_date_var.set(date.today().isoformat())
        self.content_text.delete("1.0", tk.END)
