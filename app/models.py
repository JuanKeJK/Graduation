import datetime
import hashlib
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request


# 权限常量
class Permission:
    FOLLOW = 0x01
    COMMIT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


# 学生类
class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    # 学号
    student_id = db.Column(db.String(16), unique=True, index=True)
    # 昵称
    username = db.Column(db.String(16))
    # 实名
    name = db.Column(db.String(16), index=True)
    # 性别
    gender = db.Column(db.String(2))
    # 生日
    birth = db.Column(db.DateTime())
    # 地区
    location = db.Column(db.String(32))
    # 班级
    class_name = db.Column(db.String(32))
    # 简介
    about_me = db.Column(db.Text())
    # 手机号
    phone_number = db.Column(db.String(16), unique=True, index=True)
    # 邮箱
    email = db.Column(db.String(64), unique=True, index=True)
    # 密码
    password_hash = db.Column(db.String(128))
    # 头像
    avatar_hash = db.Column(db.String(32))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成用户头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secur.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    # 生成虚拟数据
    @staticmethod
    def generate_fake(count=20):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            s = Student(name=forgery_py.internet.user_name(True))
            db.session.add(s)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<Student %r>' % self.name

# 角色模型类
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    # 在数据库中创建角色
    @staticmethod
    def insert_roles():
        roles = {
            '学生' : (Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ARTICLES, True),
            '老师' : (Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            '管理员' : (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 学号/工号
    student_id = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    gender = db.Column(db.String(4))
    phone_number = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(64), unique=True, index=True)
    class_name = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(64), default='安庆')
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    avatar_hash = db.Column(db.String(32))

    # 定义默认角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成确认令牌
    def generate_confirmation_token(self, expiration=180):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 确认令牌
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 检查是否有指定的权限
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == Permission

    # 检查管理员权限
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 刷新用户的最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 生成虚拟数据
    @staticmethod
    def generate_fake(count=20):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()

        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # 生成用户头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secur.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.name


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# 加载用户回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))