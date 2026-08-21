import sqlite3

DB_NAME = "agriconnect.db"


def get_db():
    # one connection per call, rows come back like dicts so we can do row["Name"]
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # shop has to exist before farmer/items can point to it
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Shop (
            ShopID INTEGER PRIMARY KEY,
            ShopName TEXT NOT NULL,
            Review FLOAT DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Customer (
            UserCustomerID INTEGER PRIMARY KEY,
            password TEXT NOT NULL,
            Address TEXT,
            Phone TEXT,
            Name TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Farmer (
            UserFarmerID INTEGER PRIMARY KEY,
            password TEXT NOT NULL,
            Address TEXT,
            Phone TEXT,
            Name TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Bio TEXT,
            ShopID INTEGER,
            FOREIGN KEY (ShopID) REFERENCES Shop (ShopID)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS DeliveryMan (
            UserDeliveryManID INTEGER PRIMARY KEY,
            password TEXT NOT NULL,
            Address TEXT,
            Phone TEXT,
            Name TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Review FLOAT DEFAULT 0,
            TotalDeliveries INTEGER DEFAULT 0,
            VehicleNo TEXT
        )
    """)

    # "Order" is a reserved word in SQL so it needs quotes everywhere it's used.
    # "Total amount" isn't a valid column name either, same fix as the old backend: TotalAmount
    # ShopRating stays NULL until the customer rates a delivered order
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "Order" (
            OrderID INTEGER PRIMARY KEY,
            TotalAmount FLOAT NOT NULL,
            CouponCode TEXT,
            InvoiceDate TEXT,
            InvoiceID TEXT,
            PaymentStatus TEXT,
            OrderDate TEXT,
            PaymentMethod TEXT,
            Status TEXT,
            ShopRating INTEGER DEFAULT NULL,
            UserCustomerID INTEGER,
            FOREIGN KEY (UserCustomerID) REFERENCES Customer (UserCustomerID)
        )
    """)

    # same deal here, "Fruits & Vegetables" -> FruitsAndVegetables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            ItemID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Price FLOAT NOT NULL,
            Stock INTEGER DEFAULT 0,
            FruitsAndVegetables BOOLEAN DEFAULT 0,
            Grains BOOLEAN DEFAULT 0,
            Meat BOOLEAN DEFAULT 0,
            ShopID INTEGER,
            OrderID INTEGER,
            FOREIGN KEY (ShopID) REFERENCES Shop (ShopID),
            FOREIGN KEY (OrderID) REFERENCES "Order" (OrderID)
        )
    """)

    # DeliveryRating stays NULL until the customer rates a completed delivery
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Delivery (
            DeliveryID INTEGER PRIMARY KEY,
            PickedUpTime TEXT,
            Status TEXT,
            DeliveryRating INTEGER DEFAULT NULL,
            UserDeliveryManID INTEGER,
            OrderID INTEGER,
            FOREIGN KEY (UserDeliveryManID) REFERENCES DeliveryMan (UserDeliveryManID),
            FOREIGN KEY (OrderID) REFERENCES "Order" (OrderID)
        )
    """)

    # points at a Shop rather than a specific Farmer - same as Items, the
    # farmer running it is found through Farmer.ShopID when needed.
    # ItemID is nullable on purpose - a customer can ask for something that
    # isn't in the catalog yet, and CustomItemName carries the name for that case
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PreOrderRequest (
            PreOrderID INTEGER PRIMARY KEY,
            ProposedPrice FLOAT NOT NULL,
            Quantity INTEGER NOT NULL,
            Status TEXT,
            RequestDate TEXT,
            UserCustomerID INTEGER,
            ShopID INTEGER,
            ItemID INTEGER,
            CustomItemName TEXT,
            FOREIGN KEY (UserCustomerID) REFERENCES Customer (UserCustomerID),
            FOREIGN KEY (ShopID) REFERENCES Shop (ShopID),
            FOREIGN KEY (ItemID) REFERENCES Items (ItemID)
        )
    """)

    # UserID's meaning depends on Role (Farmer #1 and Customer #1 are different
    # people), so no single FK here - it's a compound key by design, same as
    # how session["user_id"] + session["role"] already work together in app.py
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Notification (
            NotificationID INTEGER PRIMARY KEY,
            UserID INTEGER NOT NULL,
            Role TEXT NOT NULL,
            Message TEXT NOT NULL,
            IsRead BOOLEAN DEFAULT 0,
            CreatedAt TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("db ready")


# run this file on its own to set up the db: python db.py
if __name__ == "__main__":
    init_db()
