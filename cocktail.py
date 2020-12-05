import json


def handler(event, context):
    text = text_or_welcome_message(event)
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': 'false'
        }
    }


def is_help_command(command):
    return command in ['помощь', 'что ты умеешь']


def is_gratitude_command(command):
    return command in ['спасибо', 'благодарю', 'благодарочка']


def text_or_welcome_message(event):
    if 'request' in event:
        request = event['request']
        if 'command' in request and is_help_command(request['command']):
            return help_message()
        elif 'command' in request and is_gratitude_command(request['command']):
            return gratitude_message()
        elif 'original_utterance' in request and len(request['original_utterance']) > 0:
            return give_receipt(request)
    return welcome_message()


def welcome_message():
    return 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой ' \
           'любимый коктейль. Расскажи, что ты хотел бы выпить.'


def help_message():
    return 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.'


def gratitude_message():
    return 'Пожалуйста. Главное - соблюдать культуру пития.'


def give_receipt(request):
    tokens = request['nlu']['tokens']
    original_utterance = request['original_utterance']
    receipt = Cocktail().find(original_utterance, tokens)
    if receipt:
        return receipt
    else:
        return 'Я пока не знаю рецепта этого коктейля'


def intro(name, value):
    return 'Чтобы приготовить коктейль {}, {}'.format(name, value)


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
                    return intro(name, record.receipt)
        return None
