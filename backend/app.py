import sqlite3
import re
import hashlib

DB_PATH = '../database/damaq.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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
    conn.commit()
    conn.close()

# Валидация функциялары
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_price(price):
    return isinstance(price, (int, float)) and price > 0

def validate_required(value, field_name):
    if not value or str(value).strip() == '':
        print(f"Қате: {field_name} міндетті өріс!")
        return False
    return True

# Құпия сөзді хэштеу
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Пайдаланушы қосу (валидациямен)
def add_user(username, email, password):
    if not validate_required(username, "username"):
        return False
    if not validate_required(email, "email"):
        return False
    if not validate_email(email):
        print("Қате: Email форматы дұрыс емес!")
        return False
    if len(password) < 6:
        print("Қате: Құпия сөз 6 символдан кем болмауы керек!")
        return False
    
    hashed = hash_password(password)
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, hashed))
        conn.commit()
        conn.close()
        print(f"Пайдаланушы қосылды: {username}")
        return True
    except sqlite3.IntegrityError:
        print("Қате: Бұл email тіркелген!")
        return False

# Тағам қосу (валидациямен)
def add_menu_item(name, description, price, category):
    if not validate_required(name, "name"):
        return False
    if not validate_price(price):
        print("Қате: Баға оң сан болуы керек!")
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
                   (name, description, price, category))
    conn.commit()
    conn.close()
    print(f"Тағам қосылды: {name}")
    return True

def get_all_menu_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu_items')
    items = cursor.fetchall()
    conn.close()
    return items

# Тест
init_db()

print("=== Валидация тесті ===")
print("\n1. Дұрыс пайдаланушы:")
add_user("Damila", "damila@gmail.com", "secret123")

print("\n2. Қате email:")
add_user("Aizhan", "qate-email", "pass123")

print("\n3. Қысқа құпия сөз:")
add_user("Aizhan", "aizhan@gmail.com", "123")

print("\n4. Дұрыс тағам:")
add_menu_item("Бешбармақ", "Дәстүрлі тағам", 2500, "Негізгі")

print("\n5. Теріс баға:")
add_menu_item("Плов", "Өзбек плові", -100, "Негізгі")

print("\n6. Бос атау:")
add_menu_item("", "Сипаттама", 1000, "Негізгі")

print("\n=== Тағамдар тізімі ===")
items = get_all_menu_items()
for item in items:
    print(f"{item['id']}. {item['name']} - {item['price']} ₸")
