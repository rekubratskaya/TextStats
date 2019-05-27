from flask import Flask
import os


app = Flask(__name__)  # Инициализируем Flask приложение
app.secret_key = os.urandom(16)  # Секретный код, необходимый для интеграции Flask приожения с Heroku

'''
app запускается во внешнем модуле "run"
Текущий модуль, по сути конструктор в директории webapp
'''

import webapp.routes  # Импортируем модуль "routes"
