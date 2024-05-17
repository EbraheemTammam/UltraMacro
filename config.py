from pydantic import EmailStr
from pydantic_settings import BaseSettings
from importlib import import_module
import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    green = "\x1b[32m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(levelname)s" + reset +":\t %(message)s",
        logging.INFO: green + "%(levelname)s" + reset + ":\t %(message)s",
        logging.WARNING: grey + "%(asctime)s - %(levelname)s" + reset + ":\t %(message)s",
        logging.ERROR: grey + "%(asctime)s - %(levelname)s" + reset + ":\t %(message)s",
        logging.CRITICAL: grey + "%(asctime)s - %(levelname)s" + reset + ":\t %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a custom console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())

# Add the handler to the logger
logger.addHandler(console_handler)


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
     
	#	root user data
	ROOT_USER_FIRST_NAME: str
	ROOT_USER_LAST_NAME: str
	ROOT_USER_EMAIL: EmailStr
	ROOT_USER_PASSWORD: str

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
            logging.warning(f'\tFailed to import {app}.models: {e}')
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