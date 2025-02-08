import configparser
import os
import re

config = configparser.ConfigParser()
config.read('config.ini')

# Get list of games in config
config_games = []
for section_name in config.sections():
    if section_name.startswith('overlay.'):
        config_games.append(section_name[8:])

config_game = None
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


def err(message: str):
    print(f"ERROR\nError: {message}\n{(7 + len(message)) * '='}\n")
    exit(1)


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
    general_config['joystick_threshold'] = set_config_value('config', 'joystickthreshold', '0.5')
    general_config['window_position'] = set_config_value('config', 'windowpos', '0,0')

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
    global key_index, config_game
    key_index = 0

    if 'keynames' not in config[f'overlay.{config_game}']:
        err('No keynames found in [overlay.{config_game}].')

    game_keys = config[f'overlay.{config_game}']['keynames'].split(',')

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

        if "mode" not in config[f'overlay.{config_game}'] or config[f'overlay.{config_game}']['mode'] not in ("keyboard", "gamepad"):
            err(f'No input mode/wrong mode in [overlay.{config_game}] add either mode="keyboard" or "gamepad".')

        mode = config[f'overlay.{config_game}']['mode']

        if mode == "keyboard":
            if key not in config[f'keyconfig.{config_game}']:
                err(f'Key "{key}" is not bound in [keyconfig.{config_game}].')

            key_code = config[f'keyconfig.{config_game}'][key]
        elif mode == "gamepad":
            if f"joyconfig.{config_game}" not in config:
                err(f'No [joyconfig.{config_game}] found in config file.')
            if key not in config[f'joyconfig.{config_game}']:
                err(f'Button "{key}" is not bound in [joyconfig.{config_game}].')

            key_code = config[f'joyconfig.{config_game}'][key]

        key_obj = FGKey(key, key_code, asset_path, x, y)
        keyconfig.append(key_obj)

    return [dirconfig, keyconfig, mode]


def read_combo_config():
    global config_game
    game_keys = config[f'overlay.{config_game}']['keynames'].split(',')

    combo_keys = []
    mode = config[f'overlay.{config_game}']['mode']

    if mode == "keyboard":
        if f"combokeys.{config_game}" in config:
            for key, value in config[f"combokeys.{config_game}"].items():
                split_keys = value.split(',')
                # Fix for special keys being turned lowercase
                key = key.replace("key", "Key")
                for k in split_keys:
                    if k not in game_keys:
                        err(f'Key "{k}" is not bound in [overlay.{config_game}] keynames.')

                combo_keys.append(ComboKey(key, split_keys))
    elif mode == "gamepad":
        if f"joycombokeys.{config_game}" in config:
            for key, value in config[f"joycombokeys.{config_game}"].items():
                split_keys = value.split(',')
                for k in split_keys:
                    if k not in game_keys:
                        err(f'Key "{k}" is not bound in [overlay.{config_game}] keynames.')

                combo_keys.append(ComboKey(key, split_keys))

    return combo_keys


def validate_configs():
    global config_game

    validating_str = "Validating game configs..."
    print(f"{'=' * len(validating_str)}\n{validating_str}\n")
    print(f'Found {len(config_games)} games in config: {", ".join(config_games)}')

    for game in config_games:
        print(f'Checking {game} config...', end=' ')
        config_game = game
        read_key_config()
        read_combo_config()
        print('OK')

    finished_str = "Finished config validation!"
    print(f"\n{finished_str}\n{'=' * len(finished_str)}")


def select_game():
    game_selected = ""
    lastgame = ""
    if "lastusedgame" in config["config"] and config["config"]["lastusedgame"] in config_games and config["config"]["lastusedgame"] != "":
        lastgame = config["config"]["lastusedgame"]
    while game_selected not in config_games:
        if lastgame == "":
            game_selected = input("Select a game: ").strip()
        else:
            game_selected = input(f"Select a game (Default: {lastgame}): ").strip()
        if game_selected == "":
            game_selected = lastgame

    # Save last used game and write to file while preserving comments
    f = open('config.ini', 'r')
    content = f.read()
    f.close()
    content = re.sub(r'lastusedgame=.*', f"lastusedgame={game_selected}", content)
    f = open('config.ini', 'w')
    f.write(content)
    f.close()

    print(f"Using game: {game_selected}")
    return game_selected
