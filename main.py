from src.app import app
import uvicorn

uvicorn.run(app=app, port=8000)