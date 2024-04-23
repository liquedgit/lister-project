from flask import Flask
from flask import render_template, request, session, redirect,url_for, jsonify
from database import init_db, create_bakpao, get_all_bakpao,create_order, get_all_order, group_orders,total_order, update_paid_status
import dotenv
import secrets
import os
import time

app = Flask(__name__)
init_db(app)
dotenv.load_dotenv()
app.secret_key = secrets.token_hex()

admin_password = os.getenv("ADMIN_PASSWORD")
print(admin_password)

@app.route("/", methods=["GET"])
def view_order():
    if request.method == "GET":
        bakpaos = get_all_bakpao()
        raw_data = get_all_order()
        orders = group_orders(raw_data)
        total = total_order(raw_data)
        return render_template("guest.html", bakpaos=bakpaos, orders=orders, total=total)

@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    elif request.method == "POST":
        form_data = request.form
        pw = form_data.get("password")
        if pw == admin_password:
            session["logged_in"] = True
            return redirect(url_for("view_order"), 302)
            

@app.route("/bakpao", methods=["GET", "POST"])
def bakpao():
    if request.method == "GET":
        bakpaos = get_all_bakpao()
        print(bakpaos)
        return render_template("bakpao.html", bakpaos=bakpaos)
    elif request.method == "POST" and session.get("logged_in") == True:
        bakpao_name = request.form["bakpao_name"]
        bakpao_price = request.form["bakpao_price"]
        print(int(bakpao_price))
        create_bakpao(bakpao_name, bakpao_price)
        return redirect(url_for("bakpao"))
    
@app.route("/order", methods=["POST", "PATCH"])
def order():
    if request.method == "POST" and session.get("logged_in") == True:
        data = request.json
        initial = data['initial']
        if len(initial) >=2:
            create_order(initial, data["items"])
            return jsonify({'message':"Order created succesfully"})
        else:
            return jsonify({"message":"Please send initial"})
    elif request.method == "PATCH" and session.get("logged_in") == True:
        data = request.json
        print(data)
        update_paid_status(data["transaction_id"], data["status"])
        return jsonify({"message":"Succesfully paid"})