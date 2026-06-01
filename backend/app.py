import sqlite3

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

# CREATE - қосу
def add_menu_item(name, description, price, category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO menu_items (name, description, price, category) VALUES (?, ?, ?, ?)',
                   (name, description, price, category))
    conn.commit()
    conn.close()
    print(f"Тағам қосылды: {name}")

# READ - оқу
def get_all_menu_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu_items')
    items = cursor.fetchall()
    conn.close()
    return items

# UPDATE - жаңарту
def update_menu_item(id, price):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE menu_items SET price = ? WHERE id = ?', (price, id))
    conn.commit()
    conn.close()
    print(f"Баға жаңартылды!")

# DELETE - өшіру
def delete_menu_item(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM menu_items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    print(f"Тағам өшірілді!")

# Тест
init_db()
add_menu_item("Бешбармақ", "Дәстүрлі қазақ тағамы", 2500, "Негізгі тағам")
add_menu_item("Плов", "Өзбек плові", 1800, "Негізгі тағам")
add_menu_item("Цезарь салаты", "Тауық еті, пармезан", 1200, "Салат")

print("\n--- Барлық тағамдар ---")
items = get_all_menu_items()
for item in items:
    print(f"{item['id']}. {item['name']} - {item['price']} ₸")

update_menu_item(1, 2800)
print("\nБешбармақ бағасы жаңартылды: 2800 ₸")

delete_menu_item(3)
print("Цезарь салаты өшірілді")

print("\n--- Жаңартылған тізім ---")
items = get_all_menu_items()
for item in items:
    print(f"{item['id']}. {item['name']} - {item['price']} ₸")
