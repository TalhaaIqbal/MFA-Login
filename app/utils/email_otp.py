import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logging_config import logger
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_FROM_NAME


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def verify_otp(stored_otp: str, provided_otp: str) -> bool:
    """Verify if the provided OTP matches the stored OTP"""
    return stored_otp == provided_otp


async def send_email_otp(email: str, otp: str):
    """Send OTP to user's email using SMTP"""
    try:
        if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
            logger.warning("SMTP configuration incomplete. Logging OTP instead.")
            logger.info(f"Email OTP for {email}: {otp}")
            return True

        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Verification Code"
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = email

        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>Your Verification Code</h2>
            <p>Your verification code is: <strong>{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """

        # Create plain text content
        text_content = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes.\nIf you didn't request this code, please ignore this email."

        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, email, message.as_string())

        logger.info(f"Email OTP sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email OTP to {email}: {e}")
        # Fallback: log the OTP if email sending fails
        logger.info(f"Email OTP for {email} (fallback): {otp}")
        return False
