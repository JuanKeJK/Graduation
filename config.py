import os

class Config:
    # 密钥：保护所有表单免受跨站请求伪造
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # 配置数据库，设置每次请求结束都会自动commit数据库的变动
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 配置电子邮件主题前缀、默认发件人和管理员邮箱
    FLASKY_MAIL_SUBJECT_PREFIX = '[AQNU]'
    MAIL_DEFAULT_SENDER = ('Qiao Lei', os.environ.get('MAIL_USERNAME'))
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # 分页页数
    FLASKY_POSTS_PER_PAGE = 10 if os.environ.get('FLASKY_POSTS_PER_PAGE')is None else int(os.environ.get('FLASKY_POSTS_PER_PAGE'))

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    # 数据库URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:123456@127.0.0.1:3306/graduation'
    # 配置电子邮件服务器的主机名或IP地址
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # 配置电子邮件服务器的端口
    MAIL_PORT = 587
    # 配置电子邮件服务器的传输层安全协议
    MAIL_USE_TLS = True
    # 配置电子邮件用户名和密码
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}