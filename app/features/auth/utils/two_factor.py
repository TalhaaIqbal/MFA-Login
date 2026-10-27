import pyotp
import qrcode
from io import BytesIO
import base64
from logging_config import logger


def generate_totp_secret():
    """Generate a new TOTP secret key"""
    return pyotp.random_base32()


def generate_qr_code(secret: str, email: str, app_name: str = "Scraper Dashboard") -> str:
    """Generate QR code for TOTP setup and return as base64 string"""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=app_name
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """Verify if the TOTP code is valid"""
    try:
        totp = pyotp.TOTP(secret)
        # Allow wider window (3 steps = 90 seconds) to handle clock drift
        result = totp.verify(code, valid_window=3)
        logger.info(f"TOTP verification result: {result}, code: {code}, secret length: {len(secret)}")
        return result
    except Exception as e:
        logger.error(f"Error verifying TOTP code: {e}")
        return False
