from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_title: str = 'Приложение QRKot'
    database_url: str = Field(default='sqlite+aiosqlite:///./fastapi.db')
    secret: str = 'SECRET'

    class Config:
        env_file = '.env'


settings = Settings()
