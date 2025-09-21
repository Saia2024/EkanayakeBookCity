-- database/db_setup.sql (for reference, the python script will execute these)

CREATE DATABASE IF NOT EXISTS ebc_db;
USE ebc_db;

-- 1. Users Table for Login
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Admin'
);

-- 2. Publications Table
CREATE TABLE IF NOT EXISTS publications (
    publication_id INT AUTO_INCREMENT PRIMARY KEY,
    category ENUM('Newspaper', 'Magazine') NOT NULL,
    title VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    publish_type ENUM('Daily', 'Weekly', 'Monthly') NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- 3. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    contact_no VARCHAR(15) NOT NULL UNIQUE,
    customer_type ENUM('Prepaid', 'Postpaid') NOT NULL
);

-- 4. Stock Table
CREATE TABLE IF NOT EXISTS stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    publication_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (publication_id) REFERENCES publications(publication_id) ON DELETE CASCADE
);

-- 5. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    delivery_status ENUM('Pending', 'Delivered') DEFAULT 'Pending',
    payment_status ENUM('Unpaid', 'Paid') DEFAULT 'Unpaid',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 6. Order Items (to handle multiple publications in one order)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    publication_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

-- 7. Advertisements Table
CREATE TABLE IF NOT EXISTS advertisements (
    ad_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    publication_id INT NOT NULL,
    publication_date DATE NOT NULL,
    content TEXT NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

-- 8. Bills Table
CREATE TABLE IF NOT EXISTS bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    bill_type ENUM('Order', 'Advertisement') NOT NULL,
    related_id INT NOT NULL, -- This will be order_id or ad_id
    due_amount DECIMAL(10, 2) NOT NULL,
    due_date DATE,
    status ENUM('Unpaid', 'Paid') DEFAULT 'Unpaid',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Insert a default admin user for initial login
INSERT INTO users (username, password_hash) VALUES ('admin', 'admin'); -- NOTE: In a real app, hash the password!