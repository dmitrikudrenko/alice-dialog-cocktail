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
        alice_response.update(
            {
                'user_state_update': {
                    'last_receipt': response.text
                }
            }
        )
        card = {
            'card': {
                'type': 'BigImage',
                'image_id': cocktail.image,
                'title': cocktail.name.capitalize()
            }
        }
        if cocktail.ingredients:
            card['card'].update({'description': cocktail.ingredients})  # до 255 символов
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
    elif is_repeat_command(command):
        if 'state' in event \
                and 'user' in event['state'] \
                and 'last_receipt' in event['state']['user']:
            return Response(event['state']['user']['last_receipt'])
        else:
            return Response(nothing_to_repeat_message())
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


def is_repeat_command(command):
    return command in ['повтори', 'еще раз', 'ещё раз']


def welcome_message():
    return 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой ' \
           'любимый коктейль. Расскажи, что ты хотел бы выпить. Или можешь спросить меня про коктейль дня'


def help_message():
    return 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.'


def gratitude_message():
    return 'Пожалуйста. Главное - соблюдать культуру пития.'


def unknown_message():
    return 'Я пока не знаю рецепта этого коктейля'


def nothing_to_repeat_message():
    return 'Что повторить?'


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


class Cocktail:
    def __init__(self, name, extra_names, receipt, image, ingredients, name_tts, receipt_tts):
        self.name = name
        self.extra_names = extra_names
        self.receipt = receipt
        self.image = image
        self.ingredients = ingredients
        self.name_tts = name_tts
        self.receipt_tts = receipt_tts

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
                obj['receipt'],
                obj.get('image'),
                obj.get('ingredients'),
                obj.get('name_tts'),
                obj.get('receipt_tts')
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


class Response:
    def __init__(self, text, cocktail=None):
        self.text = text
        self.cocktail = cocktail


if __name__ == '__main__':
    print('Добавлено {} коктейлей'.format(len(CocktailList())))
