import string
import collections
import os
from langdetect import detect

"""
scipy: Chi-square test of independence of variables in a contingency table
"""
from scipy.stats import chi2_contingency

from webapp.logger import function_logger
# from webapp.models import LetitbeDB


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
        words = clear_words.split(' ')
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

    def __init__(self, text: str, num: int):
        super().__init__(text, num)
        self._letters_scrabble()
        self.observed_values = list(self.res.values())
        self.expected_values = list()

    @function_logger
    def get_expected_array(self, iso2):
        # base_text = LetitbeDB.get(LetitbeDB.language == iso2)  #TODO вот здесь вот проблема !!!
        # base_letters_dict = TextProceedStrategy(base_text.text, 3)
        # base_letters_dict._letters_scrabble()

        APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
        APP_TMP = os.path.join(APP_ROOT, 'tmp')
        entries = os.listdir(APP_TMP)

        for entry in entries:
            print(entry)
            with open(os.path.join(APP_TMP, entry), 'r') as f:
                data = f.read()
                iso_data = detect(data)
                if not iso_data == iso2:
                    continue
                base_letters_dict = TextProceedStrategy(data, 3)
                base_letters_dict._letters_scrabble()
                for k in self.res.keys():
                    expected_frequency = base_letters_dict.res.get(k, 0)
                    self.expected_values.append(expected_frequency)

