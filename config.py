from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	# secret key
	SECRET_KEY: str = 'insecure key please change it'

	# jwt token settings
	TOKEN_URL: str = 'login'
	TOKEN_ENCODING_ALGORITHM: str = 'HS256'
	ACCESS_TOKEN_EXPIRE_HOURS: int = 12
	# database settings
	DATABASE_URL: str = 'sqlite+sqlite3:///db.sqlite3'
	ASYNC_DATABASE_URL: str = 'sqlite+aiosqlite:///db.sqlite3'

	class Config:
		env_file = '.env'

settings = Settings()
