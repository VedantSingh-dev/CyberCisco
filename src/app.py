from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.database.dbConfig import Base, engine

import src.modals.courses_models
import src.modals.payments_models
import src.modals.user_models
import src.modals.general_models

from src.api.users import auth, courses, general
from src.api.admin import admin_courses, admin_general
from src.api.certifications import ceritficate_verification, exam_link
from src.api.enrollment import payments

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield



app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(general.router)
app.include_router(admin_courses.router)
app.include_router(admin_general.router)
app.include_router(ceritficate_verification.router)
app.include_router(exam_link.router)
app.include_router(payments.router)

@app.get("/")
def home():
    return {"message": "Application Running..."}

