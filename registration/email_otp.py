import pyotp
import asyncio
import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = "mail.sizaf.com"
SMTP_PORT = 465
SMTP_USERNAME = "dotsdesktop@sizaf.com"
SMTP_PASSWORD = "eri$45;e]H0K"
SMTP_FROM = "dotsdesktop@sizaf.com"

def generate_otp_secret() -> str:
    return pyotp.random_base32()

def generate_otp(secret: str, interval: int = 300) -> str:
    return pyotp.TOTP(secret, interval=interval).now()

def verify_otp(secret: str, otp: str, interval: int = 300) -> bool:
    return pyotp.TOTP(secret, interval=interval).verify(otp, valid_window=5)

async def send_email(recipient: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    print("Connecting to mail.sizaf.com:465 with SSL")
    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            use_tls=True,
        )
        print("Email sent!")
        return True
    except Exception as e:
        print("EMAIL SEND ERROR:", e)
        return False
    
async def send_otp(user):
    otp_secret = generate_otp_secret()
    otp = generate_otp(otp_secret)
    email_sent = await send_email(user.email, "Your OTP Code", f"Your OTP is: {otp}")
    if not email_sent:
        return {"success": False, "message": "Failed to send email."}

    return {"success": True, "otp_token": otp_secret}