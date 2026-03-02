# 🛒 Supermarket Billing System

A Python-based console application that simulates a real-world supermarket billing system with inventory management, data validation, and professional PDF invoice generation.

---

## 📌 Project Overview

This project is designed to replicate a real supermarket billing counter.  
It allows multiple customers to shop in a single run, validates user inputs, updates stock dynamically, and generates professional PDF bills.

The system follows an Object-Oriented Programming (OOP) approach for better structure and maintainability.

---

## 🚀 Features

### 👤 Customer Features
- Name validation (alphabets only)
- Mobile number validation (exactly 10 digits)
- Multiple item selection
- Quantity validation (positive integers only)
- Automatic stock validation
- GST calculation (SGST + CGST)
- Professional PDF bill generation
- Automatic bill opening
- View previously generated bills

### 🛠 Admin Features
- Password-protected admin access
- Update product price
- Update stock quantity
- Real-time inventory updates

---

## 🧾 Billing Details

- Subtotal Calculation
- SGST (9%)
- CGST (9%)
- Final Payable Amount
- Unique Bill Number (timestamp-based)
- A4 formatted PDF invoice

---

## 🏗 Project Structure
supermarket/
│
├── supermarket.py
├── README.md
├── bills_pdf/ (auto-generated)
└── .gitignore

---

## 🛠 Technologies Used

- Python 3
- OOP Concepts
- ReportLab (PDF generation)
- Regex (Input validation)
- Git & GitHub

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
git clone https://github.com/Sharath67/supermarket-billing-system.git

cd supermarket-billing-system

### 2️⃣ Install Required Library
pip install reportlab

### 3️⃣ Run Application
python3 supermarket.py

---

## 🔐 Admin Credentials
Password: admin123


---

## 📚 Key Learning Outcomes

- Object-Oriented Programming (OOP)
- Input Data Validation
- File Handling
- PDF Invoice Generation
- Inventory Management Logic
- Git Version Control
- Clean Code Structuring

---

## 📈 Future Improvements

- Persistent inventory storage using CSV or SQLite
- Sales analytics dashboard
- GUI version (Tkinter)
- Daily revenue reporting
- User authentication system

---

## 👨‍💻 Author

Sharath B M 
Data analyst 

---

## 📄 License

This project is created for educational and internship demonstration purposes.
