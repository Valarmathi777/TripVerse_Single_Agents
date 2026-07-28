from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from api.routing import router

app = FastAPI(title="Move Agent — Smart Travel Planner")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(router, prefix="/api")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")
