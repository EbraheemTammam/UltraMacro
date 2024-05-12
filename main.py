from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



origins = [
    'http://localhost',
    'http://127.0.0.1',
	'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5500',
    'http://127.0.0.1:5500',
	'https://tantacms.vercel.app',
]

app = FastAPI(
	title = 'GPAXL',
	description = 'server side APIs for gpaxl project',
	version = '1.0',
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*']
)


# from database.async_client import AsyncSessionLocal 
# from user.handler import UserHandler
# from user.schemas import UserCreate

# @app.on_event('startup')
# async def startup_event():
# 	async with AsyncSessionLocal() as db:
# 		handler = UserHandler(db)
# 		try:
# 			await handler.create(
# 				UserCreate(
# 					**{
# 						'first_name': settings.ROOT_USER_FIRST_NAME,
# 						'last_name': settings.ROOT_USER_LAST_NAME,
# 						'email': settings.ROOT_USER_EMAIL,
# 						'password': settings.ROOT_USER_PASSWORD,
# 						'is_admin': True,
# 						'divisions': []
# 					}
# 				)
# 			)
# 		except:
# 			return {'detail': 'root user already exists'}		
# 	return {'detail': 'root user created'}



from config import settings
from importlib import import_module


for app_name in settings.APPS:
	module_path = f"{app_name}.router"  # Adjust path as needed
	module = import_module(module_path)
	router = getattr(module, f"{app_name}_router", None)
	if app_name in ['authentication', 'user']:
		app.include_router(router, prefix='/accounts', tags=['authentication'])
		continue
	if app_name == 'upload':
		app.include_router(router, prefix='/data', tags=['uploads'])
		continue
	app.include_router(router, prefix=f'/{app_name}s', tags=[f'{app_name}s'])