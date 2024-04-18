from pydantic_settings import BaseSettings
from importlib import import_module

class Settings(BaseSettings):

	#	secret key
	SECRET_KEY: str = 'insecure key please change it'

	#	jwt token settings
	TOKEN_URL: str = 'login'
	TOKEN_ENCODING_ALGORITHM: str = 'HS256'
	ACCESS_TOKEN_EXPIRE_HOURS: int = 12

	#	database settings
	DATABASE_URL: str = 'sqlite+sqlite3:///db.sqlite3'
	ASYNC_DATABASE_URL: str = 'sqlite+aiosqlite:///db.sqlite3'

	#	installed apps
	APPS: list = [
		'user',
		'authentication',
		'regulation',
		'department',
		'division',
		'course',
		'student',
		'enrollment',
		'upload',
	]

	class Config:
		env_file = '.env'


settings = Settings()



def get_base():
	models = []
	for app in settings.APPS:
		try:
			module = import_module(f'{app}.models')
		except: 
			continue
		if getattr(module, 'Base', None) == None:
			continue
		models.append(getattr(module, 'Base', None))
	return models[-1]


Base = get_base()