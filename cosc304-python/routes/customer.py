"""Lab 8 TODO: show information for the currently logged-in customer."""

from flask import Blueprint, session, current_app
from db import get_connection
from html_utils import escape_html, html_page
from routes.auth import require_login

bp = Blueprint("customer", __name__)


@bp.get("/customer")
def customer_information():
    redirect_response = require_login()
    if redirect_response is not None:
        return redirect_response

    username = session["authenticatedUser"]
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
    
    # TODO: Use a parameterized SQL query to find customer.userid = username.
    #       Do not use a customer ID submitted in the URL.
        sql = "SELECT customerId, firstName, lastName, email, phonenum, address, city, state, postalCode, country, userid FROM customer WHERE userid = ?"
        cursor.execute(sql, username)
        customer = cursor.fetchone()

    # TODO: Display customer name/contact/address, but NEVER the password.
        if customer is None:
            return html_page("Customer Information", """
                <h1>Customer info not found</h1>
                <p><a href="/">Main Page</a></p>
            """), 404

    # TODO: Handle a missing customer record; close database resources.
        labels = ["Customer ID", "First Name", "Last Name", "Email", "Phone Number", "Address", "City", "State", "Postal Code", "Country", "User ID"]
        html = "<h1>Customer Info</h1><table border='1'>"
        for i in range(len(labels)):
            if customer[i] is None:
                value = ""
            else:
                value = escape_html(str(customer[i]))
            html += f"<tr><td>{labels[i]}</td><td>{value}</td></tr>"
        html += "</table><p><a href='/'>Main Page</a></p>"
        return html_page("Customer Information", html)
    except Exception:
        current_app.logger.exception("Error retrieving customer information")
        return html_page("Customer Information", """
            <h1>Error retrieving customer information</h1>
            <p><a href="/">Main Page</a></p>
        """), 500
    finally:
        if connection is not None:
            connection.close()
