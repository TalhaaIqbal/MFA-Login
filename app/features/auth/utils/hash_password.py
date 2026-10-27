from core.security import pwd_context

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
