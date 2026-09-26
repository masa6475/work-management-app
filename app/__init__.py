from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.security import hash_password

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
