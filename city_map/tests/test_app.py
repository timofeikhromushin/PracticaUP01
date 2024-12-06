import pytest
import mysql.connector
from mainapp.reviews import show_reviews_window, show_add_review_window

TEST_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'citymap_test'  # Используем тестовую базу
}

@pytest.fixture(scope="module")
def db_connection():
    """Фикстура для подключения к тестовой базе данных."""
    connection = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = connection.cursor()

    # Создаем таблицы для тестов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        type VARCHAR(255),
        description TEXT,
        latitude FLOAT,
        longitude FLOAT,
        image_path VARCHAR(255)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        location_id INT,
        user_id INT,
        rating INT,
        review_text TEXT,
        FOREIGN KEY (location_id) REFERENCES locations(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255)
    )
    """)
    connection.commit()
    yield connection
    connection.close()

@pytest.fixture(scope="function")
def setup_test_data(db_connection):
    """Подготавливает тестовые данные перед каждым тестом."""
    cursor = db_connection.cursor()

    # Удаляем все данные перед тестами
    cursor.execute("DELETE FROM reviews;")
    cursor.execute("DELETE FROM locations;")
    cursor.execute("DELETE FROM users;")

    # Добавляем тестовую локацию
    cursor.execute("""
    INSERT INTO locations (id, name, type, description, latitude, longitude, image_path)
    VALUES (1, 'Test Location', 'Park', 'Beautiful park', 55.751244, 37.618423, 'test.jpg')
    """)

    # Добавляем тестового пользователя
    cursor.execute("""
    INSERT INTO users (id, name)
    VALUES (1, 'Test User')
    """)

    db_connection.commit()

def test_database_connection(db_connection):
    """Тестируем подключение к базе данных."""
    assert db_connection.is_connected()

def test_add_location(db_connection):
    """Тестируем добавление локации."""
    cursor = db_connection.cursor()
    query = """
    INSERT INTO locations (name, type, description, latitude, longitude, image_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, ("Test Location", "Park", "Test description", 50.5, 30.5, "path/to/image.jpg"))
    db_connection.commit()

    # Проверяем, что локация добавлена
    cursor.execute("SELECT * FROM locations WHERE name = 'Test Location'")
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "Test Location"

def test_add_review(db_connection, setup_test_data):
    """Тестируем добавление отзыва."""
    cursor = db_connection.cursor()
    query = """
    INSERT INTO reviews (location_id, user_id, rating, review_text)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (1, 1, 5, "Great place!"))
    db_connection.commit()

    # Проверяем, что отзыв добавлен
    cursor.execute("SELECT * FROM reviews WHERE review_text = 'Great place!'")
    result = cursor.fetchone()
    assert result is not None
    assert result[3] == 5  # Проверяем рейтинг

def test_get_reviews(db_connection, setup_test_data):
    """Тестируем получение отзывов."""
    cursor = db_connection.cursor()
    cursor.execute("""
    INSERT INTO reviews (location_id, user_id, rating, review_text) 
    VALUES (1, 1, 4, 'Good location!')
    """)
    db_connection.commit()

    cursor.execute("""
    SELECT reviews.rating, reviews.review_text, users.name 
    FROM reviews
    JOIN users ON reviews.user_id = users.id
    WHERE reviews.location_id = 1
    """)
    result = cursor.fetchall()
    assert len(result) > 0
    assert result[0][1] == "Good location!"

def test_get_location_types(db_connection, setup_test_data):
    """Тестируем получение типов локаций."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT DISTINCT type FROM locations")
    types = [row[0] for row in cursor.fetchall()]
    assert "Park" in types
