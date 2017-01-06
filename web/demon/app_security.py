# coding=utf-8

from functools import wraps, reduce
from operator import or_

from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required)
from flask_security.forms import LoginForm



app = Flask(__name__, template_folder='../../templates')
app.config.from_object('config')
app.config['SECURITY_LOGIN_USER_TEMPLATE']='chapter4/section2/login_user.html'

db = SQLAlchemy(app)

class Permission(object):
    LOGIN = 0x01
    EDITOR = 0x02
    OPERATOR = 0x04
    ADMINISTER = 0xff
    PERMISSION_MAP = {
        LOGIN: ('login', 'Login user'),
        EDITOR: ('editor', 'Editor'),
        OPERATOR: ('op', 'Operator'),
        ADMINISTER: ('admin', 'Super administrator')
    }

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    permissions = db.Column(db.Integer, default=Permission.LOGIN)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def can(self, permissions):
        if self.roles is None:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms & permissions == permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)


# 添加login_context_process钩子
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=LoginForm)

@security.login_context_processor
def security_login_process():
    print 'Login'
    return {}

# 每次在第一次接收请求的时候就会删除相关表，再重新创建这些表，并创建两个用户，用户权限分别如下：
# dongwm@dongwm.com：它具有login与editor两种权限，但是有些页面访问不了
# admin@dongwm.co：管理员，拥有全部权限。
@app.before_first_request
def create_user():
    db.drop_all()
    db.create_all()

    for permissions, (name, desc) in Permission.PERMISSION_MAP.items():
        user_datastore.find_or_create_role(
            name=name, description=desc, permissions=permissions
        )
    for email, passwd, permissions in (
            ('dongwm@dongwm.com', '123', (
                Permission.LOGIN, Permission.EDITOR
            )),
            ('admin@dongwm.com', 'admin', (
                Permission.ADMINISTER,
            ))
    ):
        user_datastore.create_user(email=email, password=passwd)
        for permissions in permissions:
            user_datastore.add_role_to_user(
                email, Permission.PERMISSION_MAP[permissions][0]
            )
    db.session.commit()

# 添加验证访问权限的装饰器
def permission_require(permission):
    def decorator(f):
        @wraps(f)
        def _deco(*args, **kwargs):
            if not current_user.can(permission):  # currnet_user就是一个User对象，通过User类添加的can方法判断权限
                abort(403)
            return f(*args, **kwargs)
        return _deco
    return decorator

def admin_required(f):
    return permission_require(Permission.ADMINISTER)(f)


@app.route('/')
@login_required
@permission_require(Permission.LOGIN)
def index():
    return 'Login in'

@app.route('/admin/')
@login_required
@admin_required
def admin():
    return 'Only administrators can see this!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=app.debug)
