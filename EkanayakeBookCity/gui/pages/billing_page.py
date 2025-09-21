# gui/pages/billing_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import BillingDAO

class BillingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title_label = ttk.Label(self, text="Billing Records", font=("Arial", 18, "bold"))
        title_label.pack(pady=10, anchor='w', padx=10)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.mark_paid_btn = ttk.Button(button_frame, text="Mark as Paid", command=self.mark_as_paid, state='disabled')
        self.mark_paid_btn.pack(side='right')

        columns = ("bill_id", "customer", "type", "related_id", "amount", "due_date", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading("bill_id", text="Bill ID")
        self.tree.heading("customer", text="Customer Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("related_id", text="Order/Ad ID")
        self.tree.heading("amount", text="Due Amount")
        self.tree.heading("due_date", text="Due Date")
        self.tree.heading("status", text="Status")
        
        self.tree.column("bill_id", width=60, anchor='center')
        self.tree.column("amount", anchor='e')
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        self.load_bills()

    def load_bills(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        bills = BillingDAO.get_all_with_details()
        if bills:
            for bill in bills:
                self.tree.insert('', 'end', values=(
                    bill['bill_id'], bill['customer_name'], bill['bill_type'],
                    bill['related_id'], f"{bill['due_amount']:.2f}",
                    bill['due_date'], bill['status']
                ))
        self.on_item_select(None) # Disable button after loading

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            self.mark_paid_btn.config(state='disabled')
            return
        
        status = self.tree.item(selected_item)['values'][6]
        if status == 'Unpaid':
            self.mark_paid_btn.config(state='normal')
        else:
            self.mark_paid_btn.config(state='disabled')

    def mark_as_paid(self):
        selected_item = self.tree.focus()
        if not selected_item: return
        
        bill_id = self.tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Confirm Payment", f"Mark Bill #{bill_id} as Paid?"):
            BillingDAO.update_status(bill_id, 'Paid')
            messagebox.showinfo("Success", "Bill status updated.")
            self.load_bills()