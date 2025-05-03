import sqlite3
import re
database='database.db'

def check_email_unique(email):
    
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.fullmatch(email_pattern, email):
        return False
    
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT email 
                           FROM users 
                           WHERE email = ?', (email,)
                           ''')
            result = cursor.fetchone()
            
            return not bool(result)
    
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return False

def validate_password(password):
    if len(password) <8 or len(password) >63:
        return False
    else:
        return True