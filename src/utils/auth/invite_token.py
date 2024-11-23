import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.config import settings

invite_tokens = {}


def generate_invite_token(account: str) -> str:
    token = secrets.token_urlsafe(16)
    invite_tokens[account] = token
    return token


def verify_invite_token(account: str, token: str) -> bool:
    return invite_tokens.get(account) == token


async def send_invitation_email(account: str, invite_token: str) -> None:
    smtp_settings = settings.email

    msg = MIMEMultipart()
    msg['From'] = smtp_settings.from_email
    msg['To'] = account
    msg['Subject'] = 'Приглашение для регистрации'

    body = f"""
    Здравствуйте,

    Вы получили это письмо, потому что ваш адрес был использован для регистрации компании.

    Ваш инвайт-токен: {invite_token}

    Пожалуйста, перейдите по ссылке ниже, чтобы подтвердить свою регистрацию:
    http://localhost/api/v1/auth/sign-up/confirm/

    Спасибо.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_settings.smtp_server, smtp_settings.smtp_port)
        server.starttls()
        server.login(smtp_settings.smtp_username, smtp_settings.smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_settings.from_email, account, text)
        server.quit()
        logger.info(f'Письмо успешно отправлено на {account}')
    except Exception as e:
        logger.info(f'Ошибка при отправке письма: {e}')
