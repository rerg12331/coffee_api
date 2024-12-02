import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import sender_email, sender_password  # Импорт конфигурации

async def send_email(recipient_email: str, code: int) -> bool:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Создание сообщения
    subject = "Ваш код"
    body = f"Ваш код: {code}"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Отправка письма через aiosmtplib
        await aiosmtplib.send(
            msg, 
            hostname=smtp_server,
            port=smtp_port,
            username=sender_email,
            password=sender_password,
            use_tls=False,
            start_tls=True,
        )
        print("Письмо успешно отправлено!")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False