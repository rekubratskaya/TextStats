import string
import collections
import os
from scipy.stats import chisquare

from webapp.logger import function_logger


text_to_test = {
    'en': "One Hundred Years of Solitude is the story of seven generations of the Buendía Family in the town of Macondo.",
    'fr': "Cent Ans de solitude relate l'histoire de la famille Buendia sur six générations, dans le village imaginaire de Macondo.",
    'es': "El libro narra la historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.",
    'de': "Der Roman Hundert Jahre Einsamkeit begleitet sechs Generationen der Familie Buendía und hundert Jahre wirklichen Lebens in der zwar fiktiven Welt von Macondo."
}


class TextProceedStrategy:

    def __init__(self, text: str, num: int):
        self.text = text
        self.num = num
        self.res = dict()

    @function_logger
    def __text_to_words(self) -> list:
        """
        Strip punctuation from a text and split it into a list
        """
        clear_words = self.text.translate(str.maketrans('', '', string.punctuation + string.digits))
        words = clear_words.split()
        return words

    @function_logger
    def _letters_scrabble(self):
        """Split each word into equal parts"""
        chunks = list()
        for word in self.__text_to_words():
            if len(word) < self.num:
                continue
            step = self.num - 1
            for i in range(0, len(word)-step):
                chunks.append(word[i:i + self.num].lower())
        self.res.update(collections.Counter(chunks))
        self._calc_chunks_frequency(self.res)

    @staticmethod
    @function_logger
    def _calc_chunks_frequency(res):
        """
        Calculate each chunk frequency and update chunks dictionary with new values
        """
        denominator = sum(res.values())
        for key, value in res.items():
            res[key] = value / denominator


class CalculateXi2Strategy(TextProceedStrategy):

    def __init__(self, text: str, num: int, iso2: str):
        super().__init__(text, num)
        self._letters_scrabble()
        self.iso2 = iso2
        self.observed_values = list()
        self.expected_values = list()

    @function_logger
    def _get_expected_array(self):
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to TextStats main directory
        APP_TMP = os.path.join(APP_ROOT, 'tmp')
        with open(os.path.join(APP_TMP, self.iso2 + '.txt'), 'r', encoding='utf-8', errors='surrogateescape') as f:
            data = f.read()
            base_letters_dict = TextProceedStrategy(data, self.num)
            base_letters_dict._letters_scrabble()
            for k, v in self.res.items():
                expected_frequency = base_letters_dict.res.get(k)
                if expected_frequency is None:
                    continue
                self.observed_values.append(v)
                self.expected_values.append(expected_frequency)

    @function_logger
    def calculate_xi2(self):
        self._get_expected_array()
        chi2, p_value = chisquare(self.observed_values, self.expected_values)
        return round(chi2, 4), round(p_value, 4)
