import configparser

config = configparser.RawConfigParser()
config.read('config.ini')

owner = config.getint('bot', 'owner')
accessToken = config.get('bot', 'accesstoken')

WEBHOOK = {
    'url': config.get('webhook', 'url'),
    'secret_token': config.get('webhook', 'secret_token'),
    'certificate': open(config.get('webhook', 'certificate'), 'rb'),
}

SERVER = {
    'host': config.get('server', 'host'),
    'port': config.getint('server', 'port')
}

GROUP = dict(config.items('group'))
GROUP = {key: int(value) for key, value in GROUP.items()}
