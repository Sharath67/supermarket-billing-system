# ==============================
# IMPORT REQUIRED LIBRARIES
# ==============================

import datetime          # To generate date and time for bill
import os                # To create folders and manage files
import subprocess        # To open PDF automatically
import re                # For regex validation

# PDF generation library
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes


# ==============================
# VALIDATION FUNCTIONS
# ==============================

def validate_name(name):
    # Allows only alphabets and spaces
    return bool(re.fullmatch(r"[A-Za-z ]+", name))


def validate_mobile(mobile):
    # Allows exactly 10 digits
    return bool(re.fullmatch(r"\d{10}", mobile))


def validate_positive_int(value):
    # Check if value is positive integer
    return value.isdigit() and int(value) > 0


def validate_positive_float(value):
    # Check if value is positive decimal
    try:
        return float(value) > 0
    except ValueError:
        return False


# ==============================
# INVENTORY CLASS
# Handles stock and admin updates
# ==============================

class Inventory:

    def __init__(self):
        # Initial stock data stored in dictionary
        self.stock = {
            1: {"name": "Rice (1kg)", "price": 60, "quantity": 50},
            2: {"name": "Milk (1L)", "price": 45, "quantity": 30},
            3: {"name": "Bread", "price": 40, "quantity": 25},
            4: {"name": "Eggs (12 pcs)", "price": 75, "quantity": 20},
            5: {"name": "Sugar (1kg)", "price": 50, "quantity": 40}
        }

    def display_items(self):
        # Display all available items
        print("\nAvailable Items:")
        print("ID   Item Name           Price   Stock")
        print("-" * 50)
        for item_id, details in self.stock.items():
            print(f"{item_id:<5}{details['name']:<20}{details['price']:<8}{details['quantity']}")

    def check_stock(self, item_id, qty):
        # Check if requested quantity is available
        return self.stock[item_id]["quantity"] >= qty

    def update_stock(self, item_id, qty):
        # Reduce stock after purchase
        self.stock[item_id]["quantity"] -= qty

    def update_item(self):
        # Admin function to update price and quantity
        self.display_items()

        try:
            item_id = int(input("Enter Item ID to update: "))
            if item_id not in self.stock:
                print("Invalid Item ID")
                return

            # Validate price
            while True:
                price_input = input("Enter new price: ")
                if validate_positive_float(price_input):
                    new_price = float(price_input)
                    break
                print("Invalid price. Enter positive number.")

            # Validate quantity
            while True:
                qty_input = input("Enter new stock quantity: ")
                if validate_positive_int(qty_input):
                    new_qty = int(qty_input)
                    break
                print("Invalid stock. Enter positive integer.")

            # Update values
            self.stock[item_id]["price"] = new_price
            self.stock[item_id]["quantity"] = new_qty

            print("Item updated successfully!")

        except ValueError:
            print("Invalid input.")


# ==============================
# BILLING CLASS
# Handles cart and bill generation
# ==============================

class Billing:

    SGST_RATE = 0.09
    CGST_RATE = 0.09

    def __init__(self, customer_name, phone):
        self.customer_name = customer_name
        self.phone = phone
        self.cart = {}
        self.subtotal = 0
        self.sgst = 0
        self.cgst = 0
        self.final_total = 0

    def add_to_cart(self, item_id, item_details, qty):
        # Add selected item to cart
        self.cart[item_id] = {
            "name": item_details["name"],
            "price": item_details["price"],
            "quantity": qty
        }

    def calculate_totals(self):
        # Calculate subtotal
        self.subtotal = sum(
            item["price"] * item["quantity"]
            for item in self.cart.values()
        )

        # Calculate taxes
        self.sgst = self.subtotal * self.SGST_RATE
        self.cgst = self.subtotal * self.CGST_RATE
        self.final_total = self.subtotal + self.sgst + self.cgst

    def generate_bill(self):
        # Generate unique bill number using timestamp
        now = datetime.datetime.now()
        bill_no = now.strftime("%Y%m%d%H%M%S")

        print("\nGenerating PDF Bill...")

        self.save_bill_as_pdf(bill_no, now)

    def save_bill_as_pdf(self, bill_no, now):
        # Create folder if not exists
        if not os.path.exists("bills_pdf"):
            os.makedirs("bills_pdf")

        file_path = f"bills_pdf/Bill_{bill_no}.pdf"

        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        # Add Title
        elements.append(Paragraph("<b>SHARATH SUPER MARKET BILL</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Add Customer Details
        elements.append(Paragraph(f"Bill No: {bill_no}", styles["Normal"]))
        elements.append(Paragraph(f"Date: {now.strftime('%d-%m-%Y %H:%M:%S')}", styles["Normal"]))
        elements.append(Paragraph(f"Customer: {self.customer_name}", styles["Normal"]))
        elements.append(Paragraph(f"Phone: {self.phone}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Table header
        data = [["Item", "Qty", "Price", "Total"]]

        # Add cart items to table
        for item in self.cart.values():
            total = item["price"] * item["quantity"]
            data.append([
                item["name"],
                str(item["quantity"]),
                str(item["price"]),
                str(total)
            ])

        # Add totals
        data.append(["", "", "Subtotal", f"{self.subtotal:.2f}"])
        data.append(["", "", "SGST (9%)", f"{self.sgst:.2f}"])
        data.append(["", "", "CGST (9%)", f"{self.cgst:.2f}"])
        data.append(["", "", "Final Amount", f"{self.final_total:.2f}"])

        # Create table
        table = Table(data, colWidths=[200, 60, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER')
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements)

        print(f"Bill saved at: {file_path}")

        # Automatically open the PDF
        subprocess.run(["xdg-open", file_path])


# ==============================
# VIEW OLD BILLS FUNCTION
# ==============================

def view_old_bills():
    folder = "bills_pdf"

    if not os.path.exists(folder):
        print("No bills found.")
        return

    files = os.listdir(folder)
    if not files:
        print("No bills available.")
        return

    print("\nAvailable Bills:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    try:
        choice = int(input("Enter bill number to open (0 to cancel): "))
        if choice == 0:
            return

        selected_file = files[choice - 1]
        subprocess.run(["xdg-open", os.path.join(folder, selected_file)])

    except (ValueError, IndexError):
        print("Invalid selection.")


# ==============================
# MAIN FUNCTION
# ==============================

def main():
    inventory = Inventory()

    while True:
        print("\n===== MAIN MENU =====")
        print("1. New Customer")
        print("2. View Old Bills")
        print("3. Update Price & Stock (Admin)")
        print("4. Exit")

        # Menu validation
        while True:
            choice = input("Enter choice (1-4): ")
            if choice in ["1", "2", "3", "4"]:
                break
            print("Invalid choice. Select 1-4.")

        if choice == "1":

            # Name validation
            while True:
                name = input("Enter Customer Name: ")
                if validate_name(name):
                    break
                print("Invalid name. Alphabets only.")

            # Mobile validation
            while True:
                phone = input("Enter Mobile Number (10 digits): ")
                if validate_mobile(phone):
                    break
                print("Invalid mobile number.")

            billing = Billing(name, phone)

            # Shopping loop
            while True:
                inventory.display_items()

                item_id = input("Enter Item ID: ")
                if not validate_positive_int(item_id):
                    print("Invalid ID.")
                    continue

                item_id = int(item_id)

                if item_id not in inventory.stock:
                    print("Item does not exist.")
                    continue

                qty_input = input("Enter Quantity: ")
                if not validate_positive_int(qty_input):
                    print("Invalid quantity.")
                    continue

                qty = int(qty_input)

                if not inventory.check_stock(item_id, qty):
                    print("Insufficient stock.")
                    continue

                billing.add_to_cart(item_id, inventory.stock[item_id], qty)
                inventory.update_stock(item_id, qty)

                cont = input("Add more items? (Y/N): ").lower()
                if cont == 'n':
                    break

            billing.calculate_totals()
            billing.generate_bill()

        elif choice == "2":
            view_old_bills()

        elif choice == "3":
            password = input("Enter Admin Password: ")
            if password == "admin123":
                inventory.update_item()
            else:
                print("Incorrect password.")

        elif choice == "4":
            print("System shutting down...")
            break


# Program execution starts here
if __name__ == "__main__":
    main()