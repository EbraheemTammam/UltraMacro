from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers

origins = [
	'localhost',
]

app = FastAPI(
	title = ,
	description = ,
	version = ,
	terms_of_service = ,
	contact = {
		user: ,
		url: ,
		email: ,
	},
	license_info = {
		name: ,
		url: ,
	}
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*']
)

app.include_router(routers.authentication_router, prefix='auth', tags=['auth'])
