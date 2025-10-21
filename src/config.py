import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("DB_PORT", "3307"))  # compose에서 3307:3306 매핑
    user: str = os.getenv("DB_USER", "appuser")
    password: str = os.getenv("DB_PASSWORD", "apppass")
    database: str = os.getenv("DB_NAME", "appdb")
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 1800

    def url(self) -> str:
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"


settings = Settings()
