import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.dao import BillingDAO
import os
from datetime import datetime

class BillingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        title_label = ttk.Label(self, text="Billing Records", font=("Arial", 18, "bold"))
        title_label.pack(pady=10, anchor='w', padx=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)

        self.generate_invoice_btn = ttk.Button(button_frame, text="Generate Invoice", 
                                               command=self.generate_invoice, state='disabled')
        self.generate_invoice_btn.pack(side='right', padx=(5, 0))

        self.mark_paid_btn = ttk.Button(button_frame, text="Mark as Paid", 
                                        command=self.mark_as_paid, state='disabled')
        self.mark_paid_btn.pack(side='right')

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

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
        self.on_item_select(None) 

    def on_item_select(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            self.mark_paid_btn.config(state='disabled')
            self.generate_invoice_btn.config(state='disabled')
            return
        
        self.generate_invoice_btn.config(state='normal')
        
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
            self.controller.show_status_message("Bill status updated.")
            self.load_bills()

    def generate_invoice(self):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        item_data = self.tree.item(selected_item)['values']
        bill_id, _, bill_type, related_id, _, _, _ = item_data
        
        invoice_text = ""
        if bill_type == 'Order':
            details = BillingDAO.get_order_invoice_details(related_id)
            if details:
                invoice_text = self._format_order_invoice_text(bill_id, related_id, details)
        elif bill_type == 'Advertisement':
            details = BillingDAO.get_ad_invoice_details(related_id)
            if details:
                invoice_text = self._format_ad_invoice_text(bill_id, related_id, details)
        
        if not invoice_text:
            messagebox.showerror("Error", "Could not retrieve invoice details.")
            return
            
        self.save_invoice_file(bill_id, invoice_text)

    def _format_order_invoice_text(self, bill_id, order_id, details):
        main_info = details['main_info']
        items = details['items']
        
        status_stamp = f"*** {main_info['payment_status'].upper()} ***".center(70)
                
        text = f"""
======================================================================
                         Ekanayake Book City
                            ORDER INVOICE
======================================================================

{status_stamp}

Invoice #: {bill_id}
Order ID:  {order_id}
Date:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bill To:
----------------------------------------------------------------------
Name:    {main_info['name']}
Address: {main_info['address']}
Contact: {main_info['contact_no']}

----------------------------------------------------------------------
Order Details (Date: {main_info['order_date']})
----------------------------------------------------------------------
{'Item':<40} {'Qty':>5} {'Unit Price':>12} {'Subtotal':>12}
----------------------------------------------------------------------
"""
        for item in items:
            text += f"{item['title']:<40} {item['quantity']:>5} {item['price_per_unit']:>12.2f} {item['subtotal']:>12.2f}\n"
        
        text += f"""
----------------------------------------------------------------------
                                              TOTAL: {main_info['total_amount']:>12.2f}
======================================================================
                 Thank you for your business!
======================================================================
"""
        return text

    def _format_ad_invoice_text(self, bill_id, ad_id, details):
        """Formats the data for an advertisement invoice into a string."""

        status_stamp = f"*** {details['payment_status'].upper()} ***".center(70)

        text = f"""
======================================================================
                         Ekanayake Book City
                        ADVERTISEMENT INVOICE
======================================================================

{status_stamp}

Invoice #: {bill_id}
Ad ID:     {ad_id}
Date:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Bill To:
----------------------------------------------------------------------
Name:    {details['name']}
Address: {details['address']}
Contact: {details['contact_no']}

----------------------------------------------------------------------
Advertisement Details
----------------------------------------------------------------------
Publication:      {details['publication_title']}
Publication Date: {details['publication_date']}

Content:
"{details['content']}"

----------------------------------------------------------------------
                                                COST: {details['cost']:>12.2f}
======================================================================
                 Thank you for your business!
======================================================================
"""
        return text

    def save_invoice_file(self, bill_id, content):
        """Opens a save dialog and writes the invoice content to a file."""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialdir=os.path.expanduser("~"), 
                initialfile=f"EBC-Invoice-{bill_id}.txt"
            )
            if not filepath:
                return 

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.controller.show_status_message(f"Invoice saved to {filepath}")
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to save invoice file.\nError: {e}")
