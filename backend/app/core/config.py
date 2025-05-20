from typing import List, Union
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:yby258014@localhost:3306/salary_management_system"
    
    # 版本信息
    VERSION: str = "1.0.0"
    
    # CORS配置
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 加密配置
    ENCRYPTION_KEY: str = "12345678901234567890123456789012"
    
    # 其他配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 