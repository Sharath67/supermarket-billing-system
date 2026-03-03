import mysql.connector
import datetime
import re
import os
import subprocess
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes

# ==========================
# DATABASE CONNECTION
# ==========================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="supermarket"
)

cursor = conn.cursor()

# ==========================
# VALIDATION FUNCTIONS
# ==========================

def validate_name(name):
    return bool(re.fullmatch(r"[A-Za-z ]{3,50}", name.strip()))

def validate_mobile(mobile):
    return bool(re.fullmatch(r"[6-9]\d{9}", mobile))

def validate_positive_int(value):
    return value.isdigit() and int(value) > 0

def get_yes_no(prompt):
    while True:
        choice = input(prompt).strip()
        if choice in ["Y", "y", "N", "n"]:
            return choice.lower()
        print("Invalid input. Enter Y or N only.")

# ==========================
# DISPLAY INVENTORY
# ==========================

def display_items():
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    print("\nAvailable Items:")
    print("ID   Name               Price   Stock")
    print("-"*60)

    for row in rows:
        if row[3] <= 5:
            print(f"{row[0]:<5}{row[1]:<20}{row[2]:<10}{row[3]}  ⚠ LOW STOCK")
        else:
            print(f"{row[0]:<5}{row[1]:<20}{row[2]:<10}{row[3]}")

# ==========================
# PDF GENERATION
# ==========================

def generate_pdf_bill(bill_id):

    cursor.execute("""
        SELECT bills.id, customers.name, customers.mobile,
               bills.bill_date, bills.subtotal,
               bills.sgst, bills.cgst, bills.total
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        WHERE bills.id = %s
    """, (bill_id,))
    bill_data = cursor.fetchone()

    if not bill_data:
        print("Bill not found.")
        return

    bill_year = bill_data[3].year
    invoice_no = f"INV-{bill_year}-{bill_id:04d}"

    cursor.execute("""
        SELECT inventory.name, bill_items.quantity,
               bill_items.price, bill_items.total
        FROM bill_items
        JOIN inventory ON bill_items.product_id = inventory.id
        WHERE bill_items.bill_id = %s
    """, (bill_id,))
    items = cursor.fetchall()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_folder = os.path.join(BASE_DIR, "bills_pdf")
    os.makedirs(pdf_folder, exist_ok=True)

    file_path = os.path.join(pdf_folder, f"Bill_{bill_id}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>SUPER MARKET BILL</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Invoice No: {invoice_no}", styles["Normal"]))
    elements.append(Paragraph(f"Customer: {bill_data[1]}", styles["Normal"]))
    elements.append(Paragraph(f"Mobile: {bill_data[2]}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {bill_data[3]}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    data = [["Item", "Qty", "Price", "Total"]]

    for item in items:
        data.append([item[0], str(item[1]), str(item[2]), str(item[3])])

    data.append(["", "", "Subtotal", str(bill_data[4])])
    data.append(["", "", "SGST", str(bill_data[5])])
    data.append(["", "", "CGST", str(bill_data[6])])
    data.append(["", "", "Final Total", str(bill_data[7])])

    table = Table(data, colWidths=[200, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(table)
    doc.build(elements)

    subprocess.run(["xdg-open", file_path])

# ==========================
# NEW CUSTOMER BILL
# ==========================

def new_customer():

    while True:
        name = input("Enter Customer Name: ")
        if validate_name(name):
            break
        print("Invalid name.")

    while True:
        mobile = input("Enter Mobile (10 digits): ")
        if validate_mobile(mobile):
            break
        print("Invalid mobile.")

    cart = []
    subtotal = Decimal("0")

    while True:
        display_items()

        item_id = input("Enter Item ID: ")
        if not validate_positive_int(item_id):
            print("Invalid ID")
            continue

        item_id = int(item_id)

        cursor.execute("SELECT price, quantity FROM inventory WHERE id=%s", (item_id,))
        result = cursor.fetchone()

        if not result:
            print("Item not found.")
            continue

        price, stock = result
        price = Decimal(price)

        qty_input = input("Enter Quantity: ")
        if not validate_positive_int(qty_input):
            print("Invalid quantity.")
            continue

        qty = int(qty_input)

        if qty > stock:
            print("Insufficient stock.")
            continue

        total = price * qty
        subtotal += total
        cart.append((item_id, qty, price, total))

        if get_yes_no("Add more items? (Y/N): ") == 'n':
            break

    sgst = subtotal * Decimal("0.09")
    cgst = subtotal * Decimal("0.09")
    final_total = subtotal + sgst + cgst
    bill_date = datetime.datetime.now()

    try:

        cursor.execute(
            "INSERT INTO customers (name, mobile) VALUES (%s, %s)",
            (name, mobile)
        )
        customer_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO bills (customer_id, bill_date, subtotal, sgst, cgst, total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, bill_date, subtotal, sgst, cgst, final_total))

        bill_id = cursor.lastrowid

        for item in cart:
            cursor.execute("""
                INSERT INTO bill_items (bill_id, product_id, quantity, price, total)
                VALUES (%s, %s, %s, %s, %s)
            """, (bill_id, item[0], item[1], item[2], item[3]))

            cursor.execute(
                "UPDATE inventory SET quantity = quantity - %s WHERE id=%s",
                (item[1], item[0])
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Transaction failed:", e)
        return

    print("\nBill Generated Successfully!")
    print("Final Amount:", final_total)

    if get_yes_no("Generate PDF bill? (Y/N): ") == 'y':
        generate_pdf_bill(bill_id)

# ==========================
# VIEW BILLS
# ==========================

def view_bills():
    cursor.execute("""
        SELECT bills.id, customers.name, bills.total, bills.bill_date
        FROM bills
        JOIN customers ON bills.customer_id = customers.id
        ORDER BY bills.id DESC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No bills found.")
        return

    print("\n===== ALL BILLS =====")
    for row in rows:
        print(f"Bill ID: {row[0]} | Customer: {row[1]} | Total: {row[2]} | Date: {row[3]}")

    while True:
        bill_input = input("\nEnter Bill ID to open PDF or 0 to return: ")
        if bill_input == "0":
            return
        if validate_positive_int(bill_input):
            generate_pdf_bill(int(bill_input))
            return
        print("Invalid input.")

# ==========================
# UPDATE INVENTORY
# ==========================

def update_inventory():
    display_items()

    item_id = input("Enter Item ID to update: ")
    if not validate_positive_int(item_id):
        print("Invalid ID")
        return

    item_id = int(item_id)

    while True:
        try:
            price = Decimal(input("Enter new price: "))
            if price > 0:
                break
        except:
            pass
        print("Invalid price.")

    while True:
        qty_input = input("Enter new stock quantity: ")
        if validate_positive_int(qty_input):
            quantity = int(qty_input)
            break
        print("Invalid quantity.")

    cursor.execute(
        "UPDATE inventory SET price=%s, quantity=%s WHERE id=%s",
        (price, quantity, item_id)
    )
    conn.commit()
    print("Inventory updated.")

# ==========================
# ADD PRODUCT
# ==========================

def add_new_product():
    name = input("Enter product name: ")

    while True:
        try:
            price = Decimal(input("Enter price: "))
            if price > 0:
                break
        except:
            pass
        print("Invalid price.")

    while True:
        qty_input = input("Enter stock quantity: ")
        if validate_positive_int(qty_input):
            quantity = int(qty_input)
            break
        print("Invalid quantity.")

    cursor.execute("SELECT MAX(id) FROM inventory")
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1

    cursor.execute(
        "INSERT INTO inventory (id, name, price, quantity) VALUES (%s, %s, %s, %s)",
        (new_id, name, price, quantity)
    )
    conn.commit()
    print("Product added successfully.")

# ==========================
# UPDATE PRODUCT NAME
# ==========================

def update_product_name():
    display_items()
    item_id = input("Enter Product ID to rename: ")

    if not validate_positive_int(item_id):
        print("Invalid ID")
        return

    item_id = int(item_id)
    new_name = input("Enter new product name: ").strip()

    if len(new_name) < 2:
        print("Invalid name.")
        return

    cursor.execute(
        "UPDATE inventory SET name=%s WHERE id=%s",
        (new_name, item_id)
    )
    conn.commit()
    print("Product name updated.")

# ==========================
# DELETE PRODUCT (SAFE)
# ==========================

def delete_product():
    display_items()
    item_id = input("Enter Product ID to delete: ")

    if not validate_positive_int(item_id):
        print("Invalid ID")
        return

    item_id = int(item_id)

    cursor.execute("SELECT COUNT(*) FROM bill_items WHERE product_id=%s", (item_id,))
    if cursor.fetchone()[0] > 0:
        print("Cannot delete product. Used in previous bills.")
        return

    if get_yes_no("Are you sure? (Y/N): ") == 'y':
        cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id,))
        conn.commit()
        print("Product deleted.")

# ==========================
# DAILY SALES REPORT
# ==========================

def daily_sales_report():
    cursor.execute("""
        SELECT DATE(bill_date), COUNT(*), SUM(total)
        FROM bills
        GROUP BY DATE(bill_date)
        ORDER BY DATE(bill_date) DESC
    """)
    rows = cursor.fetchall()

    print("\n===== DAILY SALES REPORT =====")
    for row in rows:
        print(f"Date: {row[0]} | Bills: {row[1]} | Revenue: {row[2]}")

# ==========================
# MAIN MENU
# ==========================

def main():
    while True:
        print("\n===== MAIN MENU =====")
        print("1. New Customer")
        print("2. View Bills")
        print("3. Update Inventory")
        print("4. Add New Product")
        print("5. Update Product Name")
        print("6. Delete Product")
        print("7. Daily Sales Report")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            new_customer()
        elif choice == "2":
            view_bills()
        elif choice == "3":
            update_inventory()
        elif choice == "4":
            add_new_product()
        elif choice == "5":
            update_product_name()
        elif choice == "6":
            delete_product()
        elif choice == "7":
            daily_sales_report()
        elif choice == "8":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram exited safely.")
        cursor.close()
        conn.close()