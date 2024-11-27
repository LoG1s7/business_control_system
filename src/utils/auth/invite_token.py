import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jwt
from loguru import logger
from pydantic import UUID4

from src.config import settings
from src.schemas.user import UserRole
from src.utils.auth.jwt_tools import create_jwt, decode_jwt


def generate_admin_invite_token(account: str, role: UserRole) -> str:
    token_data = {
        'sub': account,
        'role': role.value,
    }
    invite_token = create_jwt(
        token_type='invite',
        token_data=token_data,
        expire_timedelta=timedelta(days=1),
    )
    return invite_token


def generate_employee_invite_token(company_id: UUID4, account: str, role: UserRole) -> str:
    token_data = {
        'company_id': str(company_id),
        'sub': account,
        'role': role.value,
    }
    invite_token = create_jwt(
        token_type='invite',
        token_data=token_data,
        expire_timedelta=timedelta(days=1),
    )
    return invite_token


def verify_invite_token(token: str) -> dict | None:
    try:
        payload = decode_jwt(token)
        if payload.get('type') != 'invite':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.error('Токен истёк')
        return None
    except jwt.InvalidTokenError:
        logger.error('Неверный токен')
        return None


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
