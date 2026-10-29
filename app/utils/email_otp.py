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


async def send_email_verification(email: str, verification_link: str):
    """Send email verification link to user"""
    try:
        if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
            logger.warning("SMTP configuration incomplete. Logging verification link instead.")
            logger.info(f"Email verification link for {email}: {verification_link}")
            return True

        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify Your Email Address"
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = email

        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>Verify Your Email Address</h2>
            <p>Thank you for signing up! Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_link}">Verify Email Address</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
        </html>
        """

        # Create plain text content
        text_content = f"Thank you for signing up! Please verify your email address by visiting:\n\n{verification_link}\n\nThis link will expire in 24 hours.\nIf you didn't create an account, please ignore this email."

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

        logger.info(f"Email verification sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email verification to {email}: {e}")
        # Fallback: log the verification link if email sending fails
        logger.info(f"Email verification link for {email} (fallback): {verification_link}")
        return False


async def send_email_otp(email: str, otp: str, expiry_minutes: int = 10):
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

        # Format expiry time
        if expiry_minutes == 1:
            expiry_text = "1 minute"
        elif expiry_minutes < 1:
            expiry_seconds = int(expiry_minutes * 60)
            expiry_text = f"{expiry_seconds} second{'s' if expiry_seconds != 1 else ''}"
        else:
            expiry_text = f"{expiry_minutes} minutes"

        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>Your Verification Code</h2>
            <p>Your verification code is: <strong>{otp}</strong></p>
            <p>This code will expire in {expiry_text}.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """

        # Create plain text content
        text_content = f"Your verification code is: {otp}\n\nThis code will expire in {expiry_text}.\nIf you didn't request this code, please ignore this email."

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
