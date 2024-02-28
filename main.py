from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers

origins = [
	'localhost',
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

app.include_router(routers.authentication_router, prefix='/auth', tags=['auth'])
app.include_router(routers.regulation_router, prefix='/regulations', tags=['regulations'])
