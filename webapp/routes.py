from flask import render_template, request, flash
from langdetect import detect, lang_detect_exception

from webapp import app
from webapp.texting import CalculateXi2Strategy, text_to_test


@app.route('/', methods=['POST', 'GET'])
@app.route('/output', methods=['POST', 'GET'])
def text_forms_enable():
    if request.method == 'POST':  # Если программа получила данные от пользователя - запускаем процесс обработки
        texts = request.form.to_dict()  # Переводим данные в словарь в формате {"язык": "текст"}
        try:  # Пробуем обработать данные
            for k, v in texts.items():  # Берем текст
                iso2 = detect(v)  # Определяем язык текста - через внешний модуль langdetect
                if not k == iso2:  # Определяем соответствует язык поля языку текста
                    flash('Language mismatch: "{0}" was inserted in "{1}" form'.format(iso2, k))
                    # Если нет, то выводим ошибку
                    return render_template('stats.html', filled_forms=text_to_test)
                    # И возвращает на основную страницу
                # Если все хорошо, продолжаем
                treegrams = CalculateXi2Strategy(v, 3, iso2)  # Считаем триграммы
                tree = treegrams.calculate_xi2()  # Считаем Xi2

                bigrams = CalculateXi2Strategy(v, 2, iso2)  # Считаем биграммы
                bi = bigrams.calculate_xi2()  # Считаем Xi2
                texts[k] = (tree, bi)  # Обновляем полученный от пользователя словарь, заменяя текста статистикой Xi2
            return render_template('stats.html', result=texts)
            # Отправляем пользователя на страницу с резуьтатами
        except lang_detect_exception.LangDetectException as error:  # Исключаем ошибку LangDetectException
            # Эта ошибка возникает, если пользователь не заполнил все поля
            flash('{0}: fill all fields'.format(error))
            # flash отправляет сообщение пользователю об ошибке
            return render_template('stats.html', filled_forms=text_to_test)
            # И возвращает на основную страницу
    else:  # Если программа еще не получила данные
        return render_template('stats.html', filled_forms=text_to_test)
        # Запускаем базовый html шаблон и передаем ему данные filled_forms=text_to_test
        # text_to_test - берем с модуля texting.py - это примеры текстов


'''
Функция text_forms_enable принимает текст от пользователя, обрабатывает 
этот текст и отвечает за запуск страниц ("/" или "output") с 
данными (filled_forms или result)
'''
