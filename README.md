# 🌿 AgriConnect - Eco-friendly Agricultural E-Commerce

AgriConnect is a full-stack agricultural marketplace that connects **Farmers**, **Customers**, and **Delivery Personnel** in one seamless ecosystem - from listing fresh produce to doorstep delivery.

The project is built as a **monolithic, server-rendered application** under strict academic constraints:

- 🚫 **No ORM** - every query is raw, hand-written `sqlite3` SQL.
- 🚫 **No REST APIs / AJAX** - no `fetch`, no `axios`, no JSON endpoints. Every interaction is a real HTML `<form>` submitted to the server.
- ✅ **Server-Side Rendering only** - Flask + Jinja2 render every page, the old-fashioned, transparent way.

This makes the entire request/response cycle easy to trace end-to-end for a viva/defense: one click → one `POST` → one SQL statement → one rendered page.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3 |
| **Web Framework** | Flask (server-side rendering, no REST layer) |
| **Database** | Raw `sqlite3` - no SQLAlchemy, no ORM of any kind |
| **Templating** | HTML5 + Jinja2 |
| **Styling** | Tailwind CSS (via CDN) - glassmorphism cards, gradients, responsive layouts |
| **Auth** | Flask `session` + salted `hashlib.pbkdf2_hmac` password hashing (stdlib only) |
| **Deployment** | Gunicorn, ready for Render / Heroku-style platforms |

---

## ✨ Core Features

- 🔐 **Role-Based Access** - four distinct dashboards for **Admin**, **Farmer**, **Customer**, and **Delivery Rider**, each with its own permissions and views.
- 🏬 **Inventory & Shop Management** - farmers create a shop and list items with price, stock, category, and real-world **units** (kg, grams, litres, pieces, dozen), plus custom category names.
- 🤝 **Custom Pre-Order System** - customers can negotiate a price on an existing item, or request something entirely outside the catalog. Once a farmer accepts, it's automatically bridged into a real order and delivery pipeline.
- 🛒 **Cart & Checkout** - a full shopping cart with quantity management, coupon codes (`DISCOUNT10` for 10% off), and multiple payment methods (bKash, Card, Cash on Delivery).
- 🚚 **Delivery Tracking** - a live order lifecycle: `Pending → Ready → In Transit → Delivered`, with rider accept/complete actions and customer-side cancellation & cancel-request flows.
- 🔔 **Dismissible Notifications** - real-time-feeling alerts for new orders, pre-order responses, and delivery updates, each with a one-click ✕ dismiss.
- 📊 **Admin Analytics** - deep drill-down views into every shop's inventory, every customer's order history, every rider's delivery log, and system-wide pre-order requests.
- ⭐ **Ratings & Reviews** - customers rate both the shop and the delivery rider after a completed order, with live-recomputed averages.

---

## 💻 How to Run Locally (macOS/Linux)

```bash
# 1. Clone the repository
git clone < Repository URL>
cd AgriConnect_Project/simple_app

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database (creates agriconnect.db with all tables)
python3 db.py

# 6. Run the app
python3 app.py
```

The app will be live at **http://127.0.0.1:5001**  

---

## 🪟 How to Run Locally (Windows)

```cmd
:: 1. Clone the repository
git clone < Repository URL>
cd AgriConnect_Project\simple_app

:: 2. Create a virtual environment
python -m venv venv

:: 3. Activate it
venv\Scripts\activate

:: 4. Install dependencies
pip install -r requirements.txt

:: 5. Initialize the database (creates agriconnect.db with all tables)
python db.py

:: 6. Run the app
python app.py
```

The app will be live at **http://127.0.0.1:5001**  

> 💡 **Tip:** Copy `.env.example` to `.env` and set your own `SECRET_KEY` before running in anything beyond local testing.
