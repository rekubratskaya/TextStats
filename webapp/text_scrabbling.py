import string
import collections
from os import listdir
from langdetect import detect

"""
scipy: Chi-square test of independence of variables in a contingency table
"""
from scipy.stats import chi2_contingency

from webapp.logger import function_logger
from webapp.models import Language, Letters


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
        for k in self.res.keys():
            t = Language.get(Language.language == iso2)
            expected_frequency = Letters.select().where(Letters.lang == t.id, Letters.letters == k).first()
            if not expected_frequency.exists():
                expected_frequency = 0
            self.expected_values.append(expected_frequency)


if __name__ == '__main__':
    entries = listdir('tmp')

    for entry in entries:
        with open('tmp/'+entry, 'r') as f:
            """
            Read each text and detect its language
            Create language query in Language database
            """
            data = f.read()
            iso2 = detect(data)
            lang = Language.create(language=iso2)
            """
            Proceed 2 letters words
            """
            proceeded_data_l2 = CalculateXi2Strategy(data, 2)
            """
            Proceed 3 letters words
            """
            proceeded_data_l3 = CalculateXi2Strategy(data, 3)

            """
            Create letters and frequency queries in Letters database for both 2 and 3 letters words
            """
            for let2, freq2 in proceeded_data_l2.res.items():
                Letters.create(
                    lang=lang,
                    letters=let2,
                    frequency=freq2
                )

            for let3, freq3 in proceeded_data_l3.res.items():
                Letters.create(
                    lang=lang,
                    letters=let3,
                    frequency=freq3
                )
