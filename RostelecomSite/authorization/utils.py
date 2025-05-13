import smtplib
from email.message import EmailMessage

import random

def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_confirmation_email(user):
    msg = EmailMessage()
    msg["Subject"] = "Подтвердите регистрацию"
    msg["From"] = "igamletov@bk.ru"
    msg["To"] = user.email
    msg["Reply-To"] = "igamletov@bk.ru"
    msg["User-Agent"] = "PythonSMTP/3.11"

    confirmation_url = f"http://127.0.0.1:8000/registration?code={user.code}"
    html_content = f"""
    <html>
      <body>
        <p>Здравствуйте!</p>
        <p>Пожалуйста, нажмите на кнопку ниже, чтобы подтвердить свою регистрацию:</p>
        <a href="{confirmation_url}" 
           style="display:inline-block;padding:10px 20px;background-color:#4CAF50;color:white;
                  text-decoration:none;border-radius:5px;">
          Подтвердить
        </a>
        <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
      </body>
    </html>
    """

    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL("smtp.mail.ru", 465) as smtp:
        smtp.login("igamletov@bk.ru", "CeGiQaxwvddgt711ZG93")
        smtp.send_message(msg)

def send_restore_password_email(user):
    msg = EmailMessage()
    msg["Subject"] = "Подтвердите сброс пароля"
    msg["From"] = "igamletov@bk.ru"
    msg["To"] = user.email
    msg["Reply-To"] = "igamletov@bk.ru"
    msg["User-Agent"] = "PythonSMTP/3.11"

    confirmation_url = f"http://127.0.0.1:8000/restore?code={user.code}"
    html_content = f"""
    <html>
      <body>
        <p>Здравствуйте!</p>
        <p>Пожалуйста, нажмите на кнопку ниже, чтобы сбросить свой пароль:</p>
        <a href="{confirmation_url}" 
           style="display:inline-block;padding:10px 20px;background-color:#4CAF50;color:white;
                  text-decoration:none;border-radius:5px;">
          Сменить пароль
        </a>
        <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
      </body>
    </html>
    """

    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL("smtp.mail.ru", 465) as smtp:
        smtp.login("igamletov@bk.ru", "CeGiQaxwvddgt711ZG93")
        smtp.send_message(msg)
