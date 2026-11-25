"""COSC 304 web store — Lab 7 plus Lab 8 routes (Flask)."""

import os

from flask import Flask, render_template, session

from routes import (addcart, checkout, listorder, listprod, loaddata,
                    order, showcart)
from routes import (admin, customer, display_image, login, logout,
                    product, ship, validate_login)

# The Lab 7 views directory now contains a dynamic Jinja home page.
app = Flask(__name__, template_folder="views")
# Only for local course development; production keys must be private/random.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "cosc304-local-lab-session-secret")


@app.get("/")
def index():
    return render_template("index.html", user_name=session.get("authenticatedUser"))


for module in (loaddata, listorder, listprod, addcart, showcart, checkout, order,
               login, validate_login, logout, product, display_image,
               admin, customer, ship):
    app.register_blueprint(module.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=True)
