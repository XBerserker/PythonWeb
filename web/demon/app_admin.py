# coding=utf-8

# 基于Flask-Loggin 和 Flask-SQLAlchemy实现包含如下功能的后台：
# 可以在后台操作数据库；
# 静态文件管理；
# 在导航栏添加一些链接和视图，比如笔者的Github地址，Google链接以及回首页的链接。还添加一个动态的链接，点击它可以登录和退出。当登录后会动态地添加一个"Authenticated"的链接
# 自定义点击"Aytgebtucated"的链接后看到的模板
import os.path

from ext import db
from users import User as _User

from flask_admin import Admin
from flask import Flask, url_for, redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.base import MenuLink, BaseView, expose

from flask_login import (current_user, UserMixin, login_user, logout_user, LoginManager)

app = Flask(__name__, template_folder='../../templates', static_folder='../../static')
app.config.from_object('config')
USERNAME = 'xiaoming'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(_User, UserMixin):
    pass

# 添加主页、登录和退出的视图
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

@app.route('/login/')
def login_view():
    user = User.query.filter_by(name=USERNAME).first()
    login_user(user)
    return redirect(url_for('admin.index'))

@app.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('admin.index'))

# 这样的视图只作为管理后台的可点击链接来用
class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

class NotAuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated

@login_manager.user_loader
def user_loader(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user

admin = Admin(app, name='web_develop', template_mode='bootstrap3')
admin.add_link(NotAuthenticatedMenuLink(name='Login', endpoint='login_view'))
admin.add_link(AuthenticatedMenuLink(name='Logout', endpoint='logout_view'))

# 也可以直接使用url参数指定地址：(其中category会创建一个叫做Links的下拉菜单，把Google和Github还有博客链接放进去)
admin.add_link(MenuLink(name='Back Home', url='/'))
admin.add_link(MenuLink(name='Google', category='Links', url='https://www.google.com/'))
admin.add_link(MenuLink(name='Github', category='Links', url='https://github.com/xberserker'))
admin.add_link(MenuLink(name='Blog', category='Links', url='http://luciferlv.tech'))

class MyAdminView(BaseView):
    @expose('/')
    def index(self):
        return self.render('chapter4/section2/authenticated-admin.html')

    def is_accessible(self):
        return current_user.is_authenticated

admin.add_view(ModelView(User, db.session))

path = os.path.join(os.path.dirname(__file__), '../../static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))

# 创建一个名为Authenticated的链接，但是必须登录才能访问
admin.add_view(MyAdminView(name='Authenticated'))

# 最后使用before_first_request钩子初始化数据库
@app.before_first_request
def create_user():
    db.drop_all()
    db.create_all()

    user = User(name=USERNAME, email='a@dongwm.com', password='123')
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)