from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_mail import Mail

bootstrap = Bootstrap()
db = SQLAlchemy()
# 初始化用户登录，并设置用户会话安全等级
login_manager = LoginManager()
login_manager.session_protection = 'strong'
mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # 注册蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app