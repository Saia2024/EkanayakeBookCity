# database/dao.py
from .db_connector import Database
from datetime import date

# Note: All methods are static as they don't rely on the state of a specific instance.
# They are utility functions that interact with the central database connection.

class UserDAO:
    """Data Access Object for user-related operations."""
    
    @staticmethod
    def verify_user(username, password):
        """
        Verifies user credentials against the database.
        
        IMPORTANT: In a real-world application, you MUST hash passwords using a library
        like bcrypt. This implementation compares plain text for simplicity based on the
        initial setup, but it is NOT secure.
        
        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        query = "SELECT password_hash FROM users WHERE username = %s"
        result = Database.execute_query(query, (username,), fetch='one')
        if result and result['password_hash'] == password:
            return True
        return False

class PublicationDAO:
    """Data Access Object for publication-related operations."""

    @staticmethod
    def get_all():
        """Fetches all publications from the database."""
        query = "SELECT * FROM publications ORDER BY publication_id DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def add(category, title, publisher, publish_type, price):
        """Adds a new publication and creates its initial stock record."""
        # Step 1: Add the publication
        query_pub = """
            INSERT INTO publications (category, title, publisher, publish_type, price) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params_pub = (category, title, publisher, publish_type, price)
        publication_id = Database.execute_query(query_pub, params_pub)
        
        # Step 2: Create a corresponding stock entry with quantity 0
        if publication_id:
            query_stock = "INSERT INTO stock (publication_id, quantity) VALUES (%s, 0)"
            Database.execute_query(query_stock, (publication_id,))
        return publication_id

    @staticmethod
    def update(pub_id, category, title, publisher, publish_type, price):
        """Updates an existing publication's details."""
        query = """
            UPDATE publications 
            SET category=%s, title=%s, publisher=%s, publish_type=%s, price=%s 
            WHERE publication_id=%s
        """
        params = (category, title, publisher, publish_type, price, pub_id)
        return Database.execute_query(query, params)

    @staticmethod
    def delete(pub_id):
        """
        Deletes a publication.
        Note: The corresponding stock record is deleted automatically due to 
        'ON DELETE CASCADE' constraint in the database schema.
        """
        query = "DELETE FROM publications WHERE publication_id=%s"
        return Database.execute_query(query, (pub_id,))

    @staticmethod
    def search_by_name(name):
        """Searches for publications by title (for the order page)."""
        query = "SELECT publication_id, title, publisher, price FROM publications WHERE title LIKE %s"
        # The '%' wildcards must be part of the parameter tuple
        params = (f"%{name}%",)
        return Database.execute_query(query, params, fetch='all')

    @staticmethod
    def get_count():
        """Gets the total number of publications (for the dashboard)."""
        query = "SELECT COUNT(*) as total FROM publications"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

class CustomerDAO:
    """Data Access Object for customer-related operations."""

    @staticmethod
    def get_all():
        """Fetches all customers from the database."""
        query = "SELECT * FROM customers ORDER BY customer_id DESC"
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def add(name, address, contact_no, customer_type):
        """Adds a new customer."""
        query = """
            INSERT INTO customers (name, address, contact_no, customer_type) 
            VALUES (%s, %s, %s, %s)
        """
        params = (name, address, contact_no, customer_type)
        return Database.execute_query(query, params)

    @staticmethod
    def update(customer_id, name, address, contact_no, customer_type):
        """Updates an existing customer's details."""
        query = """
            UPDATE customers 
            SET name=%s, address=%s, contact_no=%s, customer_type=%s 
            WHERE customer_id=%s
        """
        params = (name, address, contact_no, customer_type, customer_id)
        return Database.execute_query(query, params)

    @staticmethod
    def delete(customer_id):
        """Deletes a customer."""
        query = "DELETE FROM customers WHERE customer_id=%s"
        return Database.execute_query(query, (customer_id,))

    @staticmethod
    def get_count():
        """Gets the total number of customers (for the dashboard)."""
        query = "SELECT COUNT(*) as total FROM customers"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

class StockDAO:
    """Data Access Object for stock-related operations."""

    @staticmethod
    def get_all_with_details():
        """
        Fetches all stock records, joining with publications to get the title.
        """
        query = """
            SELECT s.publication_id, p.title, s.quantity, s.last_updated
            FROM stock s
            JOIN publications p ON s.publication_id = p.publication_id
            ORDER BY p.title
        """
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def update(publication_id, quantity):
        """Updates the quantity for a specific publication's stock."""
        query = "UPDATE stock SET quantity = %s WHERE publication_id = %s"
        params = (quantity, publication_id)
        return Database.execute_query(query, params)


class OrderDAO:
    """Data Access Object for order-related operations."""
    
    @staticmethod
    def create_order(customer_id, order_date, total_amount, items, delivery_status, payment_status):
        """
        Creates a complete order. This is a multi-step process.
        A proper implementation should use database transactions to ensure all steps succeed or fail together.
        """
        # Step 1: Create the main order record
        order_query = """
            INSERT INTO orders (customer_id, order_date, total_amount, delivery_status, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """
        order_params = (customer_id, order_date, total_amount, delivery_status, payment_status)
        order_id = Database.execute_query(order_query, order_params)
        
        if not order_id:
            print("Failed to create order record.")
            return None

        # Step 2: Insert each item from the order into order_items and update stock
        for item in items:
            # Insert into order_items
            item_query = """
                INSERT INTO order_items (order_id, publication_id, quantity, price_per_unit)
                VALUES (%s, %s, %s, %s)
            """
            item_params = (order_id, item['pub_id'], item['quantity'], item['price'])
            Database.execute_query(item_query, item_params)
            
            # Update stock
            stock_query = "UPDATE stock SET quantity = quantity - %s WHERE publication_id = %s"
            stock_params = (item['quantity'], item['pub_id'])
            Database.execute_query(stock_query, stock_params)

        # Step 3: Generate the bill for this order
        bill_query = """
            INSERT INTO bills (customer_id, bill_type, related_id, due_amount, due_date, status)
            VALUES (%s, 'Order', %s, %s, %s, %s)
        """
        # Due date can be set, e.g., 30 days from now. For now, we'll use order date.
        bill_params = (customer_id, order_id, total_amount, order_date, payment_status)
        Database.execute_query(bill_query, bill_params)
        
        return order_id

    @staticmethod
    def get_recent_orders(limit=10):
        """Gets the most recent orders for the dashboard."""
        query = """
            SELECT o.order_id, c.name as customer_name, o.order_date, o.total_amount, o.delivery_status
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_id DESC
            LIMIT %s
        """
        return Database.execute_query(query, (limit,), fetch='all')

    @staticmethod
    def get_pending_count():
        """Gets the count of pending orders for the dashboard."""
        query = "SELECT COUNT(*) as total FROM orders WHERE delivery_status = 'Pending'"
        result = Database.execute_query(query, fetch='one')
        return result['total'] if result else 0

class AdvertisementDAO:
    """Data Access Object for advertisement-related operations."""

    @staticmethod
    def get_all_with_details():
        """Fetches all ads with customer and publication details."""
        query = """
            SELECT a.ad_id, a.customer_id, c.name as customer_name, a.publication_id, 
                   p.title as publication_title, a.publication_date, a.cost, a.content
            FROM advertisements a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN publications p ON a.publication_id = p.publication_id
            ORDER BY a.ad_id DESC
        """
        return Database.execute_query(query, fetch='all')
    
    @staticmethod
    def add(customer_id, publication_id, publication_date, content, cost):
        """Adds a new advertisement and its corresponding bill."""
        # Step 1: Insert the advertisement
        ad_query = """
            INSERT INTO advertisements (customer_id, publication_id, publication_date, content, cost)
            VALUES (%s, %s, %s, %s, %s)
        """
        ad_params = (customer_id, publication_id, publication_date, content, cost)
        ad_id = Database.execute_query(ad_query, ad_params)

        if not ad_id:
            print("Failed to create advertisement record.")
            return None

        # Step 2: Generate the bill for this advertisement
        bill_query = """
            INSERT INTO bills (customer_id, bill_type, related_id, due_amount, due_date, status)
            VALUES (%s, 'Advertisement', %s, %s, %s, 'Unpaid')
        """
        bill_params = (customer_id, ad_id, cost, publication_date)
        Database.execute_query(bill_query, bill_params)

        return ad_id

    @staticmethod
    def delete(ad_id):
        """Deletes an advertisement."""
        # Note: You might want to decide if deleting an ad should also delete the bill.
        # For now, we leave the bill as a financial record.
        query = "DELETE FROM advertisements WHERE ad_id = %s"
        return Database.execute_query(query, (ad_id,))

    @staticmethod
    def get_todays_count():
        """Gets the count of ads for today (for the dashboard)."""
        query = "SELECT COUNT(*) as total FROM advertisements WHERE publication_date = %s"
        result = Database.execute_query(query, (date.today(),), fetch='one')
        return result['total'] if result else 0

class BillingDAO:
    """Data Access Object for billing-related operations."""

    @staticmethod
    def get_all_with_details():
        """Fetches all bills with customer names."""
        query = """
            SELECT b.bill_id, b.customer_id, c.name as customer_name, b.bill_type, 
                   b.related_id, b.due_amount, b.due_date, b.status
            FROM bills b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.bill_id DESC
        """
        return Database.execute_query(query, fetch='all')

    @staticmethod
    def update_status(bill_id, status):
        """Updates the status of a bill (e.g., to 'Paid')."""
        query = "UPDATE bills SET status = %s WHERE bill_id = %s"
        return Database.execute_query(query, (status, bill_id))