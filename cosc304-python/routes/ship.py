"""Lab 8 TODO: process one order as an all-or-nothing shipment."""

from flask import Blueprint, request, current_app
from db import get_connection
from html_utils import escape_html, html_page

bp = Blueprint("ship", __name__)


@bp.get("/ship")
def ship_order():
    raw_order_id = request.args.get("orderId", "")

    # TODO: Validate orderId and retrieve ALL orderproduct rows for the order.
    if not raw_order_id.isdecimal() or len(raw_order_id) > 9 or int(raw_order_id) <= 0:
        return html_page("Shipment Processing", """
            <h1>Invalid order ID</h1>
            <p><a href="/">Main Page</a></p>
        """), 400
    order_id = int(raw_order_id)

    # TODO: Open one connection (get_connection defaults to autocommit=False).
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = "SELECT productId, quantity FROM orderproduct WHERE orderId = ?"
        cursor.execute(sql, order_id)
        items = cursor.fetchall()

        if len(items) == 0:
            return html_page("Shipment Processing", f"""
                <h1>Order  {order_id} not found or has no items</h1>
                <p><a href="/">Main Page</a></p>
            """), 404

    # TODO: Create a shipment record for warehouseId = 1.
        sql = ("INSERT INTO shipment (shipmentDate, shipmentDesc, warehouseId) VALUES (GETDATE(), ?, 1) ")
        cursor.execute(sql,"Shipment for order" + str(order_id))
        html = f"""
            <h1>Shipment for Order {order_id}</h1>
            <table border="1">
            <tr><th>Product Id</th><th>Quantity Ordered</th><th>Previous Inventory</th><th>New Inventory</th></tr>
        """

    # TODO: For each ordered product, verify warehouse 1 has enough inventory
    #       and update productinventory by subtracting the ordered quantity.
        for item in items:
            product_id = item[0]
            quantity = item[1]

            sql = "SELECT quantity FROM productinventory WHERE productId = ? AND warehouseId = 1"
            cursor.execute(sql, product_id)
            row = cursor.fetchone()
            if row is None:
                inventory = 0
            else:
                inventory = row[0]

            # Not enough stock: undo the shipment row and any earlier updates
            if inventory < quantity:
                connection.rollback()
                return html_page("Shipment Processing", f"""
                    <h1>Not enough inventory for product {product_id}</h1>
                    <p>Ordered {quantity}, warehouse 1 has {inventory}. No changes were made.</p>
                    <p><a href="/">Main Page</a></p>
                """)
            sql = ("UPDATE productinventory SET quantity = quantity - ? WHERE productId = ? AND warehouseId = 1")
            cursor.execute(sql, quantity, product_id)
            html += f"""
                <tr><td>{product_id}</td><td>{quantity}</td><td>{inventory}</td><td>{inventory - quantity}</td></tr>
            """

    # TODO: Commit the transaction only if ALL items can be shipped.
        connection.commit()

    # TODO: Display a success or failure message and a Main Page link.
        html += f"""
            </table>
            <h1>Shipment for Order {order_id} Processed Successfully</h1>
            <p><a href="/">Main Page</a></p>
        """

        return html_page("Shipment Processing", html)
    except Exception:
        # TODO: On any error, rollback() all changes, including the shipment row
        #       and any preceding inventory updates; close the connection.
        current_app.logger.exception("Error processing shipment")
        if connection is not None:
            connection.rollback()
        return html_page("Shipment Processing", """
            <h1>Error processing shipment</h1>
            <p><a href="/">Main Page</a></p>
        """), 500
    finally:
        if connection is not None:
            connection.close()