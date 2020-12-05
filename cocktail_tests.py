import unittest
import cocktail


class MyTestCase(unittest.TestCase):
    def test_help_command(self):
        self.assertTrue(cocktail.is_help_command('помощь'))
        self.assertTrue(cocktail.is_help_command('что ты умеешь'))
        self.assertFalse(cocktail.is_help_command('совсем не помощь'))

    def test_get_receipt(self):
        receipt = cocktail.Cocktail().find(['космополитен'])
        self.assertEqual(receipt, 'Чтобы приготовить коктейль космополитен, смешайте в шейкере полторы унции '
                                  'цитрусовой водки, половину унции трипл-сека, половину унции сока лайма и одну '
                                  'унцию клюквенного морса')

    def test_receipt_not_found(self):
        receipt = cocktail.Cocktail().find(['хрючево'])
        self.assertIsNone(receipt)

    def test_help_message(self):
        help_message = cocktail.help_message()
        self.assertEqual(help_message, 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи '
                                       'его название.')

    def test_welcome_message(self):
        welcome_message = cocktail.welcome_message()
        self.assertEqual(welcome_message, 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать '
                                          'ингредиенты, чтобы получился твой любимый коктейль. Расскажи, что ты хотел '
                                          'бы выпить.')


if __name__ == '__main__':
    unittest.main()
