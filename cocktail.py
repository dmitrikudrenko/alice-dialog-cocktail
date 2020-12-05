import json
from datetime import date


def handler(event, context):
    response = get_response(event)
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': response.text,
            'end_session': 'false'
        }
    }


def is_help_command(command):
    return command in ['помощь', 'что ты умеешь']


def is_gratitude_command(command):
    return command in ['спасибо', 'благодарю', 'благодарочка']


def is_daily_recept_command(command):
    return 'рецепт дня' in command


def get_response(event):
    if event['session']['new']:
        return Response(welcome_message())

    request = event['request']
    command = request['command']
    if is_help_command(command):
        return Response(help_message())
    elif is_gratitude_command(command):
        return Response(gratitude_message())
    elif is_daily_recept_command(command):
        return Response(daily_receipt())
    else:
        return Response(give_receipt(request))


def welcome_message():
    return 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой ' \
           'любимый коктейль. Расскажи, что ты хотел бы выпить. Или можешь спросить меня про коктейль дня'


def help_message():
    return 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.'


def gratitude_message():
    return 'Пожалуйста. Главное - соблюдать культуру пития.'


def daily_receipt():
    return Cocktail().daily()


def give_receipt(request):
    tokens = request['nlu']['tokens']
    original_utterance = request['original_utterance']
    receipt = Cocktail().find(original_utterance, tokens)
    if receipt:
        return receipt
    else:
        return 'Я пока не знаю рецепта этого коктейля'


class CocktailRecord:
    def __init__(self, names, receipt):
        self.names = names
        self.receipt = receipt


class CocktailBase(list):
    pass


class Cocktail:
    base = CocktailBase()

    def __init__(self):
        with open("data.json", "r") as read_file:
            data = json.load(read_file)

        for obj in data:
            self.base.append(CocktailRecord(
                obj['names'],
                obj['receipt']
            ))

    def find(self, phrase, words):
        for record in self.base:
            for name in record.names:
                if name in phrase or name in words:
                    return self.intro(name, record)
        return None

    def daily(self):
        today = int(date.today().strftime("%d"))
        receipts_count = len(self.base)
        daily_receipt_index = max(today, receipts_count) % min(today, receipts_count)
        record = self.base[daily_receipt_index]
        name = record.names[0]
        return 'Коктейль дня - {}. {}'.format(name, self.intro(name, record))

    @staticmethod
    def intro(name, record):
        return 'Чтобы приготовить коктейль {}, {}'.format(name, record.receipt)


class Response:
    def __init__(self, text):
        self.text = text


if __name__ == '__main__':
    print(daily_receipt())
