from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Приложение QRKot'
    database_url: str
    secret: str = 'SECRET'

    class Config:
        env_file = '.env'


settings = Settings()
