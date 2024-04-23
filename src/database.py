import dotenv
import os
dotenv.load_dotenv()
from flask_mysqldb import MySQL
import uuid
import MySQLdb

db_instance = None

def init_db(app):
    global db_instance
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
    app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
    db_instance = MySQL(app)
    
def get_cursor():
    return db_instance.connection.cursor()
    

def create_bakpao(bakpao_name, bakpao_price):
    cursor = get_cursor()
    try:
        query = "INSERT INTO `bakpao` (`id`, `bakpao_name`, `bakpao_price`) VALUES (%s, %s, %s)"
        cursor.execute(query, (str(uuid.uuid4()), bakpao_name, float(bakpao_price)))
        db_instance.connection.commit()
    except MySQLdb.ProgrammingError as e:
        print(f"ProgrammingError: {e}")
        db_instance.connection.rollback()
    finally:
        cursor.close()

def get_all_bakpao():
    cursor = get_cursor()
    query = "SELECT * FROM `bakpao`"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data

def create_order(initial, items):
    cursor = get_cursor()
    query1 = "INSERT INTO `transaction` (`id`,`initial`,`is_paid`) VALUES( %s, %s, %s)"
    transaction_id = str(uuid.uuid4())
    print(initial)
    cursor.execute(query1, (transaction_id, str(initial), False))
    db_instance.connection.commit()
    cursor.close()
    create_order_details(items, transaction_id)

def create_order_details(items, transaction_id):
    query = "INSERT INTO `transaction_details` (`transaction_id`,`bakpao_id`, `quantity`) VALUES(%s,%s,%s)"
    cursor = get_cursor()
    print(items)
    for item in items:
        print(item)
        cursor.execute(query, (transaction_id, item["bakpao_id"], str(item["qty"])))
        db_instance.connection.commit()
    cursor.close()

def get_all_order():
    query = "SELECT * FROM transaction tr JOIN transaction_details trd ON tr.id = trd.transaction_id JOIN bakpao bp ON trd.bakpao_id = bp.id"
    cursor = get_cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data

    
    
def group_orders(transactions):
    grouped_transactions = {}
    for transaction in transactions:
        transaction_id = transaction[0]
        if transaction_id not in grouped_transactions:
            grouped_transactions[transaction_id] = {
                'initial': transaction[1],
                'is_paid': transaction[2],
                'transactions': [],
                'total' : 0
                
            }
        grouped_transactions[transaction_id]['transactions'].append({
            "bakpao_id": transaction[4],
            'bakpao_name': transaction[7],
            'quantity': transaction[5],
            'bakpao_price': transaction[8]
        })
        grouped_transactions[transaction_id]['total'] += transaction[5] * transaction[8]
    return grouped_transactions

def total_order(transactions):
    bapaos = get_all_bakpao()
    total_order = {bapao[1]: 0 for bapao in bapaos}
    for transaction in transactions:
        total_order[transaction[7]] += transaction[5]
    return total_order

def update_paid_status(transaction_id, status):
    cursor = get_cursor()
    query = "UPDATE transaction tr JOIN transaction_details trd ON tr.id = trd.transaction_id SET tr.is_paid = %s WHERE tr.id = %s"
    
    cursor.execute(query, (status, transaction_id))
    db_instance.connection.commit()
    cursor.close()

# DELETE trd FROM transaction_details trd JOIN transaction tr ON tr.id = trd.transaction_id WHERE tr.initial = "LA"

# DELETE tr from transaction tr WHERE tr.initial = "LA"
    
    
    