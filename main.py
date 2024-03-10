from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers

origins = [
	'http://localhost',
    'http://127.0.0.1',
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

app.include_router(routers.authentication_router, prefix='/accounts', tags=['auth'])
app.include_router(routers.regulation_router, prefix='/regulations', tags=['regulations'])
app.include_router(routers.department_router, prefix='/departments', tags=['departments'])
app.include_router(routers.division_router, prefix='/divisions', tags=['divisions'])
app.include_router(routers.user_router, prefix='/accounts', tags=['users'])
app.include_router(routers.course_router, prefix='/courses', tags=['courses'])
app.include_router(routers.student_router, prefix='/students', tags=['students'])
