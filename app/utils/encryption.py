import os
from config import ENCRYPTION_KEY
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def get_encryption_key(password: str = None, salt: bytes = None) -> bytes:
    """
    Get the Fernet encryption key.

    Args:
        password: Password to derive key from. If None, uses ENCRYPTION_KEY from config.
        salt: Salt for key derivation. If None, generates random salt (stored separately needed for decryption).

    Returns:
        Fernet encryption key
    """
    if password is None:
        # Use the configured ENCRYPTION_KEY (validated at startup)
        return ENCRYPTION_KEY.encode()

    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_data(data: str, key: bytes = None) -> str:
    """
    Encrypt a string using Fernet symmetric encryption.

    Args:
        data: String to encrypt
        key: Fernet encryption key. If None, uses ENCRYPTION_KEY from config.

    Returns:
        Encrypted string (base64 encoded)
    """
    if key is None:
        key = get_encryption_key()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str, key: bytes = None) -> str:
    """
    Decrypt a string encrypted with encrypt_data.

    Args:
        encrypted_data: Encrypted string (base64 encoded)
        key: Fernet encryption key. If None, uses ENCRYPTION_KEY from config.

    Returns:
        Decrypted string

    Raises:
        ValueError: If decryption fails (invalid key or corrupted data)
    """
    if key is None:
        key = get_encryption_key()

    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def encrypt_dict(data: dict, key: bytes = None) -> dict:
    """
    Encrypt all string values in a dictionary.

    Args:
        data: Dictionary to encrypt
        key: Fernet encryption key. If None, uses ENCRYPTION_KEY from config.

    Returns:
        Dictionary with encrypted string values
    """
    encrypted = {}
    for k, v in data.items():
        if isinstance(v, str):
            encrypted[k] = encrypt_data(v, key)
        elif isinstance(v, dict):
            encrypted[k] = encrypt_dict(v, key)
        elif isinstance(v, list):
            encrypted[k] = [encrypt_data(item, key) if isinstance(item, str) else item for item in v]
        else:
            encrypted[k] = v
    return encrypted


def decrypt_dict(data: dict, key: bytes = None) -> dict:
    """
    Decrypt all string values in a dictionary.

    Args:
        data: Dictionary to decrypt
        key: Fernet encryption key. If None, uses ENCRYPTION_KEY from config.

    Returns:
        Dictionary with decrypted string values

    Raises:
        ValueError: If decryption fails
    """
    decrypted = {}
    for k, v in data.items():
        if isinstance(v, str):
            try:
                decrypted[k] = decrypt_data(v, key)
            except ValueError:
                # If not encrypted, keep original value
                decrypted[k] = v
        elif isinstance(v, dict):
            decrypted[k] = decrypt_dict(v, key)
        elif isinstance(v, list):
            decrypted[k] = [decrypt_data(item, key) if isinstance(item, str) else item for item in v]
        else:
            decrypted[k] = v
    return decrypted
