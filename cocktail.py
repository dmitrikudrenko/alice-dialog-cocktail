from datetime import datetime
import json
import random


def handler(event, context):
    return handle(event)


def handle(event):
    response = get_response(event)
    alice_response = {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': response.text,
            'end_session': 'false'
        }
    }
    alice_response['response'].update(
        {
            'buttons': [
                {
                    'title': '📅 Коктейль дня',
                    'hide': 'true'
                },
                {
                    'title': '✨ Случайный коктейль',
                    'hide': 'true'
                }
            ]
        }
    )
    cocktail = response.cocktail
    if cocktail:
        card = {
            'card': {
                'type': 'BigImage',
                'image_id': cocktail.image,
                'title': cocktail.name.capitalize()
            }
        }
        if cocktail.short_receipt:
            card['card'].update({'description': cocktail.short_receipt})
        alice_response['response'].update(card)
    return alice_response


def get_response(event):
    request = event['request']
    command = request['command']

    if event['session']['new'] and command == '':
        return Response(welcome_message())
    elif is_help_command(command):
        return Response(help_message())
    elif is_gratitude_command(command):
        return Response(gratitude_message())
    elif is_daily_receipt_command(command):
        return daily_receipt_response()
    elif is_random_receipt_command(command):
        return random_receipt_response()
    else:
        response = query_receipt_response(request)
        if response:
            return response
        else:
            return Response(unknown_message())


def is_help_command(command):
    return command in ['помощь', 'что ты умеешь']


def is_gratitude_command(command):
    return command in ['спасибо', 'благодарю', 'благодарочка']


def is_daily_receipt_command(command):
    return 'коктейль дня' in command


def is_random_receipt_command(command):
    return 'случайный' in command


def welcome_message():
    return 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой ' \
           'любимый коктейль. Расскажи, что ты хотел бы выпить. Или можешь спросить меня про коктейль дня'


def help_message():
    return 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.'


def gratitude_message():
    return 'Пожалуйста. Главное - соблюдать культуру пития.'


def unknown_message():
    return 'Я пока не знаю рецепта этого коктейля'


def daily_receipt_response():
    daily_cocktail = CocktailList().daily()
    return Response('Коктейль дня - {}. {}'.format(daily_cocktail.get_name(), intro(daily_cocktail)), daily_cocktail)


def random_receipt_response():
    random_cocktail = CocktailList().random()
    return Response('Коктейль {}. {}'.format(random_cocktail.get_name(), intro(random_cocktail)), random_cocktail)


def query_receipt_response(request):
    tokens = request['nlu']['tokens']
    original_utterance = request['original_utterance']
    found_cocktail = CocktailList().find(original_utterance, tokens)
    if found_cocktail:
        return Response(intro(found_cocktail), found_cocktail)
    return None


def intro(c):
    return 'Чтобы приготовить коктейль {}, {}'.format(c.get_name(), c.get_receipt())


class Taste:
    def __init__(self, sour, strong, fruit, fresh):
        self.sour = sour
        self.strong = strong
        self.fruit = fruit
        self.fresh = fresh


class Cocktail:
    def __init__(self, name, extra_names, receipt, image, short_receipt, name_tts, receipt_tts, taste, alcohol):
        self.name = name
        self.extra_names = extra_names
        self.receipt = receipt
        self.image = image
        self.short_receipt = short_receipt
        self.name_tts = name_tts
        self.receipt_tts = receipt_tts
        self.taste = taste
        self.alcohol = alcohol

    def get_name(self):
        if self.name_tts:
            return self.name_tts
        else:
            return self.name

    def get_receipt(self):
        if self.receipt_tts:
            return self.receipt_tts
        else:
            return self.receipt


class CocktailList(list):
    def __init__(self):
        super().__init__()
        with open("data.json", "r") as read_file:
            data = json.load(read_file)

        for obj in data:
            self.append(Cocktail(
                obj['original_name'],
                obj.get('names'),
                obj.get('receipt'),
                obj.get('image'),
                obj.get('short_receipt'),
                obj.get('name_tts'),
                obj.get('receipt_tts'),
                Taste(
                    obj.get('sour'),
                    obj.get('strong'),
                    obj.get('fruit'),
                    obj.get('fresh')
                ),
                obj.get('alcohol')
            ))

    def find(self, phrase, words):
        equal = self.find_by_equal(phrase)
        if equal:
            return equal

        for c in self:
            if c.name in phrase or c.name in words:
                return c

            if c.extra_names:
                for name in c.extra_names:
                    if name in phrase or name in words:
                        return c
        return None

    def find_by_equal(self, phrase):
        for c in self:
            if c.name == phrase:
                return c
        return None

    def daily(self):
        day_of_the_year = datetime.now().timetuple().tm_yday
        receipts_count = len(self)
        daily_receipt_index = day_of_the_year % receipts_count
        return self[daily_receipt_index]

    def random(self):
        receipts_count = len(self)
        random_receipt_index = random.randint(0, receipts_count - 1)
        return self[random_receipt_index]

    def filter(self, predicate):
        filtered = []
        for c in self:
            if predicate(c):
                filtered.append(c)
        return filtered


class Response:
    def __init__(self, text, cocktail=None):
        self.text = text
        self.cocktail = cocktail


if __name__ == '__main__':
    print('Добавлено {} коктейлей'.format(len(CocktailList())))
    print('Добавлено {} кислых коктейлей'.format(len(CocktailList().filter(lambda c: c.taste.sour))))
    print('Добавлено {} крепких коктейлей'.format(len(CocktailList().filter(lambda c: c.taste.strong))))
    print('Добавлено {} фруктовых коктейлей'.format(len(CocktailList().filter(lambda c: c.taste.fruit))))
    print('Добавлено {} освежающих коктейлей'.format(len(CocktailList().filter(lambda c: c.taste.fresh))))
