import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Путь к вашей базе данных SQLite
db_path = 'products.db'


def add_product(name, amount, price, image_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, amount, price, image_path) VALUES (?, ?, ?, ?)",
                  (name, amount, price, image_path))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Товар успешно добавлен в базу данных!")
    except sqlite3.Error as error:
        messagebox.showerror("Ошибка", f"Произошла ошибка при добавлении товара в базу данных: {error}")


def fetch_products():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products


def view_products():
    products_window = tk.Toplevel()
    products_window.title("Список товаров")

    tree = ttk.Treeview(products_window, columns=("ID", "Name", "Amount", "Price", "Image"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Название")
    tree.heading("Amount", text="Количество")
    tree.heading("Price", text="Стоимость")
    tree.heading("Image", text="Путь до картинки")

    tree.column("ID", anchor="center")
    tree.column("Name", anchor="center")
    tree.column("Amount", anchor="center")
    tree.column("Price", anchor="center")
    tree.column("Image", anchor="center")

    products = fetch_products()
    for product in products:
        tree.insert('', tk.END, values=product)

    tree.pack(expand=True, fill='both')


def submit():
    name = name_entry.get()
    amount = amount_entry.get()
    price = price_entry.get()
    image_path = image_path_entry.get()

    if not (name and amount and price and image_path):
        messagebox.showwarning("Предупреждение", "Все поля должны быть заполнены!")
        return

    try:
        amount = int(amount)
        price = float(price)
    except ValueError:
        messagebox.showerror("Ошибка", "Количество и стоимость должны быть числовыми значениями.")
        return

    add_product(name, amount, price, image_path)


# Создание графического интерфейса
root = tk.Tk()
root.title("Менеджер товаров")

# Создание и расположение виджетов
tk.Label(root, text="Название:").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, sticky="ew")

tk.Label(root, text="Количество:").grid(row=1, column=0, sticky="w")
amount_entry = tk.Entry(root)
amount_entry.grid(row=1, column=1, sticky="ew")

tk.Label(root, text="Стоимость:").grid(row=2, column=0, sticky="w")
price_entry = tk.Entry(root)
price_entry.grid(row=2, column=1, sticky="ew")

tk.Label(root, text="Путь до картинки:").grid(row=3, column=0, sticky="w")
image_path_entry = tk.Entry(root)
image_path_entry.grid(row=3, column=1, sticky="ew")

submit_button = ttk.Button(root, text="Добавить товар", command=submit)
submit_button.grid(row=4, column=0, columnspan=2, sticky="ew")

view_products_button = ttk.Button(root, text="Просмотр товаров", command=view_products)
view_products_button.grid(row=5, column=0, columnspan=2, sticky="ew")

root.mainloop()
