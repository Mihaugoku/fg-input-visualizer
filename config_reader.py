import configparser
import os
import re


def err(message: str):
    print(f"Error: {message}")
    exit(1)


config = configparser.ConfigParser()
config.read('config.ini')

if 'game' not in config['config'] or config['config']['game'] == '':
    err('No game found in [config].')

config_game = config['config']['game']
print(f'Using game {config_game}')

if 'keynames' not in config[f'overlay.{config_game}']:
    err('No keynames found in [overlay.{config_game}].')

game_keys = config[f'overlay.{config_game}']['keynames'].split(',')

key_index = 0


class FGKey():
    def __init__(self, keyname: str, keycode: str, asset: str, x: int, y: int):
        global key_index
        self.index = key_index
        key_index += 1

        self.keyname = keyname
        self.keycode = keycode
        self.asset = asset
        self.x = x
        self.y = y

    def __str__(self):
        return f"'{self.keyname}': Bound to '{self.keycode}', asset at '{self.asset}', position ({self.x}, {self.y})"


class ComboKey():
    def __init__(self, keycode: str, keynames: list):
        self.keycode = keycode
        self.keynames = keynames

    def __str__(self):
        return f"{self.keycode}: {self.keynames}"


def set_config_value(config_part, val, fallback):
    if val in config[config_part]:
        return config[config_part][val]
    return fallback


def read_config():
    general_config = {}

    general_config['game'] = config_game
    general_config['window_size'] = set_config_value('config', 'windowsize', '400,180')
    general_config['background'] = set_config_value('config', 'backgroundcolor', '#000000')
    general_config['chromakey'] = set_config_value('config', 'chromakey', '1')
    general_config['opacity'] = set_config_value('config', 'opacity', '0.95')
    general_config['stick_radius'] = set_config_value('config', 'stickradius', '70')

    stick_position = set_config_value('config', 'stickpos', '90,90').split(',')
    for i in range(len(stick_position)):
        stick_position[i] = min(max(0, int(stick_position[i])), 1000)
    general_config['stick_position'] = stick_position

    window_size = general_config['window_size'].split(',')
    for i in range(len(window_size)):
        window_size[i] = min(max(0, int(window_size[i])), 1000)
    general_config['window_size'] = window_size

    # Check for validity of values
    if not re.match(r"^#[0-9A-Fa-f]{6}$", general_config['background']):
        print("Invalid background color, defaulting to black")
        general_config['background'] = '#000000'

    if general_config['chromakey'] not in ('0', '1'):
        print("Invalid chromakey value, defaulting to 1 (True)")
        general_config['chromakey'] = '1'

    general_config['opacity'] = min(max(0.1, float(general_config['opacity'])), 1)
    general_config['stick_radius'] = min(max(10, int(general_config['stick_radius'])), 200)

    return general_config


def read_key_config():
    keyconfig = []

    # Directional key config
    if "keyconfig" not in config:
        err('No [keyconfig] found in config file.')

    left = config['keyconfig']['left']
    right = config['keyconfig']['right']
    up = config['keyconfig']['up']
    down = config['keyconfig']['down']

    dirconfig = {
        'left': left,
        'right': right,
        'up': up,
        'down': down
    }

    # Action key config
    for key in game_keys:
        if key not in config[f'assets.{config_game}']:
            err(f'Sprite asset for "{key}" not found in [assets.{config_game}].')

        asset_data = config[f'assets.{config_game}'][key].split(',')

        if len(asset_data) != 3:
            err(f'Sprite asset for "{key}" has incorrect format. Must be "<filename>.png,<x>,<y>".')

        asset_path = f"assets/{config_game}/{asset_data[0]}"

        x, y = 0, 0
        try:
            x, y = int(asset_data[1]), int(asset_data[2])
        except ValueError:
            err("Could not parse coordinates for sprite asset.")

        if x < 0 or x > 1000 or y < 0 or y > 1000:
            err(f'Coordinates for sprite asset for "{key}" are out of bounds (0-1000).')

        if not os.path.exists(asset_path):
            err(f'Sprite asset for "{key}" does not exist.')

        if key not in config[f'keyconfig.{config_game}']:
            err(f'Key "{key}" is not bound in [keyconfig.{config_game}].')

        key_code = config[f'keyconfig.{config_game}'][key]

        key_obj = FGKey(key, key_code, asset_path, x, y)

        keyconfig.append(key_obj)

    return [dirconfig, keyconfig]


def read_combo_config():
    combo_keys = []
    for key, value in config[f"combokeys.{config_game}"].items():
        split_keys = value.split(',')
        for k in split_keys:
            if k not in game_keys:
                err(f'Key "{k}" is not bound in [overlay.{config_game}] keynames.')

        combo_keys.append(ComboKey(key, split_keys))

    return combo_keys
