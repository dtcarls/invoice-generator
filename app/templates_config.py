from fastapi.templating import Jinja2Templates

# Shared Jinja2Templates instance imported by both main.py and route modules
templates = Jinja2Templates(directory="app/templates")
