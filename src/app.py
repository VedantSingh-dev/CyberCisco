from contextlib import asynccontextmanager
import subprocess
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

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables first
    Base.metadata.create_all(bind=engine)
    
    # 2. Run seed script after tables are ready
    try:
        print("Running seed script...")
        result = subprocess.run(["python", "seed.py"], capture_output=True, text=True)
        print("Seed Output:", result.stdout)
        if result.stderr:
            print("Seed Warnings/Errors:", result.stderr)
    except Exception as e:
        print(f"Failed to execute seed script: {e}")
        
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows all origins (cross-platform)
    allow_credentials=True,     # Allows cookies/authorization headers
    allow_methods=["*"],        # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],        # Allows all headers
)

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