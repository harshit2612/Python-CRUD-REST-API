import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
app = Flask(__name__)

SECRET_KEY = ""
DATABASE = 'database.db'

# -----------------
# Database Helper
# -----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#---------------------------------
#Initialize Database
#---------------------------------
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT NOT NULL,
        salary INTEGER,
        phone TEXT
        )
    ''')

    #User table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

#JWT Functions
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": (datetime.now(timezone.utc) + timedelta(hours=2)).timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data["user_id"]
    except:
        return None

#Auth Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return {"message":"Token Missing"}, 401

        try:
            parts = auth_header.split(" ")
            if len(parts) != 2:
                return {"message": "Invalid header format: (Use Bearer <token>)"}, 401

            token = parts[1]
            user_id = verify_token(token)
            
            if not user_id:
                return {"message": "Invalid/Expired token"},401
        except:
            return {"message":"Invalid token format"}, 401

        return f(*args, **kwargs)

    return decorated

#Auth Routes
@app.route('/register', methods=["POST"])
def register():
    data= request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"message": "Username and Password are required"}, 400

    hashed_password = generate_password_hash(password)
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                       (username,hashed_password))
        conn.commit()
        return {"message":"User registered successfully"}, 201
    except sqlite3.IntegrityError:
        return {"message":"User already exists"}, 400
    except Exception as e:
        return {"message": f"Databsae Error : {str(e)}"}, 500
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
    user= cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"],data["password"]):
        token = generate_token(user["id"])
        return {"token":token}

    return {"message":"Invalid credentials"}, 401


#-------------------------
#Creating Employee
#--------------------------------
@app.route('/employees', methods=['POST'])
@token_required
def create_employees():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get('name')
    designation = data.get('designation', 'Not Assigned')
    salary = data.get('salary', 0)
    phone = data.get('phone', '')

    if not name:
        return {"message": "Employee name is required"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, designation,salary, phone) VALUES (?,?,?,?)",
            (data['name'],data['designation'],data['salary'],data['phone'])
        )
        conn.commit()
        return jsonify({"message": "Employee created"}), 201
    except Exception as e:
        return jsonify({"message":"Failed to create employee"}), 500
    finally:
        conn.close()


#----------------------
#Read All Employee
#---------------------
@app.route('/employees',methods=['GET'])
@token_required
def get_employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return jsonify([dict(emp) for emp in employees])

#-----------------------
#Read Single Employee
#-----------------------
@app.route('/employees/<int:id>',methods=['GET'])
@token_required
def get_employee(id):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM employees WHERE id=?",(id,)).fetchone()
    conn.close()

    if employee is None:
        return jsonify({"error":"Not found"}), 404

    return jsonify(dict(employee))

#----------------------
#Update Employee
#---------------------
@app.route('/employees/<int:id>',methods=['PUT'])
@token_required
def update_employee(id):
    conn = get_db_connection()
    data = request.get_json()
        
    conn.execute(
        "UPDATE employess SET name=?, designation=?, salary=?, phone=?, WHERE id=?",
    (data['name'],data['designation'],data['salary'],data['phone'],id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message":"Employee updated"})

#--------------------
#Delete Employee
#--------------------
@app.route('/employees/<int:id>',methods=['DELETE'])
@token_required
def delete_employee(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM employees WHERE id=?",(id,))
    conn.commit()
    conn.close()

    return jsonify({"message":"Employee deleted"})

#---------------------
#Run the application
#---------------------
if __name__ == '__main__':
    app.run(debug=True)
