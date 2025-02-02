from pynput.keyboard import Listener

import asyncio
import gamepad_reader


def check_key_press(key):
    print(str(key).replace("'", ""))


print("Listening for keypresses... Press Ctrl+C to quit.")


listener = Listener(on_press=check_key_press)
listener.start()

listener.join()
