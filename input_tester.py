from pynput.keyboard import Listener

import gamepad_tester
import threading


def check_key_press(key):
    key = str(key).replace("'", "")
    print(key)
    if key.strip() == "Key.esc":
        listener.stop()
        exit(0)


print("Listening for keypresses... Press Escape or Ctrl+C to quit.")


gamepad_thread = threading.Thread(target=gamepad_tester.gamepad_tester_main, daemon=True)
gamepad_thread.start()


listener = Listener(on_press=check_key_press)
listener.start()

listener.join()
