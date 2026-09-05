from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templats")

app.secret_key = "finance-dashboard-secret-key"


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return redirect(url_for("login"))


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:

            connection = get_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                query,
                (name, email, hashed_password)
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("login"))

        except Exception as e:

            return f"Registration Error: {e}"

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            connection = get_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:

                if check_password_hash(
                    user["password"],
                    password
                ):

                    session["user_id"] = user["id"]
                    session["user_name"] = user["name"]

                    return redirect(
                        url_for("dashboard")
                    )

            return "Invalid email or password"

        except Exception as e:

            return f"Login Error: {e}"

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    # TOTAL INCOME

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = %s
        AND type = 'Income'
        """,
        (session["user_id"],)
    )

    income = cursor.fetchone()["total"]


    # TOTAL EXPENSE

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = %s
        AND type = 'Expense'
        """,
        (session["user_id"],)
    )

    expense = cursor.fetchone()["total"]


    # TRANSACTIONS

    cursor.execute(
        """
        SELECT
            transactions.*,
            categories.name AS category_name
        FROM transactions
        JOIN categories
        ON transactions.category_id =
           categories.id
        WHERE transactions.user_id = %s
        ORDER BY
            transaction_date DESC,
            id DESC
        """,
        (session["user_id"],)
    )

    transactions = cursor.fetchall()


    # CATEGORIES

    cursor.execute(
        """
        SELECT *
        FROM categories
        ORDER BY type, name
        """
    )

    categories = cursor.fetchall()


    cursor.close()
    connection.close()


    balance = (
        float(income)
        -
        float(expense)
    )


    return render_template(
        "dashboard.html",
        name=session["user_name"],
        income=float(income),
        expense=float(expense),
        balance=balance,
        transactions=transactions,
        categories=categories
    )


# =========================
# EXPENSE CATEGORY API
# =========================

@app.route("/api/expense_categories")
def expense_categories():

    if "user_id" not in session:
        return jsonify([])


    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            categories.name AS category_name,
            SUM(transactions.amount) AS total
        FROM transactions
        JOIN categories
        ON transactions.category_id =
           categories.id
        WHERE transactions.user_id = %s
        AND transactions.type = 'Expense'
        GROUP BY categories.name
        ORDER BY total DESC
        """,
        (session["user_id"],)
    )


    data = cursor.fetchall()


    cursor.close()
    connection.close()


    result = []


    for item in data:

        result.append(
            {
                "name":
                    item["category_name"],

                "total":
                    float(item["total"])
            }
        )


    return jsonify(result)


# =========================
# MONTHLY DATA API
# =========================

@app.route("/api/monthly")
def monthly_data():

    if "user_id" not in session:
        return jsonify([])


    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    cursor.execute(
        """
        SELECT
            DATE_FORMAT(
                transaction_date,
                '%Y-%m'
            ) AS month,

            type,

            SUM(amount) AS total

        FROM transactions

        WHERE user_id = %s

        GROUP BY
            DATE_FORMAT(
                transaction_date,
                '%Y-%m'
            ),
            type

        ORDER BY month
        """,
        (session["user_id"],)
    )


    rows = cursor.fetchall()


    cursor.close()
    connection.close()


    months = {}


    for row in rows:

        month = row["month"]


        if month not in months:

            months[month] = {
                "month": month,
                "income": 0,
                "expense": 0
            }


        if row["type"] == "Income":

            months[month]["income"] = \
                float(row["total"])

        else:

            months[month]["expense"] = \
                float(row["total"])


    return jsonify(
        list(months.values())
    )


# =========================
# ADD TRANSACTION
# =========================

@app.route(
    "/add_transaction",
    methods=["POST"]
)
def add_transaction():

    if "user_id" not in session:
        return redirect(url_for("login"))


    amount = request.form["amount"]

    transaction_type = \
        request.form["type"]

    category_id = \
        request.form["category_id"]

    description = \
        request.form["description"]

    transaction_date = \
        request.form["transaction_date"]


    connection = get_connection()

    cursor = connection.cursor()


    # CHECK CATEGORY

    cursor.execute(
        """
        SELECT id
        FROM categories
        WHERE id = %s
        AND type = %s
        """,
        (
            category_id,
            transaction_type
        )
    )


    category = cursor.fetchone()


    if not category:

        cursor.close()
        connection.close()

        return "Invalid category"


    # INSERT

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

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
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


    return redirect(
        url_for("dashboard")
    )


# =========================
# EDIT TRANSACTION
# =========================

@app.route(
    "/edit_transaction/<int:transaction_id>",
    methods=["GET", "POST"]
)
def edit_transaction(transaction_id):

    if "user_id" not in session:
        return redirect(url_for("login"))


    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    if request.method == "POST":

        amount = \
            request.form["amount"]

        transaction_type = \
            request.form["type"]

        category_id = \
            request.form["category_id"]

        description = \
            request.form["description"]

        transaction_date = \
            request.form["transaction_date"]


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


        return redirect(
            url_for("dashboard")
        )


    # GET TRANSACTION

    cursor.execute(
        """
        SELECT
            transactions.*,
            categories.name AS category_name

        FROM transactions

        JOIN categories

        ON transactions.category_id =
           categories.id

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
        SELECT *
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


# =========================
# DELETE TRANSACTION
# =========================

@app.route(
    "/delete_transaction/<int:transaction_id>",
    methods=["POST"]
)
def delete_transaction(transaction_id):

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


    return redirect(
        url_for("dashboard")
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )