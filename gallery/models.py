from datetime import datetime
from uuid import uuid4

import peewee as pw
from peewee import SqliteDatabase, SQL, ForeignKeyField

from gallery import config


db = SqliteDatabase(f"{config.DATA_PATH}/db.sqlite")

def rand_id():
    return uuid4().hex


class Profile(pw.Model):
    __table__ = 'profiles'

    id = pw.AutoField()
    address = pw.CharField()
    date = pw.DateTimeField(default=datetime.utcnow)
    discord = pw.CharField(null=True)
    twitter = pw.CharField(null=True)
    email = pw.CharField(null=True)
    nonce = pw.CharField(null=True)
    nonce_date = pw.DateTimeField(null=True)

    def generate_nonce(self):
        return rand_id()[0:12]

    def change_nonce(self):
        self.nonce = self.generate_nonce()
        self.nonce_date = datetime.utcnow()
        self.save()

    def show(self):
        return {
            'address': self.address,
            'discord': self.discord,
            'twitter': self.twitter,
            'email': self.email
        }

    class Meta:
        database = db
