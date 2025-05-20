from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 从config中导入算法常量
ALGORITHM = settings.ALGORITHM

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    创建JWT访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    """
    return pwd_context.hash(password)

def encrypt_bank_account(account_number: str) -> bytes:
    """
    加密银行账号
    """
    # 实现加密逻辑 
    # 这里使用简单实现，实际开发中应使用更安全的方法
    from cryptography.fernet import Fernet
    import base64
    
    key = settings.ENCRYPTION_KEY.encode()
    # 确保密钥是标准长度
    key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    
    f = Fernet(key)
    encrypted = f.encrypt(account_number.encode())
    return encrypted

def decrypt_bank_account(encrypted_account: bytes) -> str:
    """
    解密银行账号
    """
    # 实现解密逻辑
    from cryptography.fernet import Fernet
    import base64
    
    key = settings.ENCRYPTION_KEY.encode()
    # 确保密钥是标准长度
    key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_account)
    return decrypted.decode() 