from datetime import date
import json
import random


def handler(event, context):
    response = get_response(event)
    alice_response = {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': response.text,
            'end_session': 'false'
        }
    }
    if response.new_session:
        alice_response['response'].update(
            {
                'buttons': [
                    {
                        'title': 'Коктейль дня'
                    },
                    {
                        'title': 'Случайный коктейль'
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
                'image_id': cocktail.image
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
        return Response(welcome_message(), new_session=True)
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
    daily_cocktail = Cocktail().daily()
    return Response('Коктейль дня - {}. {}'.format(daily_cocktail.name, intro(daily_cocktail)), daily_cocktail)


def random_receipt_response():
    random_cocktail = Cocktail().random()
    return Response('Коктейль {}. {}'.format(random_cocktail.name, intro(random_cocktail)), random_cocktail)


def query_receipt_response(request):
    tokens = request['nlu']['tokens']
    original_utterance = request['original_utterance']
    found_cocktail = Cocktail().find(original_utterance, tokens)
    return Response(intro(found_cocktail), found_cocktail)


def intro(record):
    return 'Чтобы приготовить коктейль {}, {}'.format(record.name, record.receipt)


class CocktailRecord:
    def __init__(self, name, extra_names, receipt, image, ingredients):
        self.name = name
        self.extra_names = extra_names
        self.receipt = receipt
        self.image = image
        self.ingredients = ingredients


class CocktailBase(list):
    pass


class Cocktail:
    base = CocktailBase()

    def __init__(self):
        with open("data.json", "r") as read_file:
            data = json.load(read_file)

        for obj in data:
            self.base.append(CocktailRecord(
                obj['original_name'],
                obj.get('names'),
                obj['receipt'],
                obj.get('image'),
                obj.get('ingredients')
            ))

    def find(self, phrase, words):
        for record in self.base:
            if record.name in phrase or record.name in words:
                return record

            if record.extra_names:
                for name in record.extra_names:
                    if name in phrase or name in words:
                        return record
        return None

    def daily(self):
        today = int(date.today().strftime("%d"))
        receipts_count = len(self.base)
        daily_receipt_index = max(today, receipts_count) % min(today, receipts_count)
        record = self.base[daily_receipt_index]
        return record

    def random(self):
        receipts_count = len(self.base)
        random_receipt_index = random.randint(0, receipts_count - 1)
        record = self.base[random_receipt_index]
        return record


class Response:
    def __init__(self, text, cocktail=None, new_session=False):
        self.text = text
        self.cocktail = cocktail
        self.new_session = new_session


if __name__ == '__main__':
    print('Добавлено {} коктейлей'.format(len(Cocktail().base)))
