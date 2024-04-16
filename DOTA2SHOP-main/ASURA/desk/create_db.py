import sqlite3


def create_database():
    connection = sqlite3.connect('orders.db')
    cursor = connection.cursor()

    # Создание таблицы заказов, если она еще не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_date TEXT NOT NULL,
        order_number INTEGER NOT NULL,
        order_content TEXT NOT NULL,
        total_amount REAL NOT NULL,
        pickup_point TEXT NOT NULL,
        retrieval_code TEXT NOT NULL
    )
    ''')

    connection.commit()
    connection.close()


if __name__ == '__main__':
    create_database()
    print("База данных успешно создана и структурирована.")
