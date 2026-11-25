"""Lab 8 TODO: product details with URL and database images."""

from flask import Blueprint, request, url_for, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("product", __name__)


@bp.get("/product")
def product_details():
    product_id_text = request.args.get("id", "")

    # TODO: Validate that id is a positive integer product ID.
    if not product_id_text.isdecimal() or int(product_id_text) <= 0:
        return html_page("Product Details", """
            <h1>Invalid product ID</h1>
            <p><a href="/listprod">Continue Shopping</a> </p>
        """), 400

    product_id = int(product_id_text)

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # TODO: Query product by ID using a parameterized SQL query.
        #       Retrieve productId, productName, productPrice, productDesc,
        #       productImageURL, and whether productImage is present.
        sql = ("SELECT productId, productName, productPrice, productDesc, productImageURL, "
               "CASE WHEN productImage IS NULL THEN 0 ELSE 1 END "
               "FROM product WHERE productId = ?")
        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()

        # TODO: Handle an invalid ID or a product not found.
        if product is None:
            return html_page("Product Details", """
                <h1>Product not found</h1>
                <p><a href="/listprod">Continue Shopping</a> </p>
            """), 404

        # TODO: Display the name, price and description, escaping HTML text.
        name = escape_html(product[1])
        price = format_currency(product[2])
        description = escape_html(product[3]) if product[3] is not None else ""

        html = f"""
            <h1>{name}</h1>
            <table>
            <tr><td>ID:</td><td>{product[0]}</td></tr>
            <tr><td>Price:</td><td>{price}</td></tr>
            </table>
            <p>{description}</p>
        """

        # TODO: For productImageURL (e.g. img/1.jpg), build an HTML <img> tag.
        #       The new local files are served from /static/img/1.jpg, etc.
        image_url = product[4]
        if image_url is not None and image_url.strip() != "":
            html += f"""
                <img src="/static/{escape_html(image_url)}" alt="{name}">
            """

        # TODO: For a database image, set <img src="/displayImage?id=...">.
        if product[5] == 1:
            image_link = escape_html(url_for("display_image.display_image", id=product[0]))
            html += f"""
                <img src="{image_link}" alt="{name}">
            """

        # TODO: Add a link to Lab 7's /addcart route with id, name, price.
        #       Flask's url_for() safely URL-encodes query parameters.
        cart_link = escape_html(url_for("addcart.add_to_cart", id=product[0],
                                       name=product[1], price=str(product[2])))
        html += f"""
            <h3><a href="{cart_link}">Add to Cart</a></h3>
            <h3><a href="/listprod">Continue Shopping</a></h3>
            <h3><a href="/">Main Page</a></h3>
        """

        return html_page("Product Details", html)
    except Exception:
        current_app.logger.exception("Error displaying product details")
        return html_page("Product Details", """
            <h1>Error displaying product details</h1>
            <p><a href="/listprod">Continue Shopping</a></p>
        """), 500
    finally:
        if connection is not None:
            connection.close()
