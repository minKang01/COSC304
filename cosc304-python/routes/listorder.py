"""Question 1 (10 marks): list all orders and their ordered products."""

from flask import Blueprint, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("listorder", __name__)


@bp.get("/listorder")
def list_orders():
    connection = None
    try:
        # TODO (Q1): Open the orders database with get_connection().
        connection = get_connection()
        cursor = connection.cursor()

        # TODO: Query ordersummary and display each order's summary in a table.
        sql = ("SELECT O.orderId, O.orderDate, C.customerId, C.firstName, C.lastName, O.totalAmount "
               "FROM ordersummary O JOIN customer C ON O.customerId = C.customerId "
               "ORDER BY O.orderId")
        cursor.execute(sql)
        orders = cursor.fetchall()

        html = """
            <h1>Order List</h1>
            <table border="1">
            <tr><th>Order Id</th><th>Order Date</th><th>Customer Id</th><th>Customer Name</th><th>Total Amount</th></tr>
        """

        for order in orders:
            order_id = order[0]
            order_date = escape_html(str(order[1]))
            customer_id = order[2]
            customer_name = escape_html(order[3] + " " + order[4])
            total = format_currency(order[5])

            html += f"""
            <tr><td>{order_id}</td><td>{order_date}</td><td>{customer_id}</td><td>{customer_name}</td><td>{total}</td></tr>
            """

            # TODO: For each order, query orderproduct joined to product to show items.
            #       Use SQL parameters with ? placeholders; e.g. cursor.execute(sql, order_id).
            #       Use escape_html(text) for text and format_currency(value) for money.
            # Products in this order (orderId passed as a ? parameter)
            sql = ("SELECT P.productId, P.productName, OP.quantity, OP.price "
                   "FROM orderproduct OP JOIN product P ON OP.productId = P.productId "
                   "WHERE OP.orderId = ?")
            cursor.execute(sql, order_id)

            html += """
                <tr><td></td><td colspan="4">
                <table border="1">
                <tr><th>Product Id</th><th>Product Name</th><th>Quantity</th><th>Price</th></tr>
            """
            for product in cursor:
                product_id = product[0]
                product_name = escape_html(product[1])
                quantity = product[2]
                price = format_currency(product[3])

                html += f"""
                    <tr><td>{product_id}</td><td>{product_name}</td><td>{quantity}</td><td>{price}</td></tr>
                """
            html += """
                </table>
                </td></tr>
            """

        html += """
            </table>
            <p><a href="/">Back to main page</a></p>
        """

        return html_page("Min and Harsh Grocery Order List", html)
    
    except Exception:
        # Log the actual error in the terminal; do not display credentials to users.
        current_app.logger.exception("Unable to list orders")
        return html_page("Order List Error", "<h1>Unable to retrieve orders.</h1>"), 500
    
    finally:
        # TODO (Q1): Close the connection if it was opened.
        # Example: if connection is not None: connection.close()
        if connection is not None:
            connection.close()