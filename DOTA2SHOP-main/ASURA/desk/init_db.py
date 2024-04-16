import sqlite3

# Подключение к базе данных (или создание, если она не существует)
conn = sqlite3.connect('products.db')
c = conn.cursor()

# Создание таблицы
c.execute('''CREATE TABLE products
             (id INTEGER PRIMARY KEY, name TEXT, amount INT, price REAL, image_path TEXT)''')

# Вставка тестовых данных
products = [
    (1, 'ВИТЧБЛЕЙДИК', 12, 2775, 'images/witch_blade.jpg'),
    (2, 'БЭКЭБЭХА', 18, 4050, 'images/black_king_bar.jpg'),
    (3, 'МОРБИТОЧКА', 777, 900, 'images/morbid_mask.jpg'),
    (4, 'ТАРАСКА', 8, 5200, 'images/heart_of_tarrasque.jpg'),
    (5, 'МОМ', 666, 900, 'images/mask_of_madness.jpg'),
    (6, 'ЭБИСАЛ', 0, 6250, 'images/abyssal_blade.jpg'),
]

c.executemany('INSERT INTO products VALUES (?,?,?,?,?)', products)

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()

print("База данных успешно создана и заполнена!")
