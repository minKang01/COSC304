"""Provided route: prompt for customer ID and submit checkout to /order."""

from flask import Blueprint
from html_utils import html_page

bp = Blueprint("checkout", __name__)


@bp.get("/checkout")
def checkout():
    return html_page("Grocery Store Checkout", """
        <h1>Checkout</h1>
        <p>Enter your customer ID and password to complete the transaction:</p>
        <form method="post" action="/order">
        <table>
            <tr><td>Customer ID:</td><td><input type="text" name="customerId" size="10" required></td></tr>
            <tr><td>Password:</td><td><input type="password" name="password" size="20" required></td></tr>
        </table>
        <input type="submit" value="Place Order">
        <input type="reset" value="Reset">
        </form>
        <p><a href="/showcart">Return to Shopping Cart</a></p>
    """)