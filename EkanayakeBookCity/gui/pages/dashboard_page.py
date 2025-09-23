import tkinter as tk
from tkinter import ttk, messagebox
from database.dao import PublicationDAO, CustomerDAO, OrderDAO, AdvertisementDAO, SubscriptionDAO

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#ecf0f1')
        self.controller = controller

        # Title
        title_label = ttk.Label(self, text="Dashboard", font=("Arial", 24, "bold"), background='#ecf0f1')
        title_label.pack(pady=20, anchor='w', padx=10)

        
        cards_frame = tk.Frame(self, bg='#ecf0f1')
        cards_frame.pack(fill='x', pady=10, padx=10)
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1) 

        self.create_summary_cards(cards_frame)

        # Recent Orders
        recent_orders_frame = ttk.LabelFrame(self, text="Recent Orders")
        recent_orders_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.create_recent_orders_table(recent_orders_frame)

        # Quick Actions
        quick_actions_frame = ttk.LabelFrame(self, text="Quick Actions")
        quick_actions_frame.pack(fill='x', padx=10, pady=10)

        generate_orders_btn = ttk.Button(quick_actions_frame, text="Generate Daily Subscription Orders",
                                         command=self.generate_subscription_orders)
        generate_orders_btn.pack(pady=10)
        
    def generate_subscription_orders(self):
        self.controller.show_status_message("Checking for due subscriptions...")
        
        due_subscriptions = SubscriptionDAO.get_due_subscriptions()
        
        if not due_subscriptions:
            messagebox.showinfo("Subscriptions", "No subscription orders are due to be generated today.")
            self.controller.clear_status_message()
            return

        generated_count = 0
        failed_count = 0

        for sub in due_subscriptions:
            items_to_order = SubscriptionDAO.get_subscription_items(sub['subscription_id'])
            
            if not items_to_order:
                failed_count += 1
                continue
            order_items_list = [{'pub_id': item['publication_id'], 'quantity': item['quantity'], 'price': item['price']}
                                for item in items_to_order]
            
            # Create the order
            order_id = OrderDAO.create_order_from_subscription(sub['customer_id'], order_items_list)
            
            if order_id:
                SubscriptionDAO.update_last_generated_date(sub['subscription_id'])
                generated_count += 1
            else:
                failed_count += 1
        
        summary_message = f"Subscription Order Generation Complete.\n\n"
        summary_message += f"Successfully Generated: {generated_count}\n"
        summary_message += f"Failed: {failed_count}"
        
        messagebox.showinfo("Generation Complete", summary_message)
        self.controller.show_status_message("Generation complete. See message box for summary.")

    def create_summary_cards(self, parent_frame):
        card_data = [
            ("Total Publications", PublicationDAO.get_count(), "#8e44ad"),
            ("Active Customers", CustomerDAO.get_count(), "#2980b9"),
            ("Pending Orders", OrderDAO.get_pending_count(), "#c0392b"),
            ("Today's Advertisements", AdvertisementDAO.get_todays_count(), "#27ae60")
        ]

        for i, (title, value_func, color) in enumerate(card_data):
            card = tk.Frame(parent_frame, bg=color, relief='raised', borderwidth=2)
            card.grid(row=0, column=i, sticky='ew', padx=10, pady=5)
            
            value = value_func if callable(value_func) else value_func
            value_label = tk.Label(card, text=str(value), bg=color, fg='white', font=("Arial", 30, "bold"))
            value_label.pack(pady=(20, 0))

            title_label = tk.Label(card, text=title, bg=color, fg='white', font=("Arial", 12))
            title_label.pack(pady=(0, 20))

    def create_recent_orders_table(self, parent_frame):
        columns = ("order_id", "customer", "date", "amount", "status")
        tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        
        tree.heading("order_id", text="Order ID")
        tree.heading("customer", text="Customer")
        tree.heading("date", text="Date")
        tree.heading("amount", text="Amount")
        tree.heading("status", text="Status")

        tree.column("order_id", width=80, anchor='center')
        tree.column("amount", width=100, anchor='e')
        tree.column("status", width=100, anchor='center')

        recent_orders = OrderDAO.get_recent_orders(limit=15)
        if recent_orders:
            for order in recent_orders:
                tree.insert('', 'end', values=(
                    order['order_id'],
                    order['customer_name'],
                    order['order_date'],
                    f"{order['total_amount']:.2f}",
                    order['delivery_status']
                ))
        
        tree.pack(fill='both', expand=True, padx=5, pady=5)

