from django_sorcery.db import databases
from django.db import models
from sqlalchemy.sql import func
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from sqlalchemy import Column, String, TIMESTAMP

session = databases.get('default')

class Users(session.Model):
    '''User class is used to create users model with given schema'''
    __tablename__ = 'users'
    acct = Column(String(), primary_key=True)
    pwd = Column(String(), nullable=False)
    fullname = Column(String())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

class AuthUser(AbstractBaseUser):
    '''AuthUser is used to implement an user class which extends abstract user'''
    acct = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255, db_column="pwd")
    last_login = models.DateTimeField(default=False, db_column="updated_at")
    USERNAME_FIELD = 'acct'

    class Meta:
        db_table = 'users'
