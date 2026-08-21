import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from db import get_db, init_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-this")

# make sure tables exist before we handle any requests
init_db()

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

# Items stores category as three separate columns, not one field.
# this maps the dropdown value to the column that should get flipped on.
CATEGORY_COLUMNS = {
    "Fruits & Vegetables": "FruitsAndVegetables",
    "Grains": "Grains",
    "Meat": "Meat",
}

# most sections are a flat table (generic rendering in admin_details.html).
# shops/customers/deliverymen/preorders need a real drill-down so those get
# their own "type" and their own query-building code below instead of one
# single query string.
ADMIN_SECTIONS = {
    "farmers": {
        "title": "All Farmers",
        "type": "flat",
        "query": "SELECT UserFarmerID AS ID, Name, Email, Phone, Address, Bio, ShopID FROM Farmer",
    },
    "customers": {
        "title": "All Customers",
        "type": "customers",
    },
    "deliverymen": {
        "title": "All Delivery People",
        "type": "deliverymen",
    },
    "shops": {
        "title": "All Shops",
        "type": "shops",
    },
    "orders": {
        "title": "All Orders",
        "type": "flat",
        "query": """SELECT "Order".OrderID AS ID, "Order".Status, "Order".TotalAmount, "Order".OrderDate,
                            "Order".ShopRating, Items.Name AS ItemName, Customer.Name AS CustomerName
                     FROM "Order"
                     LEFT JOIN Items ON Items.OrderID = "Order".OrderID
                     LEFT JOIN Customer ON Customer.UserCustomerID = "Order".UserCustomerID
                     ORDER BY "Order".OrderDate DESC""",
    },
    "preorders": {
        "title": "All Pre-Order Requests",
        "type": "preorders",
    },
}


def add_notification(conn, user_id, role, message):
    # small helper so place_order/complete_delivery don't repeat this insert
    conn.execute(
        "INSERT INTO Notification (UserID, Role, Message, IsRead, CreatedAt) VALUES (?, ?, ?, 0, ?)",
        (user_id, role, message, datetime.now().isoformat()),
    )


def hash_password(password):
    # salted hash, stdlib only, no extra package needed
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return salt.hex() + "$" + digest.hex()


def check_password(password, stored_hash):
    # compare a plain password against what hash_password produced
    salt_hex, digest_hex = stored_hash.split("$")
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return hmac.compare_digest(actual, expected)


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form.get("phone")
        address = request.form.get("address")
        hashed = hash_password(password)

        conn = get_db()
        try:
            if role == "Farmer":
                # insert into farmer table
                conn.execute(
                    "INSERT INTO Farmer (password, Address, Phone, Name, Email) VALUES (?, ?, ?, ?, ?)",
                    (hashed, address, phone, name, email),
                )
            elif role == "Customer":
                # insert into customer table
                conn.execute(
                    "INSERT INTO Customer (password, Address, Phone, Name, Email) VALUES (?, ?, ?, ?, ?)",
                    (hashed, address, phone, name, email),
                )
            elif role == "DeliveryMan":
                # insert into delivery man table, review/deliveries start at 0
                conn.execute(
                    """INSERT INTO DeliveryMan (password, Address, Phone, Name, Email, Review, TotalDeliveries)
                       VALUES (?, ?, ?, ?, ?, 0, 0)""",
                    (hashed, address, phone, name, email),
                )
            else:
                flash("Please pick a valid role.", "error")
                return redirect(url_for("register"))

            conn.commit()
        except sqlite3.IntegrityError:
            # email is UNIQUE, this means it's already taken
            flash("That email is already registered.", "error")
            return redirect(url_for("register"))
        finally:
            conn.close()

        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # hardcoded admin, no table for this one
        if email == ADMIN_EMAIL and hmac.compare_digest(password, ADMIN_PASSWORD):
            session["user_id"] = 0
            session["name"] = "Administrator"
            session["role"] = "Admin"
            return redirect(url_for("dashboard"))

        conn = get_db()

        # check farmer table
        farmer = conn.execute("SELECT * FROM Farmer WHERE Email = ?", (email,)).fetchone()
        if farmer and check_password(password, farmer["password"]):
            session["user_id"] = farmer["UserFarmerID"]
            session["name"] = farmer["Name"]
            session["role"] = "Farmer"
            conn.close()
            return redirect(url_for("dashboard"))

        # check customer table
        customer = conn.execute("SELECT * FROM Customer WHERE Email = ?", (email,)).fetchone()
        if customer and check_password(password, customer["password"]):
            session["user_id"] = customer["UserCustomerID"]
            session["name"] = customer["Name"]
            session["role"] = "Customer"
            conn.close()
            return redirect(url_for("dashboard"))

        # check delivery man table
        delivery_man = conn.execute("SELECT * FROM DeliveryMan WHERE Email = ?", (email,)).fetchone()
        if delivery_man and check_password(password, delivery_man["password"]):
            session["user_id"] = delivery_man["UserDeliveryManID"]
            session["name"] = delivery_man["Name"]
            session["role"] = "DeliveryMan"
            conn.close()
            return redirect(url_for("dashboard"))

        conn.close()
        flash("Wrong email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session["role"]
    conn = get_db()
    context = {}

    if role == "Admin":
        # just counts for the overview cards
        context["farmer_count"] = conn.execute("SELECT COUNT(*) FROM Farmer").fetchone()[0]
        context["customer_count"] = conn.execute("SELECT COUNT(*) FROM Customer").fetchone()[0]
        context["delivery_count"] = conn.execute("SELECT COUNT(*) FROM DeliveryMan").fetchone()[0]
        context["shop_count"] = conn.execute("SELECT COUNT(*) FROM Shop").fetchone()[0]
        context["order_count"] = conn.execute('SELECT COUNT(*) FROM "Order"').fetchone()[0]
        context["preorder_count"] = conn.execute("SELECT COUNT(*) FROM PreOrderRequest").fetchone()[0]

    elif role == "Customer":
        # left join so shops with no farmer attached still show up
        context["shops"] = conn.execute("""
            SELECT Shop.ShopID, Shop.ShopName, Shop.Review, Farmer.Name AS FarmerName
            FROM Shop
            LEFT JOIN Farmer ON Farmer.ShopID = Shop.ShopID
        """).fetchall()

        # this customer's past orders, with what item/shop they bought from,
        # plus ratings so the template knows whether to show a rating form
        context["orders"] = conn.execute("""
            SELECT "Order".OrderID, "Order".Status, "Order".TotalAmount, "Order".OrderDate, "Order".ShopRating,
                   Items.Name AS ItemName, Shop.ShopName AS ShopName,
                   Delivery.DeliveryRating AS DeliveryRating
            FROM "Order"
            LEFT JOIN Items ON Items.OrderID = "Order".OrderID
            LEFT JOIN Shop ON Shop.ShopID = Items.ShopID
            LEFT JOIN Delivery ON Delivery.OrderID = "Order".OrderID
            WHERE "Order".UserCustomerID = ?
            ORDER BY "Order".OrderDate DESC
        """, (session["user_id"],)).fetchall()

        context["notifications"] = conn.execute(
            "SELECT * FROM Notification WHERE UserID = ? AND Role = 'Customer' AND IsRead = 0 ORDER BY CreatedAt DESC",
            (session["user_id"],),
        ).fetchall()

    elif role == "Farmer":
        # shop points back to the farmer via Farmer.ShopID, not the other way round
        farmer = conn.execute(
            "SELECT ShopID FROM Farmer WHERE UserFarmerID = ?", (session["user_id"],)
        ).fetchone()

        shop = None
        items = []
        orders = []
        earnings = 0
        preorders = []
        if farmer and farmer["ShopID"]:
            shop = conn.execute("SELECT * FROM Shop WHERE ShopID = ?", (farmer["ShopID"],)).fetchone()
            items = conn.execute("SELECT * FROM Items WHERE ShopID = ?", (farmer["ShopID"],)).fetchall()

            # orders that touched this shop's items, with item name + who bought it
            orders = conn.execute("""
                SELECT "Order".OrderID, "Order".Status, "Order".TotalAmount,
                       Items.Name AS ItemName, Items.Price AS ItemPrice,
                       Customer.Name AS CustomerName
                FROM "Order"
                JOIN Items ON Items.OrderID = "Order".OrderID
                JOIN Customer ON Customer.UserCustomerID = "Order".UserCustomerID
                WHERE Items.ShopID = ?
                ORDER BY "Order".OrderDate DESC
            """, (farmer["ShopID"],)).fetchall()

            # TotalAmount already is Price * Quantity from checkout, so summing
            # it for delivered orders is the same as summing Quantity * Price
            earnings = conn.execute("""
                SELECT COALESCE(SUM("Order".TotalAmount), 0) FROM "Order"
                JOIN Items ON Items.OrderID = "Order".OrderID
                WHERE Items.ShopID = ? AND "Order".Status = 'Delivered'
            """, (farmer["ShopID"],)).fetchone()[0]

            # pre-order requests customers have sent in for this shop.
            # left join since a custom request has no ItemID at all
            preorders = conn.execute("""
                SELECT PreOrderRequest.PreOrderID, PreOrderRequest.ProposedPrice, PreOrderRequest.Quantity,
                       PreOrderRequest.Status, PreOrderRequest.CustomItemName,
                       Customer.Name AS CustomerName, Items.Name AS ItemName
                FROM PreOrderRequest
                JOIN Customer ON Customer.UserCustomerID = PreOrderRequest.UserCustomerID
                LEFT JOIN Items ON Items.ItemID = PreOrderRequest.ItemID
                WHERE PreOrderRequest.ShopID = ?
                ORDER BY PreOrderRequest.RequestDate DESC
            """, (farmer["ShopID"],)).fetchall()

        context["shop"] = shop
        context["items"] = items
        context["orders"] = orders
        context["earnings"] = earnings
        context["preorders"] = preorders

        context["notifications"] = conn.execute(
            "SELECT * FROM Notification WHERE UserID = ? AND Role = 'Farmer' AND IsRead = 0 ORDER BY CreatedAt DESC",
            (session["user_id"],),
        ).fetchall()

    elif role == "DeliveryMan":
        # orders a farmer has marked ready, nobody's picked them up yet
        context["available_orders"] = conn.execute("""
            SELECT "Order".OrderID, "Order".TotalAmount,
                   Items.Name AS ItemName, Shop.ShopName AS ShopName,
                   Customer.Name AS CustomerName, Customer.Address AS CustomerAddress
            FROM "Order"
            JOIN Items ON Items.OrderID = "Order".OrderID
            JOIN Shop ON Shop.ShopID = Items.ShopID
            JOIN Customer ON Customer.UserCustomerID = "Order".UserCustomerID
            WHERE "Order".Status = 'Ready'
            ORDER BY "Order".OrderDate ASC
        """).fetchall()

        # this delivery person's own orders that are still in transit
        context["my_deliveries"] = conn.execute("""
            SELECT "Order".OrderID, "Order".TotalAmount,
                   Items.Name AS ItemName, Shop.ShopName AS ShopName,
                   Customer.Name AS CustomerName, Customer.Address AS CustomerAddress
            FROM Delivery
            JOIN "Order" ON "Order".OrderID = Delivery.OrderID
            JOIN Items ON Items.OrderID = "Order".OrderID
            JOIN Shop ON Shop.ShopID = Items.ShopID
            JOIN Customer ON Customer.UserCustomerID = "Order".UserCustomerID
            WHERE Delivery.UserDeliveryManID = ? AND Delivery.Status = 'In Transit'
            ORDER BY "Order".OrderDate ASC
        """, (session["user_id"],)).fetchall()

    conn.close()
    return render_template("dashboard.html", **context)


@app.route("/create_shop", methods=["POST"])
def create_shop():
    if session.get("role") != "Farmer":
        flash("Only farmers can create a shop.", "error")
        return redirect(url_for("dashboard"))

    shop_name = request.form["shop_name"]

    conn = get_db()
    # insert the shop, then point this farmer at it (Shop has no FarmerID column,
    # the link lives on Farmer.ShopID instead)
    cur = conn.execute("INSERT INTO Shop (ShopName, Review) VALUES (?, 0)", (shop_name,))
    new_shop_id = cur.lastrowid
    conn.execute("UPDATE Farmer SET ShopID = ? WHERE UserFarmerID = ?", (new_shop_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Shop created!", "success")
    return redirect(url_for("dashboard"))


@app.route("/add_item", methods=["POST"])
def add_item():
    if session.get("role") != "Farmer":
        flash("Only farmers can add items.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()

    farmer = conn.execute(
        "SELECT ShopID FROM Farmer WHERE UserFarmerID = ?", (session["user_id"],)
    ).fetchone()
    if not farmer or not farmer["ShopID"]:
        conn.close()
        flash("Create a shop before adding items.", "error")
        return redirect(url_for("dashboard"))

    category = request.form["category"]
    column = CATEGORY_COLUMNS.get(category)
    if not column:
        conn.close()
        flash("Please pick a valid category.", "error")
        return redirect(url_for("dashboard"))

    name = request.form["name"]
    price = request.form["price"]
    stock = request.form["stock"]

    # column name comes from the CATEGORY_COLUMNS map above, never straight from
    # the form, so this is safe even though it's not a normal ? placeholder
    conn.execute(
        f"INSERT INTO Items (Name, Price, Stock, {column}, ShopID) VALUES (?, ?, ?, 1, ?)",
        (name, price, stock, farmer["ShopID"]),
    )
    conn.commit()
    conn.close()

    flash("Item added!", "success")
    return redirect(url_for("dashboard"))


@app.route("/shop/<int:shop_id>")
def shop_details(shop_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    shop = conn.execute("SELECT * FROM Shop WHERE ShopID = ?", (shop_id,)).fetchone()
    if not shop:
        conn.close()
        flash("Shop not found.", "error")
        return redirect(url_for("dashboard"))

    items = conn.execute("SELECT * FROM Items WHERE ShopID = ?", (shop_id,)).fetchall()
    conn.close()

    return render_template("shop_details.html", shop=shop, items=items)


@app.route("/place_order", methods=["POST"])
def place_order():
    if session.get("role") != "Customer":
        flash("Only customers can place orders.", "error")
        return redirect(url_for("dashboard"))

    item_id = request.form["item_id"]
    shop_id = request.form["shop_id"]
    quantity = int(request.form["quantity"])

    conn = get_db()
    item = conn.execute("SELECT * FROM Items WHERE ItemID = ?", (item_id,)).fetchone()

    # Items.OrderID is a one-to-one link (no separate line-item table in this
    # schema), so once an item is linked to an order it's off the market -
    # think of it as one listing sold in a single batch, not a shared pool.
    if not item or item["OrderID"] is not None:
        conn.close()
        flash("That item is no longer available.", "error")
        return redirect(url_for("shop_details", shop_id=shop_id))

    if quantity < 1 or quantity > item["Stock"]:
        conn.close()
        flash("Not enough stock for that quantity.", "error")
        return redirect(url_for("shop_details", shop_id=shop_id))

    total_price = item["Price"] * quantity

    cur = conn.execute(
        """INSERT INTO "Order" (TotalAmount, PaymentStatus, OrderDate, Status, UserCustomerID)
           VALUES (?, 'Unpaid', ?, 'Pending', ?)""",
        (total_price, datetime.now().isoformat(), session["user_id"]),
    )
    new_order_id = cur.lastrowid

    # link the item to this order and take it out of stock
    conn.execute(
        "UPDATE Items SET OrderID = ?, Stock = Stock - ? WHERE ItemID = ?",
        (new_order_id, quantity, item_id),
    )

    # let the farmer(s) running this shop know a new order came in
    farmers = conn.execute("SELECT UserFarmerID FROM Farmer WHERE ShopID = ?", (item["ShopID"],)).fetchall()
    for f in farmers:
        add_notification(conn, f["UserFarmerID"], "Farmer", f"New order for {item['Name']} (Qty {quantity}).")

    conn.commit()
    conn.close()

    flash("Order placed!", "success")
    return redirect(url_for("dashboard"))


@app.route("/update_order_status", methods=["POST"])
def update_order_status():
    if session.get("role") != "Farmer":
        flash("Only farmers can update order status.", "error")
        return redirect(url_for("dashboard"))

    order_id = request.form["order_id"]
    conn = get_db()

    # make sure this order is actually tied to this farmer's own shop
    farmer = conn.execute(
        "SELECT ShopID FROM Farmer WHERE UserFarmerID = ?", (session["user_id"],)
    ).fetchone()
    order = conn.execute(
        """SELECT "Order".OrderID FROM "Order"
           JOIN Items ON Items.OrderID = "Order".OrderID
           WHERE "Order".OrderID = ? AND Items.ShopID = ?""",
        (order_id, farmer["ShopID"] if farmer else None),
    ).fetchone()

    if not order:
        conn.close()
        flash("Order not found.", "error")
        return redirect(url_for("dashboard"))

    conn.execute('UPDATE "Order" SET Status = ? WHERE OrderID = ?', ("Ready", order_id))
    conn.commit()
    conn.close()

    flash("Order marked as ready for pickup!", "success")
    return redirect(url_for("dashboard"))


@app.route("/accept_delivery", methods=["POST"])
def accept_delivery():
    if session.get("role") != "DeliveryMan":
        flash("Only delivery people can accept deliveries.", "error")
        return redirect(url_for("dashboard"))

    order_id = request.form["order_id"]
    conn = get_db()

    # someone else might have grabbed it first, double check it's still ready
    order = conn.execute('SELECT Status FROM "Order" WHERE OrderID = ?', (order_id,)).fetchone()
    if not order or order["Status"] != "Ready":
        conn.close()
        flash("That order isn't available anymore.", "error")
        return redirect(url_for("dashboard"))

    conn.execute(
        "INSERT INTO Delivery (PickedUpTime, Status, UserDeliveryManID, OrderID) VALUES (?, 'In Transit', ?, ?)",
        (datetime.now().isoformat(), session["user_id"], order_id),
    )
    conn.execute('UPDATE "Order" SET Status = ? WHERE OrderID = ?', ("In Transit", order_id))
    conn.commit()
    conn.close()

    flash("Delivery accepted, get it there safe!", "success")
    return redirect(url_for("dashboard"))


@app.route("/complete_delivery", methods=["POST"])
def complete_delivery():
    if session.get("role") != "DeliveryMan":
        flash("Only delivery people can complete deliveries.", "error")
        return redirect(url_for("dashboard"))

    order_id = request.form["order_id"]
    conn = get_db()

    # only let a delivery man complete a delivery that's actually theirs
    delivery = conn.execute(
        "SELECT DeliveryID FROM Delivery WHERE OrderID = ? AND UserDeliveryManID = ?",
        (order_id, session["user_id"]),
    ).fetchone()
    if not delivery:
        conn.close()
        flash("Delivery not found.", "error")
        return redirect(url_for("dashboard"))

    conn.execute("UPDATE Delivery SET Status = 'Completed' WHERE DeliveryID = ?", (delivery["DeliveryID"],))
    conn.execute('UPDATE "Order" SET Status = ? WHERE OrderID = ?', ("Delivered", order_id))
    conn.execute(
        "UPDATE DeliveryMan SET TotalDeliveries = TotalDeliveries + 1 WHERE UserDeliveryManID = ?",
        (session["user_id"],),
    )

    # tell the customer their order showed up
    order = conn.execute('SELECT UserCustomerID FROM "Order" WHERE OrderID = ?', (order_id,)).fetchone()
    add_notification(conn, order["UserCustomerID"], "Customer", "Your order has been delivered!")

    conn.commit()
    conn.close()

    flash("Delivery marked complete!", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin_details/<section>")
def admin_details(section):
    if session.get("role") != "Admin":
        flash("Only admins can view this.", "error")
        return redirect(url_for("dashboard"))

    info = ADMIN_SECTIONS.get(section)
    if not info:
        flash("Unknown section.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    rows = columns = groups = None
    section_type = info["type"]

    if section_type == "flat":
        rows = conn.execute(info["query"]).fetchall()
        # sqlite3.Row keeps column order, so this gives matching headers for free
        columns = rows[0].keys() if rows else []

    elif section_type == "shops":
        # every shop, with its own farmer and its full item catalog nested underneath
        shops = conn.execute("""
            SELECT Shop.ShopID, Shop.ShopName, Shop.Review, Farmer.Name AS FarmerName
            FROM Shop LEFT JOIN Farmer ON Farmer.ShopID = Shop.ShopID
        """).fetchall()
        groups = []
        for shop in shops:
            items = conn.execute(
                "SELECT Name, Price, Stock, OrderID FROM Items WHERE ShopID = ?",
                (shop["ShopID"],),
            ).fetchall()
            # not "items" - dict.items is a real bound method, so Jinja's
            # attribute lookup on g.items would silently return that instead
            groups.append({"shop": shop, "item_rows": items})

    elif section_type == "customers":
        # every customer with their full order history underneath
        customers = conn.execute("SELECT * FROM Customer").fetchall()
        groups = []
        for customer in customers:
            orders = conn.execute("""
                SELECT "Order".OrderID, "Order".Status, "Order".TotalAmount, "Order".OrderDate
                FROM "Order" WHERE "Order".UserCustomerID = ?
                ORDER BY "Order".OrderDate DESC
            """, (customer["UserCustomerID"],)).fetchall()
            groups.append({"customer": customer, "orders": orders})

    elif section_type == "deliverymen":
        # every delivery person with their full activity log (in transit + completed)
        deliverymen = conn.execute("SELECT * FROM DeliveryMan").fetchall()
        groups = []
        for man in deliverymen:
            deliveries = conn.execute("""
                SELECT Delivery.DeliveryID, Delivery.Status, Delivery.PickedUpTime, Delivery.DeliveryRating,
                       "Order".OrderID, "Order".TotalAmount, Shop.ShopName, Customer.Name AS CustomerName
                FROM Delivery
                JOIN "Order" ON "Order".OrderID = Delivery.OrderID
                LEFT JOIN Items ON Items.OrderID = "Order".OrderID
                LEFT JOIN Shop ON Shop.ShopID = Items.ShopID
                LEFT JOIN Customer ON Customer.UserCustomerID = "Order".UserCustomerID
                WHERE Delivery.UserDeliveryManID = ?
                ORDER BY Delivery.PickedUpTime DESC
            """, (man["UserDeliveryManID"],)).fetchall()
            groups.append({"deliveryman": man, "deliveries": deliveries})

    elif section_type == "preorders":
        # every pre-order system-wide, catalog and custom items alike
        rows = conn.execute("""
            SELECT PreOrderRequest.PreOrderID, PreOrderRequest.Status, PreOrderRequest.ProposedPrice,
                   PreOrderRequest.Quantity, PreOrderRequest.RequestDate, PreOrderRequest.CustomItemName,
                   Items.Name AS ItemName, Shop.ShopName AS ShopName, Customer.Name AS CustomerName
            FROM PreOrderRequest
            LEFT JOIN Items ON Items.ItemID = PreOrderRequest.ItemID
            LEFT JOIN Shop ON Shop.ShopID = PreOrderRequest.ShopID
            LEFT JOIN Customer ON Customer.UserCustomerID = PreOrderRequest.UserCustomerID
            ORDER BY PreOrderRequest.RequestDate DESC
        """).fetchall()

    conn.close()
    return render_template(
        "admin_details.html",
        title=info["title"],
        section_type=section_type,
        rows=rows,
        columns=columns,
        groups=groups,
    )


@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    if session.get("role") != "Customer":
        flash("Only customers can rate orders.", "error")
        return redirect(url_for("dashboard"))

    order_id = request.form["order_id"]
    shop_rating = int(request.form["shop_rating"])
    delivery_rating = int(request.form["delivery_rating"])

    if not (1 <= shop_rating <= 5) or not (1 <= delivery_rating <= 5):
        flash("Ratings must be between 1 and 5.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()

    # only the customer who placed it can rate it, and only once it's delivered
    order = conn.execute(
        'SELECT * FROM "Order" WHERE OrderID = ? AND UserCustomerID = ?',
        (order_id, session["user_id"]),
    ).fetchone()
    if not order or order["Status"] != "Delivered" or order["ShopRating"] is not None:
        conn.close()
        flash("This order can't be rated.", "error")
        return redirect(url_for("dashboard"))

    conn.execute('UPDATE "Order" SET ShopRating = ? WHERE OrderID = ?', (shop_rating, order_id))

    delivery = conn.execute("SELECT * FROM Delivery WHERE OrderID = ?", (order_id,)).fetchone()
    if delivery:
        conn.execute(
            "UPDATE Delivery SET DeliveryRating = ? WHERE DeliveryID = ?",
            (delivery_rating, delivery["DeliveryID"]),
        )

    # recompute the shop's average rating from every order rated so far
    item = conn.execute("SELECT ShopID FROM Items WHERE OrderID = ?", (order_id,)).fetchone()
    if item:
        avg_shop = conn.execute("""
            SELECT AVG("Order".ShopRating) FROM "Order"
            JOIN Items ON Items.OrderID = "Order".OrderID
            WHERE Items.ShopID = ? AND "Order".ShopRating IS NOT NULL
        """, (item["ShopID"],)).fetchone()[0]
        conn.execute("UPDATE Shop SET Review = ? WHERE ShopID = ?", (avg_shop, item["ShopID"]))

    # same deal for the delivery man's average rating
    if delivery:
        avg_delivery = conn.execute("""
            SELECT AVG(DeliveryRating) FROM Delivery
            WHERE UserDeliveryManID = ? AND DeliveryRating IS NOT NULL
        """, (delivery["UserDeliveryManID"],)).fetchone()[0]
        conn.execute(
            "UPDATE DeliveryMan SET Review = ? WHERE UserDeliveryManID = ?",
            (avg_delivery, delivery["UserDeliveryManID"]),
        )

    conn.commit()
    conn.close()

    flash("Thanks for your feedback!", "success")
    return redirect(url_for("dashboard"))


@app.route("/submit_preorder", methods=["POST"])
def submit_preorder():
    if session.get("role") != "Customer":
        flash("Only customers can send pre-order requests.", "error")
        return redirect(url_for("dashboard"))

    item_id = request.form["item_id"]
    shop_id = request.form["shop_id"]
    proposed_price = request.form["proposed_price"]
    quantity = request.form["quantity"]

    conn = get_db()

    item = conn.execute("SELECT ItemID FROM Items WHERE ItemID = ? AND ShopID = ?", (item_id, shop_id)).fetchone()
    if not item:
        conn.close()
        flash("Item not found.", "error")
        return redirect(url_for("shop_details", shop_id=shop_id))

    conn.execute(
        """INSERT INTO PreOrderRequest (ProposedPrice, Quantity, Status, RequestDate, UserCustomerID, ShopID, ItemID)
           VALUES (?, ?, 'Pending', ?, ?, ?, ?)""",
        (proposed_price, quantity, datetime.now().isoformat(), session["user_id"], shop_id, item_id),
    )

    # let the farmer(s) running this shop know a request came in
    farmers = conn.execute("SELECT UserFarmerID FROM Farmer WHERE ShopID = ?", (shop_id,)).fetchall()
    for f in farmers:
        add_notification(conn, f["UserFarmerID"], "Farmer", "New pre-order request received.")

    conn.commit()
    conn.close()

    flash("Pre-order request sent!", "success")
    return redirect(url_for("shop_details", shop_id=shop_id))


@app.route("/submit_custom_preorder", methods=["POST"])
def submit_custom_preorder():
    if session.get("role") != "Customer":
        flash("Only customers can send pre-order requests.", "error")
        return redirect(url_for("dashboard"))

    shop_id = request.form["shop_id"]
    custom_item_name = request.form["custom_item_name"]
    proposed_price = request.form["proposed_price"]
    quantity = request.form["quantity"]

    conn = get_db()

    if not conn.execute("SELECT ShopID FROM Shop WHERE ShopID = ?", (shop_id,)).fetchone():
        conn.close()
        flash("Shop not found.", "error")
        return redirect(url_for("dashboard"))

    # ItemID stays NULL here - this is a request for something not in the catalog
    conn.execute(
        """INSERT INTO PreOrderRequest
               (ProposedPrice, Quantity, Status, RequestDate, UserCustomerID, ShopID, ItemID, CustomItemName)
           VALUES (?, ?, 'Pending', ?, ?, ?, NULL, ?)""",
        (proposed_price, quantity, datetime.now().isoformat(), session["user_id"], shop_id, custom_item_name),
    )

    farmers = conn.execute("SELECT UserFarmerID FROM Farmer WHERE ShopID = ?", (shop_id,)).fetchall()
    for f in farmers:
        add_notification(conn, f["UserFarmerID"], "Farmer", f"New custom pre-order request for {custom_item_name}.")

    conn.commit()
    conn.close()

    flash("Custom item request sent!", "success")
    return redirect(url_for("shop_details", shop_id=shop_id))


@app.route("/update_preorder", methods=["POST"])
def update_preorder():
    if session.get("role") != "Farmer":
        flash("Only farmers can respond to pre-order requests.", "error")
        return redirect(url_for("dashboard"))

    preorder_id = request.form["preorder_id"]
    action = request.form["action"]

    conn = get_db()

    # make sure this request actually belongs to this farmer's own shop
    farmer = conn.execute("SELECT ShopID FROM Farmer WHERE UserFarmerID = ?", (session["user_id"],)).fetchone()
    preorder = conn.execute(
        "SELECT * FROM PreOrderRequest WHERE PreOrderID = ? AND ShopID = ?",
        (preorder_id, farmer["ShopID"] if farmer else None),
    ).fetchone()

    if not preorder:
        conn.close()
        flash("Pre-order request not found.", "error")
        return redirect(url_for("dashboard"))

    if action != "Accept":
        conn.execute("UPDATE PreOrderRequest SET Status = 'Rejected' WHERE PreOrderID = ?", (preorder_id,))
        add_notification(conn, preorder["UserCustomerID"], "Customer", "Your pre-order request was rejected.")
        conn.commit()
        conn.close()
        flash("Pre-order request rejected.", "success")
        return redirect(url_for("dashboard"))

    # accepting: bridge this into a real order so it flows through the same
    # Ready -> In Transit -> Delivered pipeline as any other order. "Order"
    # has no ItemID column - the link always runs the other way, through
    # Items.OrderID - so that's what actually connects this to the order.
    total_price = preorder["ProposedPrice"] * preorder["Quantity"]
    cur = conn.execute(
        """INSERT INTO "Order" (TotalAmount, PaymentStatus, OrderDate, Status, UserCustomerID)
           VALUES (?, 'Unpaid', ?, 'Pending', ?)""",
        (total_price, datetime.now().isoformat(), preorder["UserCustomerID"]),
    )
    new_order_id = cur.lastrowid

    if preorder["ItemID"]:
        # catalog item - claim it at the negotiated price/quantity
        item = conn.execute("SELECT Name FROM Items WHERE ItemID = ?", (preorder["ItemID"],)).fetchone()
        item_name = item["Name"] if item else "your item"
        conn.execute(
            "UPDATE Items SET OrderID = ?, Stock = Stock - ? WHERE ItemID = ?",
            (new_order_id, preorder["Quantity"], preorder["ItemID"]),
        )
    else:
        # custom item - it didn't exist in the catalog, so create it as a
        # one-off listing that's immediately fully claimed by this order
        item_name = preorder["CustomItemName"]
        conn.execute(
            "INSERT INTO Items (Name, Price, Stock, ShopID, OrderID) VALUES (?, ?, ?, ?, ?)",
            (item_name, preorder["ProposedPrice"], preorder["Quantity"], preorder["ShopID"], new_order_id),
        )

    conn.execute("UPDATE PreOrderRequest SET Status = 'Accepted' WHERE PreOrderID = ?", (preorder_id,))
    add_notification(
        conn,
        preorder["UserCustomerID"],
        "Customer",
        f"Your pre-order for {item_name} has been accepted and is being processed!",
    )

    conn.commit()
    conn.close()

    flash("Pre-order accepted and sent into processing!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
