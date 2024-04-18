from pydantic_settings import BaseSettings
from importlib import import_module
import logging

logging.basicConfig(level=logging.INFO)

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
            logging.info(f'Successfully imported {app}.models')
        except Exception as e:
            logging.warning(f'Failed to import {app}.models: {e}')
            continue
        base = getattr(module, 'Base', None)
        if base is not None:
            models.append(base)
        else:
            logging.info(f'No Base in {app}.models')

    if not models:
        logging.error('No models found with a Base class.')
        return None

    return models[-1]


Base = get_base()