"""Question 2 (10 marks): display/search products and provide cart links."""

from flask import Blueprint, request, current_app, url_for
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("listprod", __name__)


@bp.get("/listprod")
def list_products():
    name = request.args.get("productName", "")
    form = f"""
        <h1>Search for the products you want to buy:</h1>
        <form method="get" action="/listprod">
        <input type="text" name="productName" size="50" value="{escape_html(name)}">
        <input type="submit" value="Submit">
        <input type="reset" value="Reset">
        (Leave blank for all products)
        </form>
    """

    connection = None
    try:
        # TODO (Q2): Open a connection with get_connection().
        connection = get_connection()
        cursor = connection.cursor()

        # TODO: Query product; if name is not blank, use productName LIKE ?.
        #       Bind the search value as a parameter, e.g. f"%{name}%".
        #       If name is blank, return all products.
        sql = "SELECT productId, productName, productPrice FROM product WHERE 1=1"
        params = []
        has_name = name is not None and name.strip() != ""
        if has_name:
            sql += " AND productName LIKE ?"
            params.append(f"%{name}%")
        cursor.execute(sql, params)

        # TODO: Display a table with product ID, name, and formatted price.
        if has_name:
            heading = "Products containing '" + escape_html(name) + "'"
        else:
            heading = "All Products"

        html = f"""
            <h2>{heading}</h2>
            <table border="1">
            <tr><th></th><th>Product Name</th><th>Price</th></tr>
        """

        # TODO: Each product needs a link to:
        #       /addcart?id=(productId)&name=(productName)&price=(productPrice)
        #       Use flask.url_for('addcart.add_to_cart', id=..., name=..., price=...)
    #           so special characters are URL-encoded correctly.
        # Use escape_html and format_currency when displaying values.
        for product in cursor:
            link = escape_html(url_for("addcart.add_to_cart", id=product[0], name=product[1], price=str(product[2])))
           
            # Lab 8: the product name links to the product detail page
            detail_link = escape_html(url_for("product.product_details", id=product[0]))
            product_name = escape_html(product[1])
            price = format_currency(product[2])

            html += f"""
                <tr><td><a href="{link}">Add to Cart</a></td><td><a href="{detail_link}">{product_name}</a></td><td>{price}</td></tr>
            """

        html += """
            </table>
        """

        return html_page("Min and Harsh Grocery", form + html)
    
    except Exception:
        current_app.logger.exception("Unable to list products")
        return html_page("Product Search Error", form +
                         "<p>Unable to search products.</p>"), 500
    
    finally:
        # TODO (Q2): Close the connection if it was opened.
        if connection is not None:
            connection.close()