import os
from os import listdir
from langdetect import detect
from peewee import *

db_proxy = Proxy()


class LetitbeDB(Model):
    class Meta:
        database = db_proxy

    language = CharField(unique=True, max_length=3)
    text = CharField(unique=True)


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
    db.connect()
    db.create_tables([LetitbeDB], safe=True)

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
    APP_TMP = os.path.join(APP_ROOT, 'tmp')
    entries = os.listdir(APP_TMP)

    for entry in entries:
        with open(os.path.join(APP_TMP, entry), 'r', encoding='utf-8', errors='surrogateescape') as f:
            """
            Read each text and detect its language
            Create language query in Language database
            """

            data = f.read()
            iso2 = detect(data)
            LetitbeDB.create(language=iso2, text=data)
