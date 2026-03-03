-- ==============================
-- DATABASE
-- ==============================

CREATE DATABASE IF NOT EXISTS supermarket;
USE supermarket;

-- ==============================
-- INVENTORY TABLE
-- ==============================

CREATE TABLE IF NOT EXISTS inventory (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    quantity INT NOT NULL CHECK (quantity >= 0)
);

-- ==============================
-- CUSTOMERS TABLE
-- ==============================

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mobile VARCHAR(10) NOT NULL
);

-- ==============================
-- BILLS TABLE
-- ==============================

CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    bill_date DATETIME NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    sgst DECIMAL(10,2) NOT NULL,
    cgst DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE RESTRICT
);

-- ==============================
-- BILL ITEMS TABLE
-- ==============================

CREATE TABLE IF NOT EXISTS bill_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES inventory(id)
        ON DELETE RESTRICT
);

-- ==============================
-- SAMPLE INVENTORY DATA
-- ==============================

INSERT INTO inventory (id, name, price, quantity) VALUES
(1, 'Rice (1kg)', 60.00, 50),
(2, 'Milk (1L)', 45.00, 30),
(3, 'Bread', 40.00, 25),
(4, 'Eggs (12 pcs)', 75.00, 20),
(5, 'Sugar (1kg)', 50.00, 40);
