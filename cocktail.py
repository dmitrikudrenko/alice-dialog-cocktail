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


def text_or_welcome_message(event):
    if 'request' in event:
        request = event['request']
        if 'command' in request and is_help_command(request['command']):
            return help_message()
        elif 'original_utterance' in request and len(request['original_utterance']) > 0:
            return give_receipt(request)
    return welcome_message()


def welcome_message():
    return 'Привет! Я твой личный бармен. Расскажу тебе, как правильно смешать ингредиенты, чтобы получился твой ' \
           'любимый коктейль. Расскажи, что ты хотел бы выпить.'


def help_message():
    return 'Я могу рассказать тебе, как приготовить твой любимый коктейль. Просто скажи его название.'


def give_receipt(request):
    tokens = request['nlu']['tokens']
    receipt = Cocktail().find(tokens)
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
    def find(self, word):
        for record in self:
            if word in record.names:
                return record.receipt
        return None


class Cocktail:
    base = CocktailBase()

    def __init__(self):
        self.base.append(CocktailRecord(
            ['дайкири', 'daiquiri'],
            'смешайте в шейкере полторы унции светлого рома, одну унцию сока лайма и половину унции сахарного сиропа'
        ))
        self.base.append(CocktailRecord(
            ['космополитен'],
            'смешайте в шейкере полторы унции цитрусовой водки, половину унции трипл-сека, половину унции сока лайма '
            'и одну унцию клюквенного морса'
        ))
        self.base.append(CocktailRecord(
            ['маргарита'],
            'смешай в шейкере две унции серебрянной текилы, одну унцию сока лайма, одну унцию трипл-сека и половину '
            'унции сахарного сиропа. Укрась бокал кружком лайма '
        ))
        self.base.append(CocktailRecord(
            ['манхэттен'],
            'в стакан для смешивания налей две унции бурбона и одну унцию красного вермута. Добавь дэш ангостуры. '
            'Наполни стакан льдом и простируй. Бокал с напитком укрась коктейльной вишней '
        ))
        self.base.append(CocktailRecord(
            ['негрони'],
            'наполни рокс кубиками льда доверху. В равных пропорциях налей в бокал красный вермут, кампари и джин. '
            'Размешай коктейльной ложкой. Укрась кружком апельсина '
        ))

    def find(self, words):
        for word in words:
            found_cocktail = self.base.find(word)
            if found_cocktail:
                return intro(word, found_cocktail)
        return None
