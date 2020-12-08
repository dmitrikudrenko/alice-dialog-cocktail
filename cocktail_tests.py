import unittest
import cocktail


class MyTestCase(unittest.TestCase):
    def test_help_command(self):
        self.assertTrue(cocktail.is_help_command('помощь'))
        self.assertTrue(cocktail.is_help_command('что ты умеешь'))
        self.assertFalse(cocktail.is_help_command('совсем не помощь'))

    def test_daily_receipt_command(self):
        self.assertTrue(cocktail.is_daily_receipt_command('Расскажи про коктейль дня'))

    def test_get_single_word_name_receipt(self):
        receipt = cocktail.Cocktail().find('как приготовить космополитен', ['как', 'приготовить', 'космополитен'])
        self.assertEqual(receipt, 'Чтобы приготовить коктейль космополитен, смешайте в шейкере полторы унции '
                                  'цитрусовой водки, половину унции трипл-сек, половину унции сока лайма и одну '
                                  'унцию клюквенного морса')

    def test_get_multi_word_name_receipt(self):
        receipt = cocktail.Cocktail().find('как приготовить последнее слово', ['как', 'приготовить', 'последнее', 'слово'])
        self.assertEqual(receipt, 'Чтобы приготовить коктейль последнее слово, в равных пропорциях смешай в шейкере '
                                  'зеленый шартрез, джин, ликер мараскино и сок лайма')

    def test_receipt_not_found(self):
        receipt = cocktail.Cocktail().find('как приготовить хрючево', ['как', 'приготовить', 'хрючево'])
        self.assertIsNone(receipt)

    def test_help_message(self):
        help_message = cocktail.help_message()
        self.assertEqual(help_message, 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи '
                                       'его название.')

    def test_welcome_message(self):
        welcome_message = cocktail.welcome_message()
        self.assertEqual(welcome_message, 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать '
                                          'ингредиенты, чтобы получился твой любимый коктейль. Расскажи, что ты хотел '
                                          'бы выпить. Или можешь спросить меня про коктейль дня')


if __name__ == '__main__':
    unittest.main()
