from .db_connector import Database
from datetime import date

class UserDAO:
    
    @staticmethod
    def verify_user(username, password):
        query = "SELECT password_hash FROM users WHERE username = %s"
        result = Database.execute_query(query, (username,), fetch='one')
        if result and result['password_hash'] == password:
            return True
        return False

class PublicationDAO:

    @staticmethod
    def get_all():
        query = "SELECT * FROM publications ORDER BY publication_id DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def add(category, title, publisher, publish_type, price):
        query_pub = "INSERT INTO publications (category, title, publisher, publish_type, price) VALUES (%s, %s, %s, %s, %s)"
        params_pub = (category, title, publisher, publish_type, price)
        publication_id = Database.execute_query(query_pub, params_pub)
        
        if publication_id:
            query_stock = "INSERT INTO stock (publication_id, quantity) VALUES (%s, 0)"
            Database.execute_query(query_stock, (publication_id,))
        return publication_id

    @staticmethod
    def update(pub_id, category, title, publisher, publish_type, price):
        query = "UPDATE publications SET category=%s, title=%s, publisher=%s, publish_type=%s, price=%s WHERE publication_id=%s"
        params = (category, title, publisher, publish_type, price, pub_id)
        return Database.execute_query(query, params)

    @staticmethod
    def delete(pub_id):
        query = "DELETE FROM publications WHERE publication_id=%s"
        return Database.execute_query(query, (pub_id,))

    @staticmethod
    def search_by_name(name):
        query = "SELECT publication_id, title, publisher, price FROM publications WHERE title LIKE %s"
        params = (f"%{name}%",)
        return Database.execute_query(query, params, fetch='all')

    @staticmethod
    def get_count():
        query = "SELECT COUNT(*) as total FROM publications"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

class CustomerDAO:

    @staticmethod
    def get_all():
        query = "SELECT * FROM customers ORDER BY customer_id DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def add(name, address, contact_no, customer_type):
        query = "INSERT INTO customers (name, address, contact_no, customer_type) VALUES (%s, %s, %s, %s)"
        params = (name, address, contact_no, customer_type)
        return Database.execute_query(query, params)

    @staticmethod
    def update(customer_id, name, address, contact_no, customer_type):
        query = "UPDATE customers SET name=%s, address=%s, contact_no=%s, customer_type=%s WHERE customer_id=%s"
        params = (name, address, contact_no, customer_type, customer_id)
        return Database.execute_query(query, params)

    @staticmethod
    def delete(customer_id):
        query = "DELETE FROM customers WHERE customer_id=%s"
        return Database.execute_query(query, (customer_id,))

    @staticmethod
    def get_count():
        query = "SELECT COUNT(*) as total FROM customers"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

class StockDAO:

    @staticmethod
    def get_all_with_details():
        query = "SELECT s.publication_id, p.title, s.quantity, s.last_updated FROM stock s JOIN publications p ON s.publication_id = p.publication_id ORDER BY p.title"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def add_quantity(publication_id, quantity_to_add):
        """Adds a specified quantity to the existing stock (relative update)."""
        query = "UPDATE stock SET quantity = quantity + %s WHERE publication_id = %s"
        params = (quantity_to_add, publication_id)
        return Database.execute_query(query, params)

    @staticmethod
    def update(publication_id, new_quantity):
        """Sets the quantity for a publication's stock (absolute update for corrections)."""
        query = "UPDATE stock SET quantity = %s WHERE publication_id = %s"
        params = (new_quantity, publication_id)
        return Database.execute_query(query, params)

    @staticmethod
    def get_stock_quantity(publication_id):
        query = "SELECT quantity FROM stock WHERE publication_id = %s"
        result = Database.execute_query(query, (publication_id,), fetch='one')
        return result['quantity'] if result else 0

class OrderDAO:
    
    @staticmethod
    def create_order(customer_id, order_date, total_amount, items, delivery_status, payment_status):
        order_query = "INSERT INTO orders (customer_id, order_date, total_amount, delivery_status, payment_status) VALUES (%s, %s, %s, %s, %s)"
        order_params = (customer_id, order_date, total_amount, delivery_status, payment_status)
        order_id = Database.execute_query(order_query, order_params)
        
        if not order_id: return None

        for item in items:
            item_query = "INSERT INTO order_items (order_id, publication_id, quantity, price_per_unit) VALUES (%s, %s, %s, %s)"
            item_params = (order_id, item['pub_id'], item['quantity'], item['price'])
            Database.execute_query(item_query, item_params)
            
            stock_query = "UPDATE stock SET quantity = quantity - %s WHERE publication_id = %s"
            stock_params = (item['quantity'], item['pub_id'])
            Database.execute_query(stock_query, stock_params)

        bill_query = "INSERT INTO bills (customer_id, bill_type, related_id, due_amount, due_date, status) VALUES (%s, 'Order', %s, %s, %s, %s)"
        bill_params = (customer_id, order_id, total_amount, order_date, payment_status)
        Database.execute_query(bill_query, bill_params)
        
        return order_id

    @staticmethod
    def create_order_from_subscription(customer_id, items):
        """Simplified version of create_order for automated subscription generation."""
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        return OrderDAO.create_order(customer_id, date.today(), total_amount, items, 'Pending', 'Unpaid')

    @staticmethod
    def get_recent_orders(limit=10):
        query = "SELECT o.order_id, c.name as customer_name, o.order_date, o.total_amount, o.delivery_status FROM orders o JOIN customers c ON o.customer_id = c.customer_id ORDER BY o.order_id DESC LIMIT %s"
        return Database.execute_query(query, (limit,), fetch='all')

    @staticmethod
    def get_pending_count():
        query = "SELECT COUNT(*) as total FROM orders WHERE delivery_status = 'Pending'"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

    @staticmethod
    def update_delivery_status(order_id, new_status):
        query = "UPDATE orders SET delivery_status = %s WHERE order_id = %s"
        return Database.execute_query(query, (new_status, order_id))

    @staticmethod
    def get_all_with_details():
        query = """
            SELECT o.order_id, c.name AS customer_name, o.order_date, o.total_amount, o.delivery_status, o.payment_status
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_id DESC;
        """
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def get_order_items(order_id):
        query = """
            SELECT p.title, oi.quantity, oi.price_per_unit, (oi.quantity * oi.price_per_unit) as subtotal
            FROM order_items oi
            JOIN publications p ON oi.publication_id = p.publication_id
            WHERE oi.order_id = %s;
        """
        return Database.execute_query(query, (order_id,), fetch='all')

class SubscriptionDAO:

    @staticmethod
    def create_subscription(customer_id, start_date, end_date, frequency, items):
        sub_query = "INSERT INTO subscriptions (customer_id, start_date, end_date, frequency) VALUES (%s, %s, %s, %s)"
        sub_params = (customer_id, start_date, end_date, frequency)
        subscription_id = Database.execute_query(sub_query, sub_params)

        if not subscription_id: return None

        for item in items:
            item_query = "INSERT INTO subscription_items (subscription_id, publication_id, quantity) VALUES (%s, %s, %s)"
            item_params = (subscription_id, item['pub_id'], item['quantity'])
            Database.execute_query(item_query, item_params)
        return subscription_id

    @staticmethod
    def get_all_with_details():
        query = "SELECT s.subscription_id, c.name AS customer_name, s.start_date, s.end_date, s.frequency, s.status FROM subscriptions s JOIN customers c ON s.customer_id = c.customer_id ORDER BY s.start_date DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def get_subscription_items(subscription_id):
        query = "SELECT si.publication_id, p.title, si.quantity, p.price FROM subscription_items si JOIN publications p ON si.publication_id = p.publication_id WHERE si.subscription_id = %s"
        return Database.execute_query(query, (subscription_id,), fetch='all')
        
    @staticmethod
    def update_status(subscription_id, status):
        query = "UPDATE subscriptions SET status = %s WHERE subscription_id = %s"
        return Database.execute_query(query, (status, subscription_id))

    @staticmethod
    def get_due_subscriptions():
        query = "SELECT * FROM subscriptions WHERE status = 'Active' AND CURDATE() BETWEEN start_date AND end_date AND (last_generated_date IS NULL OR last_generated_date < CURDATE()) AND (frequency = 'Daily' OR (frequency = 'Weekly' AND DAYOFWEEK(CURDATE()) = DAYOFWEEK(start_date)) OR (frequency = 'Monthly' AND DAY(CURDATE()) = DAY(start_date)))"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def update_last_generated_date(subscription_id):
        query = "UPDATE subscriptions SET last_generated_date = CURDATE() WHERE subscription_id = %s"
        return Database.execute_query(query, (subscription_id,))

class AdvertisementDAO:

    @staticmethod
    def get_all_with_details():
        query = "SELECT a.ad_id, a.customer_id, c.name as customer_name, a.publication_id, p.title as publication_title, a.publication_date, a.cost, a.content FROM advertisements a JOIN customers c ON a.customer_id = c.customer_id JOIN publications p ON a.publication_id = p.publication_id ORDER BY a.ad_id DESC"
        return Database.execute_query(query, fetch='all')
    
    @staticmethod
    def add(customer_id, publication_id, publication_date, content, cost):
        ad_query = "INSERT INTO advertisements (customer_id, publication_id, publication_date, content, cost) VALUES (%s, %s, %s, %s, %s)"
        ad_params = (customer_id, publication_id, publication_date, content, cost)
        ad_id = Database.execute_query(ad_query, ad_params)

        if not ad_id: return None

        bill_query = "INSERT INTO bills (customer_id, bill_type, related_id, due_amount, due_date, status) VALUES (%s, 'Advertisement', %s, %s, %s, 'Unpaid')"
        bill_params = (customer_id, ad_id, cost, publication_date)
        Database.execute_query(bill_query, bill_params)
        return ad_id

    @staticmethod
    def delete(ad_id):
        query = "DELETE FROM advertisements WHERE ad_id = %s"
        return Database.execute_query(query, (ad_id,))

    @staticmethod
    def get_todays_count():
        query = "SELECT COUNT(*) as total FROM advertisements WHERE publication_date = %s"
        result = Database.execute_query(query, (date.today(),), fetch='one')
        return result['total'] if result else 0

class BillingDAO:

    @staticmethod
    def get_all_with_details():
        query = "SELECT b.bill_id, b.customer_id, c.name as customer_name, b.bill_type, b.related_id, b.due_amount, b.due_date, b.status FROM bills b JOIN customers c ON b.customer_id = c.customer_id ORDER BY b.bill_id DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def update_status(bill_id, status):
        query = "UPDATE bills SET status = %s WHERE bill_id = %s"
        return Database.execute_query(query, (status, bill_id))

    @staticmethod
    def get_order_invoice_details(order_id):
        details = {}
        main_query = """
            SELECT c.name, c.address, c.contact_no, o.order_date, o.total_amount, o.payment_status
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s;
        """
        details['main_info'] = Database.execute_query(main_query, (order_id,), fetch='one')

        items_query = """
            SELECT p.title, oi.quantity, oi.price_per_unit, (oi.quantity * oi.price_per_unit) as subtotal
            FROM order_items oi
            JOIN publications p ON oi.publication_id = p.publication_id
            WHERE oi.order_id = %s;
        """
        details['items'] = Database.execute_query(items_query, (order_id,), fetch='all')

        return details

    @staticmethod
    def get_ad_invoice_details(ad_id):
        query = """
            SELECT 
                c.name, c.address, c.contact_no,
                a.publication_date, a.content, a.cost,
                p.title AS publication_title,
                b.status AS payment_status
            FROM advertisements a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN publications p ON a.publication_id = p.publication_id
            JOIN bills b ON (b.related_id = a.ad_id AND b.bill_type = 'Advertisement')
            WHERE a.ad_id = %s;
        """
        return Database.execute_query(query, (ad_id,), fetch='one')

class ReportDAO:

    @staticmethod
    def get_sales_report(start_date, end_date):
        query = "SELECT o.order_id, o.order_date, c.name AS customer_name, p.title AS publication_title, oi.quantity, oi.price_per_unit, (oi.quantity * oi.price_per_unit) AS subtotal FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN publications p ON oi.publication_id = p.publication_id WHERE o.order_date BETWEEN %s AND %s ORDER BY o.order_date, o.order_id;"
        return Database.execute_query(query, (start_date, end_date), fetch='all')

    @staticmethod
    def get_stock_level_report():
        query = "SELECT p.publication_id, p.title, p.category, s.quantity FROM stock s JOIN publications p ON s.publication_id = p.publication_id ORDER BY p.title;"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def get_customer_statement(customer_id, start_date, end_date):
        query = "SELECT bill_id, bill_type, related_id AS transaction_id, due_date, due_amount, status FROM bills WHERE customer_id = %s AND due_date BETWEEN %s AND %s ORDER BY due_date;"
        return Database.execute_query(query, (customer_id, start_date, end_date), fetch='all')
