import unittest
from freezegun import freeze_time
import cocktail
from cocktail import CocktailList


class DataTestCase(unittest.TestCase):
    def test_name_exists(self):
        """У каждого коктейля должно быть название"""
        for item in CocktailList():
            self.assertTrue(len(item.name) > 0)

    def test_receipt_exists(self):
        """У каждого коктейля должен быть рецепт"""
        for item in CocktailList():
            self.assertTrue(len(item.receipt) > 0)

    def test_description(self):
        """У каждого коктейля должны быть прописаны ингредиенты, но не больше 255 символов"""
        for item in CocktailList():
            self.assertTrue(0 < len(item.short_receipt) <= 255)


class DialogTestCase(unittest.TestCase):
    def test_welcome_message_for_new_session_without_command(self):
        result = cocktail.handle(create_request(session_new=True))
        self.assertEqual(result['response']['text'],
                         'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой '
                         'любимый коктейль. Расскажи, что ты хотел бы выпить. Или можешь спросить меня про коктейль дня')

    def test_help_command(self):
        help_commands = ['помощь', 'что ты умеешь']
        for command in help_commands:
            result = cocktail.handle(create_request(command))
            self.assertEqual(result['response']['text'],
                             'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.')

    def test_gratitude_command(self):
        gratitude_commands = ['спасибо', 'благодарю', 'благодарочка']
        for command in gratitude_commands:
            result = cocktail.handle(create_request(command))
            self.assertEqual(result['response']['text'], 'Пожалуйста. Главное - соблюдать культуру пития.')

    @freeze_time("2020-12-19")
    def test_daily_cocktail(self):
        result = cocktail.handle(create_request('Расскажи про коктейль дня'))
        self.assertEqual(result['response']['card']['title'], 'Негрони')

    @freeze_time("2020-12-20")
    def test_daily_cocktail(self):
        result = cocktail.handle(create_request('Расскажи про коктейль дня'))
        self.assertEqual(result['response']['card']['title'], 'Последнее слово')

    def test_random_cocktail(self):
        result = cocktail.handle(create_request('Случайный коктейль'))
        self.assertIsNotNone(result['response']['card']['title'])

    def test_cocktail_not_found(self):
        result = cocktail.handle(create_request('Неизвестный коктейль'))
        self.assertEqual(result['response']['text'], 'Я пока не знаю рецепта этого коктейля')

    def test_single_word_cocktail(self):
        result = cocktail.handle(create_request('как приготовить космополитен'))
        self.assertEqual(result['response']['text'],
                         'Чтобы приготовить коктейль космополитен, смешайте в шейкере полторы унции цитрусовой водки, '
                         'половину унции трипл-сек, половину унции сока лайма и одну унцию клюквенного морса')

    def test_multiple_words_cocktail(self):
        result = cocktail.handle(create_request('как приготовить последнее слово'))
        self.assertEqual(result['response']['text'],
                         'Чтобы приготовить коктейль последнее слово, в равных пропорциях смешай в шейкере '
                         'зеленый шартрез, джин, ликер мараскино и сок лайма')

    def test_buttons(self):
        result = cocktail.handle(create_request(session_new=True))
        buttons = result['response']['buttons']
        self.assertEqual(len(buttons), 2)


def create_request(command='', session_new=False):
    tokens = command.split()
    return {'version': '1.0', 'session': {'new': session_new},
            'request': {'original_utterance': command, 'command': command.lower(), 'nlu': {'tokens': tokens}}}


if __name__ == '__main__':
    unittest.main()
