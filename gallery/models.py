import peewee as pw
from peewee import SqliteDatabase, SQL, ForeignKeyField

from gallery import config


db = SqliteDatabase(f"{config.DATA_PATH}/db.sqlite")

class BaseModel(pw.Model):
    id = pw.AutoField()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    class Meta:
        database = db

class Profile(BaseModel):
    # id = pw.AutoField
    address = pw.CharField()
    date = pw.DateTimeField()
    discord = pw.CharField()
    twitter = pw.CharField()
    email = pw.CharField()
