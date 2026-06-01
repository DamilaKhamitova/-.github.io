from flask import Flask, request, jsonify
import sqlite3
import re
import hashlib

app = Flask(__name__)
DB_PATH = '../database/damaq.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id))''')
    
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    if cursor.fetchone()[0] == 0:
        items = [
            ("Бешбармақ", "Дәстүрлі қазақ тағамы", 2500, "Негізгі"),
            ("Плов", "Өзбек плові", 1800, "Негізгі"),
            ("Манты", "Қол манты", 1500, "Негізгі"),
            ("Цезарь салаты", "Тауық еті, пармезан", 1200, "Салат"),
            ("Шай", "Қара шай", 400, "Сусын"),
        ]
        cursor.executemany('INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)', items)
    
    conn.commit()
    conn.close()

# ТІРКЕЛУ
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({'error': 'Барлық өрістер міндетті!'}), 400
    if not validate_email(email):
        return jsonify({'error': 'Email форматы дұрыс емес!'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Құпия сөз 6 символдан кем болмауы керек!'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, hash_password(password)))
        conn.commit()
        conn.close()
        return jsonify({'message': f'Тіркелу сәтті: {username}'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Бұл email тіркелген!'}), 400

# КІРУ
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                  (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'message': f'Қош келдің, {user["username"]}!'}), 200
    return jsonify({'error': 'Email немесе құпия сөз дұрыс емес!'}), 401

# МӘЗІР - барлығын алу
@app.route('/menu', methods=['GET'])
def get_menu():
    category = request.args.get('category', '')
    conn = get_db()
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT * FROM menu_items WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM menu_items')
    items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

# МӘЗІР - қосу
@app.route('/menu', methods=['POST'])
def add_menu():
    data = request.get_json()
    name = data.get('name', '')
    price = data.get('price', 0)
    category = data.get('category', '')
    description = data.get('description', '')
    
    if not name or not category:
        return jsonify({'error': 'Атау және санат міндетті!'}), 400
    if price <= 0:
        return jsonify({'error': 'Баға оң сан болуы керек!'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
                   (name, description, price, category))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Тағам қосылды: {name}'}), 201

# ТАПСЫРЫС беру
@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    user_id = data.get('user_id')
    menu_item_id = data.get('menu_item_id')
    quantity = data.get('quantity', 1)
    
    if not user_id or not menu_item_id:
        return jsonify({'error': 'user_id және menu_item_id міндетті!'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, menu_item_id, quantity) VALUES (?, ?, ?)',
                   (user_id, menu_item_id, quantity))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Тапсырыс қабылданды!'}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
