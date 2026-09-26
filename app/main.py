from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware

from app.database import init_db
from app.routers import auth, records

app = FastAPI(title="業務管理アプリ", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key="work-management-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(records.router)

init_db()


@app.get("/")
async def home(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)
