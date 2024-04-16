import datetime
import json
import random
import tkinter as tk
from tkinter import Menu
from tkinter import ttk
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
import sqlite3

from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm


pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arial.ttf'))


class OrderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Order System')
        self.geometry('800x600')

        self.order = {}
        self.order_window = None

        self.products = self.load_products()

        self.canvas = tk.Canvas(self)
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.pickup_combobox = 0
        self.confirm_window = None

        self.frame = tk.Frame(self.canvas)
        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.display_product_buttons()

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        self.view_order_button = tk.Button(self, text="Просмотреть заказ", command=self.view_order)
        self.update_order_button()

    def load_products(self):
        connection = sqlite3.connect('products.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name, image_path, price FROM products")
        products = cursor.fetchall()
        connection.close()
        return products

    def load_products(self):
        connection = sqlite3.connect('products.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name, image_path, price, amount FROM products")
        products = cursor.fetchall()
        connection.close()
        return products

    from tkinter import Menu

    def display_product_buttons(self):
        max_buttons_per_row = 4
        current_row = 0
        current_column = 0

        for product in self.products:
            product_name, image_path, price, amount = product
            try:
                original_image = Image.open(image_path)
                resized_image = original_image.resize((50, 50), Image.Resampling.LANCZOS)
                image = ImageTk.PhotoImage(resized_image)
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
                image = None

            button_text = f"{product_name}\n{price} тугрик.\nНа складе: {amount}"
            button_state = tk.NORMAL if amount > 0 else tk.DISABLED

            # Функция для создания контекстного меню
            def create_context_menu(event, product_name=product_name, product_price=price, product_amount=amount):
                context_menu = Menu(self.frame, tearoff=0)
                context_menu.add_command(label="Добавить к заказу",
                                         command=lambda: self.add_to_order(product_name, product_price, product_amount))
                context_menu.post(event.x_root, event.y_root)

            button = tk.Button(self.frame, image=image, text=button_text, compound="top",
                               command=lambda name=product_name, product_price=price,
                                              product_amount=amount: self.add_to_order(name, product_price,
                                                                                       product_amount),
                               state=button_state)
            button.image = image
            button.grid(row=current_row, column=current_column, padx=10, pady=10)

            # Привязка обработчика ПКМ к кнопке
            button.bind("<Button-3>", create_context_menu)

            current_column += 1
            if current_column >= max_buttons_per_row:
                current_column = 0
                current_row += 1

        self.frame.update_idletasks()

    def add_to_order(self, product_name, product_price, product_amount):
        if product_name in self.order and self.order[product_name]["qty"] >= product_amount:
            messagebox.showerror("Ошибка", f"Недостаточно '{product_name}' на складе.")
            return
        elif product_name in self.order:
            self.order[product_name]["qty"] += 1
        else:
            self.order[product_name] = {"qty": 1, "price": product_price}
        self.update_order_button()
        messagebox.showinfo("Успех", f"'{product_name}' добавлен к заказу.")

    def on_close_order_window(self):
        self.order_window.destroy()
        self.order_window = None

    def validate_quantity(self, qty_var, *args):
        try:
            value = int(qty_var.get())
            if value > 1000:
                qty_var.set("1000")
        except ValueError:
            qty_var.set("1")

    def view_order(self):
        if self.order_window is None or not self.order_window.winfo_exists():
            self.order_window = Toplevel(self)
            self.order_window.title('Ваш заказ')
            self.order_window.protocol("WM_DELETE_WINDOW", self.on_close_order_window)
        else:
            for widget in self.order_window.winfo_children():
                widget.destroy()

        total_price = 0
        for product, info in self.order.items():
            total_price += info["qty"] * info["price"]
            tk.Label(self.order_window, text=f"{product}: ").pack()
            qty_entry = tk.Entry(self.order_window, width=5)
            qty_entry.insert(tk.END, str(info['qty']))
            qty_entry.pack()

            update_btn = tk.Button(self.order_window, text="Обновить",
                                   command=lambda p=product, e=qty_entry: self.update_quantity(p, e))
            update_btn.pack()
            tk.Label(self.order_window, text=f" - {info['price']} тугрик. ").pack()

        tk.Label(self.order_window, text=f"Общая стоимость: {total_price} тугрик.").pack()
        tk.Button(self.order_window, text="Очистить заказ", command=self.clear_order).pack()
        tk.Button(self.order_window, text="Оформить заказ", command=self.confirm_order).pack()

    def create_order_window(self):
        self.order_window = Toplevel(self)
        self.order_window.title('Ваш заказ')
        self.order_window.geometry('300x300')

    def populate_order_window(self):
        total_price = 0
        for product, info in self.order.items():
            total_price += info["qty"] * info["price"]
            tk.Label(self.order_window, text=f"{product}: ").pack()
            qty_entry = tk.Entry(self.order_window, width=5)
            qty_entry.insert(tk.END, str(info['qty']))
            qty_entry.pack()
            update_btn = tk.Button(self.order_window, text="Обновить",
                                   command=lambda p=product, e=qty_entry: self.update_quantity(p, e))
            update_btn.pack()
            tk.Label(self.order_window, text=f" - {info['price']} тугрик. каждый").pack()

        tk.Label(self.order_window, text=f"Общая стоимость: {total_price} тугрик.").pack()
        tk.Button(self.order_window, text="Очистить заказ", command=self.clear_order).pack()
        tk.Button(self.order_window, text="Оформить заказ", command=self.confirm_order).pack()

    def on_close_order_window(self):
        self.order_window.destroy()
        self.order_window = None

    def update_quantity(self, product_name, entry):
        new_qty = int(entry.get())
        if new_qty == 0:
            del self.order[product_name]
        elif new_qty >= 1000:
            messagebox.showinfo("Ошибка", "Проверьте ввод.")
        else:
            self.order[product_name]["qty"] = new_qty
        self.view_order()

    def clear_order(self):
        self.order.clear()
        self.update_order_button()
        messagebox.showinfo("Информация", "Заказ очищен.")
        if hasattr(self, 'order_window') and self.order_window.winfo_exists():
            self.order_window.withdraw()
            self.order_window = None

    def update_order_button(self):
        if self.order:
            self.view_order_button.pack()
        else:
            self.view_order_button.pack_forget()

    def confirm_order(self):
        self.confirm_window = Toplevel(self)
        self.confirm_window.title('Подтверждение заказа')
        self.confirm_window.geometry('400x400')

        tk.Label(self.confirm_window, text="Подтверждение заказа:").pack()

        # Предполагается, что self.order уже определён в другом месте вашего класса
        for product, info in self.order.items():
            tk.Label(self.confirm_window,
                     text=f"{product}: {info['qty']} шт. - {info['price'] * info['qty']} тугрик.").pack()

        total_price = sum(info['qty'] * info['price'] for info in self.order.values())
        tk.Label(self.confirm_window, text=f"Общая стоимость: {total_price} тугрик.").pack()

        tk.Label(self.confirm_window, text="Выберите пункт выдачи:").pack()
        pickup_points = ['ПУНКТ ВЫДАЧИ 1 DIRE', 'ПУНКТ ВЫДАЧИ 2 RADIANT ', 'ПУНКТ ВЫДАЧИ 3 NEUTRAL']
        self.pickup_combobox = ttk.Combobox(self.confirm_window, values=pickup_points)
        self.pickup_combobox.pack()

        confirm_button = tk.Button(self.confirm_window, text="Оформить заказик",
                                   command=lambda: self.check_pickup_point_and_finalize_order(total_price))
        confirm_button.pack()
        self.order_window.destroy()

    def check_pickup_point_and_finalize_order(self, total_price):
        pickup_point = self.pickup_combobox.get()
        if pickup_point == "":
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите пунктик выдачи.")
        else:
            self.finalize_order(self.confirm_window, total_price, pickup_point)

    def finalize_order(self, confirm_window, total_price, pickup_point):
        if not self.order:
            messagebox.showerror("Ошибка", "Ваша корзина пуста.")
            return

        retrieval_code = f"{random.randint(100, 999)}"
        order_number = random.randint(10000, 99999)
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_content = {product: info for product, info in self.order.items()}
        total_amount = sum(info["qty"] * info["price"] for info in order_content.values())

        if len(self.order) >= 3:
            delivery_time = 3
        else:
            delivery_time = 6

        connection = sqlite3.connect('orders.db')
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO orders (order_date, order_number, order_content, total_amount, pickup_point, retrieval_code) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (order_date, order_number, json.dumps(order_content), total_amount, pickup_point, retrieval_code))

        connection.commit()
        connection.close()

        save_pdf_button = tk.Button(confirm_window, text="Сохранить в PDF",
                                    command=lambda: self.save_order_to_pdf(order_number, total_price, pickup_point,
                                                                           delivery_time, retrieval_code,
                                                                           order_content))
        save_pdf_button.pack()

        messagebox.showinfo("Заказик оформлен",
                            f"Ваш заказик №{order_number} успешно оформлен.\nПУНКТ ВЫДАЧИ: {pickup_point}\nКодик получения: {retrieval_code}")

        self.order = {}
        self.update_order_button()

    def save_order_to_pdf(self, order_number, total_price, pickup_point, delivery_time, retrieval_code, order_content):
        filename = f"Order_{order_number}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Arial", 12)
        c.drawString(100, 750, "Заказик №" + str(order_number))
        c.drawString(100, 735, f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 720, f"Пункт выдачи: {pickup_point}")
        c.drawString(100, 705, f"Срок доставки: {delivery_time} дней")
        c.drawString(100, 690, "Список товаров:")

        y = 675
        for product, info in order_content.items():
            c.drawString(120, y, f"{product}: {info['qty']} шт. - {info['price'] * info['qty']} тугрик.")
            y -= 15

        c.drawString(100, y - 15, f"Общая стоимость: {total_price} тугрик.")
        c.setFont("Arial-Bold", 14)
        c.drawString(100, y - 45, f"Код получения: {retrieval_code}")

        # Создание и добавление штрих-кода
        barcode = code128.Code128(retrieval_code, barWidth=0.5 * mm, barHeight=10 * mm)
        barcode.drawOn(c, 100, y - 75)

        c.setFont("Arial", 12)
        c.showPage()
        c.save()

        self.clear_order()
        self.confirm_window.destroy()
        messagebox.showinfo("PDF сохранен", f"Ваш заказ был сохранен в файл: {filename}")


if __name__ == "__main__":
    app = OrderApp()
    app.mainloop()
