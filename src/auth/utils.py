import secrets
import smtplib
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import jwt
from loguru import logger

from src.config import settings

invite_tokens = {}


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(tz=UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


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
