from fastapi.templating import Jinja2Templates
from ..conf import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)
