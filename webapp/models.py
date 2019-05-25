import os
from peewee import *

# from webapp.logger import function_logger

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

if __name__ == '__main__':
    db_proxy.connect()
    db_proxy.create_tables([Language, Letters])
    # for each in Letters.select().where(Letters.lang == 1, fn.length(Letters.letters) == 2):
    #     print(each)
    db_proxy.close()

