# 💰 Personal Finance & Expense Analytics Dashboard

A web-based Personal Finance and Expense Analytics Dashboard built using
Python Flask, MySQL, HTML, CSS and JavaScript.

The application helps users manage their income and expenses, view their
financial balance, analyze spending categories and compare monthly income
with expenses.

## 🚀 Features

- User Registration
- User Login
- Secure Password Hashing
- Personal Finance Dashboard
- Add Income
- Add Expense
- Expense Categories
- Income Categories
- Edit Transactions
- Delete Transactions
- Search Transactions
- Filter by Type
- Filter by Category
- Total Income Calculation
- Total Expense Calculation
- Balance Calculation
- Expense by Category Chart
- Monthly Income vs Expense Chart
- Responsive UI

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript
- Canvas API

### Backend

- Python
- Flask

### Database

- MySQL

### Development Tools

- Visual Studio Code
- Git
- GitHub

## 📂 Project Structure

Personal-Finance-Dashboard/

├── app.py

├── database.py

├── README.md

├── .gitignore

│

├── templates/

│   ├── login.html

│   ├── register.html

│   ├── dashboard.html

│   └── edit_transaction.html

│

├── static/

│   ├── css/

│   │   └── style.css

│   │

│   └── js/

│       └── dashboard.js

│

└── venv/

## 🗄️ Database

The project uses MySQL with the following database:

finance_db

Main tables:

- users
- categories
- transactions

## ⚙️ Installation

### 1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

### 2. Open the project

cd Personal-Finance-Dashboard

### 3. Create virtual environment

python -m venv venv

### 4. Install dependencies

pip install flask mysql-connector-python werkzeug

### 5. Create MySQL database

CREATE DATABASE finance_db;

### 6. Run the application

venv\Scripts\python.exe app.py

### 7. Open in browser

http://127.0.0.1:5000

## 📊 Dashboard

The dashboard provides:

- Total Income
- Total Expense
- Current Balance
- Expense Category Analysis
- Monthly Income vs Expense Analysis
- Transaction Management

## 🔐 Security

Passwords are stored using password hashing instead of plain-text
password storage.

The project also uses user-specific transaction access.

## 🎯 Future Improvements

- Monthly budget planning
- Budget alerts
- PDF financial reports
- CSV export
- Advanced analytics
- Dark mode
- Cloud deployment
- Mobile optimization

## 👨‍💻 Author

Rahul

## 📌 Project Type

Personal Finance Management and Data Analytics Web Application