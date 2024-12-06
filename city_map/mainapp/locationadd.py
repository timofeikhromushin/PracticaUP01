import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import mysql.connector
import view

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'citymap'
}


def show_location_add_window(username, style):
    location_window = ttk.Toplevel()
    location_window.title("Добавить локацию")
    location_window.geometry("600x500")
    location_window.configure(bg=style.colors.bg)

    # Поля для добавления локации
    ttk.Label(location_window, text="Название локации:", font=("Arial", 12)).pack(pady=10)
    location_name = ttk.Entry(location_window, font=("Arial", 12))
    location_name.pack(pady=10)

    # Функция для получения типов локаций из базы данных
    def get_location_types():
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT type FROM locations")
            types = [row[0] for row in cursor.fetchall()]
            connection.close()
            return types
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить типы локаций: {err}")
            return []

    # Динамический список типов локаций
    types = get_location_types()
    types.insert(0, "Выберите тип...")  # Вставляем опцию "Выберите тип..."

    ttk.Label(location_window, text="Тип локации:", font=("Arial", 12)).pack(pady=10)
    location_type = ttk.Combobox(location_window, values=types, state="readonly", font=("Arial", 12))
    location_type.set("Выберите тип...")
    location_type.pack(pady=10)

    ttk.Label(location_window, text="Описание:", font=("Arial", 12)).pack(pady=10)
    location_description = ttk.Text(location_window, font=("Arial", 12), height=5, width=40)  # Многострочное поле
    location_description.pack(pady=10)

    ttk.Label(location_window, text="Широта:", font=("Arial", 12)).pack(pady=10)
    latitude = ttk.Entry(location_window, font=("Arial", 12))
    latitude.pack(pady=10)

    ttk.Label(location_window, text="Долгота:", font=("Arial", 12)).pack(pady=10)
    longitude = ttk.Entry(location_window, font=("Arial", 12))
    longitude.pack(pady=10)

    # Добавляем кнопку для выбора фото
    def upload_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            image_label.config(text="Изображение выбрано: " + file_path.split("/")[-1])  # Отображаем название файла
            selected_image.set(file_path)

    ttk.Button(location_window, text="Выбрать фото", command=upload_image, bootstyle="info").pack(pady=10)

    # Метка для выбранного изображения
    selected_image = tk.StringVar()
    image_label = ttk.Label(location_window, text="Фото не выбрано", font=("Arial", 12), anchor="w")
    image_label.pack(pady=10)

    # Функция для сохранения локации в базу данных
    def save_location_to_db():
        name = location_name.get()
        type_ = location_type.get()
        description = location_description.get("1.0", "end-1c").strip()  # Получаем текст из многострочного поля
        lat = latitude.get()
        lon = longitude.get()
        image_path = selected_image.get()

        if not name or not type_ or not description or not lat or not lon:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            query = """
            INSERT INTO locations (name, type, description, latitude, longitude, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, type_, description, lat, lon, image_path))
            connection.commit()
            connection.close()
            messagebox.showinfo("Успех", "Локация успешно добавлена!")
            location_window.destroy()
            view.show_main_window(username)
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить локацию: {err}")

    save_button = ttk.Button(location_window, text="Сохранить", command=save_location_to_db,
                             bootstyle="success-outline")
    save_button.pack(pady=20)

    def go_back():
        location_window.destroy()
        view.show_main_window(username)

    back_button = ttk.Button(location_window, text="Назад", command=go_back, bootstyle="secondary-outline")
    back_button.pack(pady=10)

    location_window.minsize(650, 700)
    location_window.mainloop()
