"""Provided route: display the current session's shopping cart."""

from decimal import Decimal
from flask import Blueprint, redirect, request, session, url_for
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("showcart", __name__)


@bp.get("/showcart")
def show_cart():
    product_list = session.get("productList")
    if product_list is None or len(product_list) == 0:
        return html_page("Your Shopping Cart", "<h1>Your shopping cart is empty!</h1>"
            '<p><a href="/listprod">Continue Shopping</a></p>')

    html = """
        <h1>Your Shopping Cart</h1>
        <table border="1">
        <tr><th>Product Id</th><th>Product Name</th><th>Quantity</th><th>Price</th><th>Subtotal</th><th></th></tr>
    """

    total = Decimal("0.00")
    for product in product_list.values():
        product_id = escape_html(product["id"])
        product_name = escape_html(product["name"])
        quantity = int(product["quantity"])
        price = format_currency(product["price"])
        subtotal = Decimal(str(product["price"])) * quantity
        total += subtotal

        # One row per product: a quantity box with an Update button, and a Remove button
        html += f"""
  <tr>
    <td>{product_id}</td>
    <td>{product_name}</td>
    <td>
      <form method="post" action="/updatecart">
        <input type="hidden" name="id" value="{product_id}">
        <input type="number" name="quantity" min="0" max="999" value="{quantity}">
        <input type="submit" value="Update">
      </form>
    </td>
    <td>{price}</td>
    <td>{format_currency(subtotal)}</td>
        <td>
        <form method="post" action="/removecart">
            <input type="hidden" name="id" value="{product_id}">
            <input type="submit" value="Remove">
        </form>
        </td>
    </tr>
    """

    html += f"""
        <tr><td colspan="4"><strong>Order Total</strong></td><td>{format_currency(total)}</td><td></td></tr>
        </table>
        <h2><a href="/checkout">Check Out</a></h2>
        <p><a href="/listprod">Continue Shopping</a></p>
    """

    return html_page("Your Shopping Cart", html)


@bp.post("/updatecart")
def update_cart():
    product_id = request.form.get("id", "")
    quantity = request.form.get("quantity", "").strip()

    cart = dict(session.get("productList", {}))
    if product_id in cart and quantity.isdecimal():
        if int(quantity) == 0:
            del cart[product_id]
        else:
            product = dict(cart[product_id])
            product["quantity"] = min(int(quantity), 999)
            cart[product_id] = product
        session["productList"] = cart

    return redirect(url_for("showcart.show_cart"))


@bp.post("/removecart")
def remove_from_cart():
    product_id = request.form.get("id", "")

    cart = dict(session.get("productList", {}))
    if product_id in cart:
        del cart[product_id]
        session["productList"] = cart

    return redirect(url_for("showcart.show_cart"))