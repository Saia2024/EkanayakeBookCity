import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry 
from database.dao import ReportDAO, CustomerDAO
from datetime import datetime, date
import csv
import os

class ReportsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.reports_dir = "Reports"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Main Layout
        filter_frame = ttk.LabelFrame(self, text="Report Filters")
        filter_frame.pack(fill='x', padx=10, pady=10)

        self.results_frame = ttk.LabelFrame(self, text="Report Results")
        self.results_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Filter Widgets
        ttk.Label(filter_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.report_type_var = tk.StringVar()
        self.report_combo = ttk.Combobox(filter_frame, textvariable=self.report_type_var,
                                         values=["Sales Report", "Stock Level Report", "Customer Statement"],
                                         state='readonly', width=30)
        self.report_combo.grid(row=0, column=1, padx=5, pady=5)
        self.report_combo.bind("<<ComboboxSelected>>", self.on_report_type_change)

        self.start_date_label = ttk.Label(filter_frame, text="Start Date:")
        self.start_date_entry = DateEntry(filter_frame, date_pattern='y-mm-dd')

        self.end_date_label = ttk.Label(filter_frame, text="End Date:")
        self.end_date_entry = DateEntry(filter_frame, date_pattern='y-mm-dd')
        
        customers = CustomerDAO.get_all()
        customer_choices = [f"{c['customer_id']} - {c['name']}" for c in customers] if customers else []
        self.customer_label = ttk.Label(filter_frame, text="Customer:")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(filter_frame, textvariable=self.customer_var, values=customer_choices, state='readonly', width=30)
        
        self.generate_btn = ttk.Button(filter_frame, text="Generate Report", command=self.generate_report)
        self.export_btn = ttk.Button(filter_frame, text="Export to CSV", command=self.export_to_csv, state='disabled')

        # Treeview for results
        self.tree = ttk.Treeview(self.results_frame, show='headings')
        self.tree.pack(fill='both', expand=True, side='left')
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(fill='y', side='right')
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.report_combo.set("Sales Report")
        self.on_report_type_change(None)

    def on_report_type_change(self, event):
        self.start_date_label.grid_forget()
        self.start_date_entry.grid_forget()
        self.end_date_label.grid_forget()
        self.end_date_entry.grid_forget()
        self.customer_label.grid_forget()
        self.customer_combo.grid_forget()
        self.generate_btn.grid_forget()
        self.export_btn.grid_forget()

        report_type = self.report_type_var.get()
        
        if report_type in ["Sales Report", "Customer Statement"]:
            self.start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
            self.start_date_entry.grid(row=1, column=1, padx=5, pady=5)
            self.end_date_label.grid(row=1, column=2, padx=5, pady=5, sticky='w')
            self.end_date_entry.grid(row=1, column=3, padx=5, pady=5)
        
        if report_type == "Customer Statement":
            self.customer_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
            self.customer_combo.grid(row=2, column=1, padx=5, pady=5)
            self.generate_btn.grid(row=2, column=2, padx=10, pady=5)
            self.export_btn.grid(row=2, column=3, padx=5, pady=5)
        elif report_type == "Sales Report":
            self.generate_btn.grid(row=1, column=4, padx=10, pady=5)
            self.export_btn.grid(row=1, column=5, padx=5, pady=5)
        elif report_type == "Stock Level Report":
            self.generate_btn.grid(row=0, column=2, padx=10, pady=5)
            self.export_btn.grid(row=0, column=3, padx=5, pady=5)

    def generate_report(self):
        report_type = self.report_type_var.get()
        self.clear_treeview()
        data = []
        columns = []

        try:
            if report_type == "Sales Report":
                columns = ("order_id", "order_date", "customer_name", "publication_title", "quantity", "price_per_unit", "subtotal")
                start_date = self.start_date_entry.get_date()
                end_date = self.end_date_entry.get_date()
                data = ReportDAO.get_sales_report(start_date, end_date)
            
            elif report_type == "Stock Level Report":
                columns = ("publication_id", "title", "category", "quantity")
                data = ReportDAO.get_stock_level_report()

            elif report_type == "Customer Statement":
                columns = ("bill_id", "bill_type", "transaction_id", "due_date", "due_amount", "status")
                cust_selection = self.customer_var.get()
                if not cust_selection:
                    messagebox.showerror("Error", "Please select a customer.")
                    return
                customer_id = int(cust_selection.split(' - ')[0])
                start_date = self.start_date_entry.get_date()
                end_date = self.end_date_entry.get_date()
                data = ReportDAO.get_customer_statement(customer_id, start_date, end_date)

            self.setup_treeview_columns(columns)
            self.populate_treeview(data, columns)
            self.export_btn.config(state='normal' if data else 'disabled')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            self.export_btn.config(state='disabled')

    def setup_treeview_columns(self, columns):
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=120, anchor='w')

    def populate_treeview(self, data, columns):
        if not data:
            self.controller.show_status_message("No data found for the selected criteria.")
            return

        for row in data:
            values = [row.get(col, '') for col in columns]
            self.tree.insert('', 'end', values=values)

    def clear_treeview(self):
        self.tree.delete(*self.tree.get_children())

    def export_to_csv(self):
        if not self.tree.get_children():
            messagebox.showerror("Error", "No data to export.")
            return
        
        report_type_slug = self.report_type_var.get().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y-%m-%d")
        suggested_filename = f"{report_type_slug}_{timestamp}.csv"

        filename = filedialog.asksaveasfilename(
            initialdir=self.reports_dir, 
            initialfile=suggested_filename, 
            title="Save Report As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                columns = self.tree["columns"]
                writer.writerow(columns)
                
                for child in self.tree.get_children():
                    row = self.tree.item(child)['values']
                    writer.writerow(row)
            self.controller.show_status_message(f"Report exported successfully to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")
