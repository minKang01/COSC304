"""Lab 8 TODO: daily administrator sales report."""

from flask import Blueprint, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page
from routes.auth import require_login

bp = Blueprint("admin", __name__)


@bp.get("/admin")
def admin_report():
    # TODO: Call require_login() and return its redirect when needed.
    redirect_response = require_login()
    if redirect_response is not None:
        return redirect_response

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

    # TODO: Query total sales for each day from ordersummary. Use
    #       CAST(orderDate AS date), SUM(totalAmount), GROUP BY and ORDER BY.
        sql = """
            SELECT CAST(orderDate AS date) AS orderDay, SUM(totalAmount) AS totalSales
            FROM ordersummary
            GROUP BY CAST(orderDate AS date)
            ORDER BY orderDay
        """
        cursor.execute(sql)

    # TODO: Display the daily sales in an HTML table; close the connection.
        html = """
            <h1>Daily Sales Report</h1>
            <table border="1">
            <tr><th>Date</th><th>Total Sales</th></tr>
        """
        for row in cursor:
            order_day = escape_html(str(row[0]))
            total_sales = format_currency(row[1])
            html += f"""
                <tr><td>{order_day}</td><td>{total_sales}</td></tr>
            """
        html += """
            </table>
            <p><a href="/">Main Page</a></p>
        """

        return html_page("Administrator Report", html)
    except Exception:
        current_app.logger.error("Error generating admin report")
        return html_page("Administrator Report", """
            <h1>Error retreiving sales report</h1>
            <p>Could not generate report.</p>
            """), 500
    finally:
        if connection is not None:
            connection.close()
