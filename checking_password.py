import sqlite3
import hashlib

#Таблица users: id, name, email, password_hash, role, created_at

def verify_user(email: str, password: str) -> bool:
    """
    Проверяет соответствие введённых email и пароля данным в базе.
    
    Args:
        email: Введённый email пользователя
        password: Введённый пароль пользователя
        
    Returns:
        bool: True если данные верные, False если нет

    Пример:
        >>> if name == "main":
        >>>     user_email = input("Введите email: ")
        >>>     user_password = input("Введите пароль: ")

        >>> if verify_user(user_email, user_password):
        >>>     print("Аутентификация успешна!")
        >>> else:
        >>>     print("Неверный email или пароль")
        
    """
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('database.db')  # замените на ваш путь к БД
        cursor = conn.cursor()
        
        # Ищем пользователя с указанным email
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result is None:
            # Пользователь с таким email не найден
            return False
        
        # Получаем хеш пароля из базы
        stored_password_hash = result[0]
        
        # Хешируем введённый пароль для сравнения
        input_password_hash = hashlib.sha3_256(password.encode()).hexdigest()
        
        # Сравниваем хеши
        return input_password_hash == stored_password_hash
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return False
    finally:
        # Закрываем соединение в любом случае
        if conn:
            conn.close()

    

