from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

# 把Permission类加入模板上下文
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import views, errors