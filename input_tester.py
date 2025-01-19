from pynput.keyboard import Listener


def check_key_press(key):
    print(str(key).replace("'", ""))
    if str(key).replace("'", "") == "Key.esc":
        exit(0)


print("Listening for keypresses... Press ESC to quit.")


listener = Listener(on_press=check_key_press)
listener.start()
listener.join()
