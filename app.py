from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
from psycopg2.extras import RealDictCursor

app = Flask(__name__, template_folder="templats")
app.secret_key = "finance-dashboard-secret-key"

# =========================

# HOME

# =========================

@app.route("/")
def home():
if "user_id" in session:
return redirect(url_for("dashboard"))

```
return redirect(url_for("login"))
```

# =========================

# REGISTER

# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

```
if request.method == "POST":

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        return "All fields are required"

    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return "Email already registered"

    hashed_password = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """,
        (name, email, hashed_password)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("login"))

return render_template("register.html")
```

# =========================

# LOGIN

# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

```
if request.method == "POST":

    email = request.form.get("email")
    password = request.form.get("password")

    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and check_password_hash(user["password"], password):

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect(url_for("dashboard"))

    return "Invalid email or password"

return render_template("login.html")
```

# =========================

# DASHBOARD

# =========================

@app.route("/dashboard")
def dashboard():

```
if "user_id" not in session:
    return redirect(url_for("login"))

connection = get_connection()
cursor = connection.cursor(cursor_factory=RealDictCursor)

user_id = session["user_id"]

# Total income
cursor.execute(
    """
    SELECT COALESCE(SUM(amount), 0) AS total
    FROM transactions
    WHERE user_id = %s
    AND type = 'Income'
    """,
    (user_id,)
)

income_result = cursor.fetchone()
total_income = income_result["total"]

# Total expense
cursor.execute(
    """
    SELECT COALESCE(SUM(amount), 0) AS total
    FROM transactions
    WHERE user_id = %s
    AND type = 'Expense'
    """,
    (user_id,)
)

expense_result = cursor.fetchone()
total_expense = expense_result["total"]

# Recent transactions
cursor.execute(
    """
    SELECT
        transactions.id,
        transactions.amount,
        transactions.type,
        transactions.description,
        transactions.transaction_date,
        categories.name AS category
    FROM transactions
    JOIN categories
    ON transactions.category_id = categories.id
    WHERE transactions.user_id = %s
    ORDER BY transactions.transaction_date DESC,
             transactions.id DESC
    LIMIT 10
    """,
    (user_id,)
)

transactions = cursor.fetchall()

cursor.close()
connection.close()

balance = float(total_income) - float(total_expense)

return render_template(
    "dashboard.html",
    total_income=total_income,
    total_expense=total_expense,
    balance=balance,
    transactions=transactions,
    user_name=session.get("user_name")
)
```

# =========================

# GET CATEGORIES

# =========================

@app.route("/api/categories")
def get_categories():

```
if "user_id" not in session:
    return jsonify({"error": "Unauthorized"}), 401

connection = get_connection()
cursor = connection.cursor(cursor_factory=RealDictCursor)

cursor.execute(
    """
    SELECT id, name, type
    FROM categories
    ORDER BY type, name
    """
)

categories = cursor.fetchall()

cursor.close()
connection.close()

return jsonify(categories)
```

# =========================

# MONTHLY ANALYTICS

# =========================

@app.route("/api/monthly")
def monthly():

```
if "user_id" not in session:
    return jsonify({"error": "Unauthorized"}), 401

user_id = session["user_id"]

connection = get_connection()
cursor = connection.cursor(cursor_factory=RealDictCursor)

cursor.execute(
    """
    SELECT
        TO_CHAR(transaction_date, 'YYYY-MM') AS month,
        type,
        COALESCE(SUM(amount), 0) AS total
    FROM transactions
    WHERE user_id = %s
    GROUP BY
        TO_CHAR(transaction_date, 'YYYY-MM'),
        type
    ORDER BY month
    """,
    (user_id,)
)

data = cursor.fetchall()

cursor.close()
connection.close()

result = {}

for row in data:

    month = row["month"]

    if month not in result:
        result[month] = {
            "Income": 0,
            "Expense": 0
        }

    result[month][row["type"]] = float(row["total"])

return jsonify(result)
```

# =========================

# ADD TRANSACTION

# =========================

@app.route("/add_transaction", methods=["POST"])
def add_transaction():

```
if "user_id" not in session:
    return redirect(url_for("login"))

amount = request.form.get("amount")
transaction_type = request.form.get("type")
category_id = request.form.get("category_id")
description = request.form.get("description")
transaction_date = request.form.get("transaction_date")

if not amount or not transaction_type or not category_id or not transaction_date:
    return "Please fill all required fields"

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    INSERT INTO transactions
    (
        user_id,
        category_id,
        amount,
        type,
        description,
        transaction_date
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    (
        session["user_id"],
        category_id,
        amount,
        transaction_type,
        description,
        transaction_date
    )
)

connection.commit()

cursor.close()
connection.close()

return redirect(url_for("dashboard"))
```

# =========================

# EDIT TRANSACTION

# =========================

@app.route("/edit_transaction/[int:transaction_id](int:transaction_id)", methods=["GET", "POST"])
def edit_transaction(transaction_id):

```
if "user_id" not in session:
    return redirect(url_for("login"))

connection = get_connection()
cursor = connection.cursor(cursor_factory=RealDictCursor)

if request.method == "POST":

    amount = request.form.get("amount")
    transaction_type = request.form.get("type")
    category_id = request.form.get("category_id")
    description = request.form.get("description")
    transaction_date = request.form.get("transaction_date")

    cursor.execute(
        """
        UPDATE transactions
        SET
            amount = %s,
            type = %s,
            category_id = %s,
            description = %s,
            transaction_date = %s
        WHERE id = %s
        AND user_id = %s
        """,
        (
            amount,
            transaction_type,
            category_id,
            description,
            transaction_date,
            transaction_id,
            session["user_id"]
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("dashboard"))

cursor.execute(
    """
    SELECT
        transactions.*,
        categories.name AS category
    FROM transactions
    JOIN categories
    ON transactions.category_id = categories.id
    WHERE transactions.id = %s
    AND transactions.user_id = %s
    """,
    (
        transaction_id,
        session["user_id"]
    )
)

transaction = cursor.fetchone()

cursor.execute(
    """
    SELECT id, name, type
    FROM categories
    ORDER BY type, name
    """
)

categories = cursor.fetchall()

cursor.close()
connection.close()

if not transaction:
    return "Transaction not found"

return render_template(
    "edit_transaction.html",
    transaction=transaction,
    categories=categories
)
```

# =========================

# DELETE TRANSACTION

# =========================

@app.route("/delete_transaction/[int:transaction_id](int:transaction_id)", methods=["POST", "GET"])
def delete_transaction(transaction_id):

```
if "user_id" not in session:
    return redirect(url_for("login"))

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    DELETE FROM transactions
    WHERE id = %s
    AND user_id = %s
    """,
    (
        transaction_id,
        session["user_id"]
    )
)

connection.commit()

cursor.close()
connection.close()

return redirect(url_for("dashboard"))
```

# =========================

# LOGOUT

# =========================

@app.route("/logout")
def logout():

```
session.clear()

return redirect(url_for("login"))
```

# =========================

# RUN APPLICATION

# =========================

if **name** == "**main**":
app.run(debug=True)
