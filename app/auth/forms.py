from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

# 登录表单
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remeber_me = BooleanField('记住我')
    submit = SubmitField('登录')

# 注册表单
class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Regexp('^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?!([^(0-9a-zA-Z)])+$).{6,20}$'), EqualTo('password2', message='密码必须保持一致')], description='密码必须包含 数字,英文,字符以上的两种，长度6-20')
    password2 = PasswordField('确认密码', validators=[DataRequired(), Regexp('^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?!([^(0-9a-zA-Z)])+$).{6,20}$')], description='密码必须包含 数字,英文,字符以上的两种，长度6-20')
    submit = SubmitField('注册')

    # 自定义邮箱检测
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

# 学生个人信息表单
class StudentProfileForm(FlaskForm):
    student_id = StringField('学号', validators=[DataRequired(), Regexp('^\d{9}$')], description='请输入9位学号')
    name = StringField('姓名', validators=[DataRequired(), Regexp('^[\u4E00-\u9FA5\uf900-\ufa2d·s]{2,20}$')], description='请输入真实姓名')
    gender = SelectField('性别', validators=[DataRequired()], coerce=int, choices=[(0, '女'), (1, '男')])
    phone_num = StringField('手机号', validators=[DataRequired(), Regexp('^1(3|4|5|7|8)\d{9}$', 0, '请输入正确的手机号')])
    class_name = StringField('班级', validators=[DataRequired()], description='格式如：2016级电子信息科学与技术一班')
    location = StringField('家庭地址')
    submit = SubmitField('提交')
