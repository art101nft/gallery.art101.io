import peewee as pw
from peewee import SqliteDatabase, SQL, ForeignKeyField

from gallery import config


db = SqliteDatabase(f"{config.DATA_PATH}/db.sqlite")


class Events(pw.Model):
    id = pw.AutoField()
    event_type = pw.CharField()
    source_owner = pw.CharField()
    target_owner = pw.CharField()
    token_id = pw.IntegerField()
    amount = pw.IntegerField()
    date = pw.DateTimeField()
    tx_hash = pw.CharField()
    log_index = pw.IntegerField()
    platform = pw.CharField()
    block_number = pw.IntegerField()

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    class Meta:
        database = db
