from flask import render_template, request, flash
from langdetect import detect, lang_detect_exception

from webapp import app
from webapp.text_scrabbling import TextProceedStrategy, text_to_test


@app.route('/', methods=['POST', 'GET'])
@app.route('/output', methods=['POST', 'GET'])
def text_forms_enable():
    if request.method == 'POST':
        texts = request.form.to_dict()
        # texts.to_dict(flat=False)
        print(type(texts))
        try:
            for k, v in texts.items():
                '''
                Verify that texts were inserted in proper language field.
                That should be done to avoid language mismatch e.g.: eng form - deu text.
                '''
                lang = detect(v)
                if not k == lang:
                    flash('Language mismatch: "{0}" was inserted in "{1}" form'.format(lang, k))
                    return render_template('forms.html', filled_forms=text_to_test)

                proceed_data = TextProceedStrategy(v, 3)
                proceed_data.letters_scrabble()
                texts[k] = sum(proceed_data.res.keys())

            return render_template('raw.html', result=texts)

        except lang_detect_exception.LangDetectException as error:
            '''
            Catch No text exception in language detection module
            That may occur if user leaves an empty field.
            To avoid app crash, render the initial template and show flash message.
            '''
            flash('{0}: fill all fields'.format(error))
            return render_template('forms.html', filled_forms=text_to_test)

    else:
        '''
        Fill forms for advance, by adding "filled_forms" parameter with "text_to_test" dictionary
        "text_to_test" dictionary is imported from "text_srabbling" module 
        '''
        return render_template('forms.html', filled_forms=text_to_test)
