#  Supermarket Management System (MySQL)

A console-based Supermarket Management System built using Python and MySQL.  
This project demonstrates backend development concepts including database design, transaction management, CRUD operations, reporting, and PDF invoice generation.

---

##  Features

### Billing System
- Create new customer bills
- GST calculation (SGST + CGST)
- Decimal-safe financial calculation
- Transaction-safe bill generation (commit / rollback)
- Invoice format: `INV-YYYY-0001`
- PDF invoice generation
- Auto-open generated PDF
- View historical bills
### Inventory Management (Full CRUD)
- Add new product
- Update price & stock
- Update product name
- Safe delete (restricted if product used in bills)
- Low stock alert (≤ 5 items)

### Reporting
- Daily Sales Report
- Total bills per day
- Daily revenue summary (SQL GROUP BY)

### Security
- Database password stored using environment variable
- Foreign key constraints enforced
- Safe transaction handling

---

##  Database Schema

Tables:

- `inventory`
- `customers`
- `bills`
- `bill_items`

Relationships:

- One customer → Many bills
- One bill → Many bill_items
- One product → Many bill_items

Database schema is available in `schema.sql`.

To create database:

```bash
mysql -u root -p < schema.sql
 Technologies Used

Python 3

MySQL

mysql-connector-python

ReportLab

Regular Expressions

Git & GitHub

 Setup Instructions
1️ Install Dependencies
pip install mysql-connector-python reportlab
2️ Set Database Password (Linux / Mac)
export DB_PASSWORD=your_mysql_password
3️ Run Application
python3 supermarket_mysql.py
 Key Concepts Implemented

ACID Transactions

Relational Database Design

Foreign Key Integrity

Decimal Financial Calculations

Input Validation (Indian mobile format)

CRUD Operations

SQL Reporting

PDF Invoice Generation

 Author

Sharath B M
Data Analyst
