"""Question 2 (20 marks): validate and save a completed order."""

from decimal import Decimal
from flask import Blueprint, request, session, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("order", __name__)

def error_page(message):
    return html_page("Order Processing Error", f"""
            <h1>{message}</h1>
            <p><a href="/checkout">Back to checkout</a></p>
    """), 400


@bp.post("/order")
def place_order():
    customer_id = request.form.get("customerId", "").strip()
    password = request.form.get("password", "")

    product_list = session.get("productList")

    connection = None
    try:
        # TODO (Q2): Validate that customer_id is a positive integer and exists
        #       in the customer table. Show an error if not valid.
        if customer_id == "" or not customer_id.isdecimal() or len(customer_id) > 9 \
                or int(customer_id) <= 0:
            return error_page("Invalid customer id. Go back and try again.")

        # TODO: Show an error if the products list is empty.
        if product_list is None or len(product_list) == 0:
            return error_page("Your shopping cart is empty!")

        products = list(product_list.values())

        # TODO: Open a connection to the orders database.
        connection = get_connection()
        cursor = connection.cursor()

        sql = "SELECT password FROM customer WHERE customerId = ?"
        cursor.execute(sql, int(customer_id))
        customer = cursor.fetchone()
        if customer is None:
            return error_page("Invalid customer id. Go back and try again.")

        # Bonus: the password must match the customer's password
        if password == "" or customer[0] != password:
            return error_page("Incorrect password. Go back and try again.")

        # TODO: INSERT ordersummary with the customer ID and order date.
        #       Use a parameterized INSERT and return the generated orderId.
        #       In SQL Server, INSERT ... OUTPUT INSERTED.orderId ... works.
        sql = ("INSERT INTO ordersummary (customerId, orderDate) "
               "OUTPUT INSERTED.orderId VALUES (?, GETDATE())")
        cursor.execute(sql, int(customer_id))
        order_id = cursor.fetchone()[0]

        # TODO: Display order ID, purchased products, and total amount.
        html = """
            <h1>Your Order Summary</h1>
            <table border="1">
            <tr><th>Product Id</th><th>Product Name</th><th>Quantity</th><th>Price</th><th>Subtotal</th></tr>
        """

        # TODO: Loop through products; entries have id, name, price, quantity.
        #       INSERT each item into orderproduct, using ? placeholders.
        #       Use escape_html() for HTML text and format_currency() for prices.
        total = Decimal("0.00")
        sql = "INSERT INTO orderproduct (orderId, productId, quantity, price) VALUES (?, ?, ?, ?)"
        for product in products:
            price = Decimal(str(product["price"]))
            quantity = int(product["quantity"])
            subtotal = price * quantity
            total += subtotal

            cursor.execute(sql, order_id, int(product["id"]), quantity, price)

            product_id = escape_html(product["id"])
            product_name = escape_html(product["name"])
            html += f"""
                <tr><td>{product_id}</td><td>{product_name}</td><td>{quantity}</td><td>{format_currency(price)}</td><td>{format_currency(subtotal)}</td></tr>
            """

        # TODO: UPDATE ordersummary.totalAmount for the order.
        #       Commit only when all statements succeed; roll back on failure.
        sql = "UPDATE ordersummary SET totalAmount = ? WHERE orderId = ?"
        cursor.execute(sql, total, order_id)

        connection.commit()

        html += f"""
            </table>
            <h2>Order Total: {format_currency(total)}</h2>
            <h2>Order completed. Your order reference number is: {order_id}</h2>
            <p><a href="/">Back to main page</a></p>
        """

        # TODO: Clear session['productList'] only after the order is committed.
        session["productList"] = {}

        return html_page("Min and Harsh Grocery Order Processing", html)
    except Exception:
        current_app.logger.exception("Unable to process order")
        # TODO (Q2): Roll back any uncommitted inserts on a failure.
        if connection is not None:
            connection.rollback()
        return html_page("Order Processing Error",
                         "<h1>Unable to process the order.</h1>"), 500
    finally:
        # TODO (Q2): Close the connection if it was opened.
        if connection is not None:
            connection.close()