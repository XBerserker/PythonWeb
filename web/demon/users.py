# coding=utf-8

# 使用关系型数据库时，修改数据库模型和更新数据库这样的工作时有发生，而且很重要。
# SQLAlchemy作者为此开发了迁移框架Alembic, Flask-Migrate就是基于Alembic做了轻量级封装，并集成到Flask-Script中。所有操作都通过
# Flask-Script命令完成。它能跟踪数据库结构的变化，把变化的部分应用到数据库中。

from ext import db

class User(db.Model):
    __tablename__ = 'login_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    login_count = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(128), default='unknown')
    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
