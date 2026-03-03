import os
from pathlib import Path
from typing import Set

from dotenv import load_dotenv

load_dotenv()


class Config:
    QQ_BOT_APPID: str = os.getenv("QQ_BOT_APPID", "")
    QQ_BOT_TOKEN: str = os.getenv("QQ_BOT_TOKEN", "")
    
    BSM_API_URL: str = os.getenv("BSM_API_URL", "http://47.108.93.18:11325")
    BSM_USERNAME: str = os.getenv("BSM_USERNAME", "")
    BSM_PASSWORD: str = os.getenv("BSM_PASSWORD", "")
    
    BOT_PREFIX: str = os.getenv("BOT_PREFIX", "/mc")
    
    ADMIN_USERS: Set[str] = set(
        uid.strip() for uid in os.getenv("ADMIN_USERS", "").split(",") if uid.strip()
    )
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        required = [
            ("QQ_BOT_APPID", cls.QQ_BOT_APPID),
            ("QQ_BOT_TOKEN", cls.QQ_BOT_TOKEN),
            ("BSM_API_URL", cls.BSM_API_URL),
            ("BSM_USERNAME", cls.BSM_USERNAME),
            ("BSM_PASSWORD", cls.BSM_PASSWORD),
        ]
        missing = [name for name, value in required if not value]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        return True
    
    @classmethod
    def is_admin(cls, user_id: str) -> bool:
        return user_id in cls.ADMIN_USERS


config = Config()
