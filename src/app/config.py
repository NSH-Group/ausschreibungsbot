from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    app_name: str = 'tender-monitoring'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'tenders'
    postgres_user: str = 'tenders_user'
    postgres_password: str = 'change_me'
    @property
    def database_url(self):
        return f'postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
settings = Settings()
