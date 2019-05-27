import string
import collections
import os
from scipy.stats import chisquare

from webapp.logger import function_logger
'''
C модуля "logger" импортируем функцию деоратора "function_logger" для логирования функций основного модуля
'''

text_to_test = {
    'en': "One Hundred Years of Solitude is the story of seven generations of the Buendía Family in the town of Macondo.",
    'fr': "Cent Ans de solitude relate l'histoire de la famille Buendia sur six générations, dans le village imaginaire de Macondo.",
    'es': "El libro narra la historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.",
    'de': "Der Roman Hundert Jahre Einsamkeit begleitet sechs Generationen der Familie Buendía und hundert Jahre wirklichen Lebens in der zwar fiktiven Welt von Macondo."
}


class TextProceedStrategy:

    def __init__(self, text: str, num: int):
        self.text = text  # Текст в виде строки, который необходимо проанализировать
        self.num = num  # Задаем кол-во символов для N-грамм
        self.res = dict()  # Создаем пустой словарь, который далее будет заполняться N-граммами и их частотами

    '''
    Метод __init__ создает конструктор для класса "TextProceedStrategy", 
    который отвечает за обработку текста - очищение текста от знаков 
    пуктуации и чисел, выделение в тексте биграмм и триграмм и 
    вычисление их частот. 
    '''

    @function_logger  # Декоратор логирования
    def __text_to_words(self) -> list:
        clear_words = self.text.translate(str.maketrans('', '', string.punctuation + string.digits))
        # Убираем с текста ненужные символы и числа. При этом спецсимволы в Французского и т.д. языков остаются.
        words = clear_words.split()  # Разбиваем текст на слова и создаем список из слов
        return words
    '''
    Функция "__text_to_words" используется внутри класса "TextProceedStrategy"
    и отвечает за очищение текста от "мусора" и разбитие его на слова.
    В return получаем список всех слов в порядке их появления в тексте. 
    '''

    @function_logger  # Декоратор логирования
    def _letters_scrabble(self):
        chunks = list()  # Создаем пустой список для биграмм или триграмм
        for word in self.__text_to_words():  # Берем слово из списка, полученного из "__text_to_words"
            if len(word) < self.num:  # Вычисляем длину слова
                continue  # Если длина меньше значения, заданого в параметре "num", тогда переходим к следующему слову
            step = self.num - 1  # Вычисляем шаг, для разбития слова на граммы
            for i in range(0, len(word)-step):  # i - это кол-во граммов в слове
                chunks.append(word[i:i + self.num].lower())
                # Разбиваем слово на граммы с использованием среза [i:i+num] и добавляем каждый грамм в список "chunks"
        self.res.update(collections.Counter(chunks))
        # Подсчитываем кол-во каждого грамма в списке "chunks" и обновляем, заданный в конструкторе, пустой словарь
        # в формате {"грамм": кол-во}
        self._calc_chunks_frequency(self.res)
        # Делаем переподсчет даных в словаре и переводим кол-во в частоту
    '''
    Функция "_letters_scrabble" вызывается внутри дочернего класса 
    "CalculateXi2Strategy" и отвечает за разбитие каждого слова на 
    граммы и подсчет частоты каждого грамма.
    '''

    @staticmethod  # _calc_chunks_frequency не требует передачи обьекта, потому она в @staticmethod'е
    @function_logger  # Декоратор логирования
    def _calc_chunks_frequency(res: dict):
        denominator = sum(res.values())  # Считаем общее кол-во всех грамм
        for key, value in res.items():  # Для каждого грамма обновляем значение
            res[key] = value / denominator  # Вместо кол-ва подставляем частоты
    '''
    Функция "_calc_chunks_frequency" вызывается внутри функции "_letters_scrabble" и 
    овечает за подсчет частоты граммов в словаре "res"
    '''


class CalculateXi2Strategy(TextProceedStrategy):

    def __init__(self, text: str, num: int, iso2: str):
        super().__init__(text, num)
        self._letters_scrabble()
        self.iso2 = iso2
        self.observed_values = list()
        self.expected_values = list()
    '''
    Метод __init__ создает конструктор для класса "CalculateXi2Strategy", который
    отвечает за обработку данных в словаре "res" и вычиления статистики Xi2.
    super().__init__ определяет наследовательность класса "CalculateXi2Strategy"
    относительно "TextProceedStrategy". 
    В конструкторе self._letters_scrabble() запускает функцию обработки текста, чтобы не
    вызывать функцию внешней командой.
    '''

    @function_logger  # Декоратор логирования
    def _get_expected_array(self):
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        # Переходим в директорию ../TextStats/webapp/
        APP_TMP = os.path.join(APP_ROOT, 'tmp')
        # Выбираем путь ../TextStats/webapp/tmp/ - это нужно для выбора большого текста с которым будем сравнивать
        with open(os.path.join(APP_TMP, self.iso2 + '.txt'), 'r', encoding='utf-8', errors='surrogateescape') as f:
            # Выбираем файл языка например, iso2 = "en", тогда ../TextStats/webapp/tmp/en.txt
            # Указываем кодировку 'utf-8' для чтения спец символов французского, немецкого и испансского языков
            # Указываем 'surrogateescape' для обработки символов, которых нет в 'utf-8' (частные случаи во французском)
            data = f.read()  # Читаем файл и берем его текст
            base_letters_dict = TextProceedStrategy(data, self.num)
            base_letters_dict._letters_scrabble()  # Обрабатываем текст, так же как и тестовый текст
            # Из-за данного процеса програма работает медленно - можно ускорить через чтение JSON файлов
            for k, v in self.res.items():  # Берем граммы со словаря "res"
                expected_frequency = base_letters_dict.res.get(k)
                # Находим граммы и их частоты среди грамм большого текста
                if expected_frequency is None:  # Если не находим, тогда пропускаем
                    continue
                self.observed_values.append(v)  # Добавляем наблюдаемые значения (только частоты) в список
                self.expected_values.append(expected_frequency)  # Добавляем ожидаемые значения во второй список

    '''
    Функция "_get_expected_array" вызывается внутри функции "calculate_xi2" и отвечает
    за формирования двух списков:
    1) observed_values - наблюдаемые значения (текст пользователя)
    2) expected_values - ожидаемые значения (текст програмы)
    '''

    @function_logger  # Декоратор логирования
    def calculate_xi2(self):
        self._get_expected_array()
        chi2, p_value = chisquare(self.observed_values, self.expected_values)
        return round(chi2, 4), round(p_value, 4)

    '''
    Функция "calculate_xi2" отвечает за обработку полученных списков 
    "observed_values" и "expected_values" и подсчитывает Xi2 с помощью
    библиотеки scipy 
    '''