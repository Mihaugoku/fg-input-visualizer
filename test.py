import configparser

config = configparser.ConfigParser()
config.read('config.ini')

config_game = config['config']['game']

game_keys = config[f'overlay.{config_game}']['keynames'].split(',')
print(game_keys)

keyconfig = []
for key in game_keys:
    if key not in config[f'keyconfig.{config_game}']:
        print(f'Key "{key}" is not bound in [keyconfig.{config_game}]. Aborting...')
        exit(1)

    keyconfig.append(config[f'keyconfig.{config_game}'][key])
print(keyconfig)
