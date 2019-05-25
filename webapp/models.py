import os
from peewee import *

db_proxy = Proxy()


class Base(Model):
    class Meta:
        database = db_proxy


class Language(Base):
    language = CharField(unique=True, max_length=3)


class Letters(Base):
    lang = ForeignKeyField(Language, backref='letters')
    letters = CharField(max_length=3)
    frequency = DoubleField()

    def __str__(self):
        return f"{self.lang.language}; letters: {self.letters}; frequency: {self.frequency}"


if 'HEROKU' in os.environ:
    import urllib.parse, psycopg2

    urllib.parse.uses_netloc.append('postgres')
    url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
    db = PostgresqlDatabase(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)
    db_proxy.initialize(db)
else:
    db = SqliteDatabase('../langstat.db')
    db_proxy.initialize(db)


def initialize_db():
    db_proxy.connect()
    db_proxy.create_tables([Language, Letters])
    db_proxy.close()


if __name__ == '__main__':
    initialize_db()

