import threading

from pynput.keyboard import Listener

from modules import gamepad_tester


def check_key_press(key):
    key = str(key).replace("'", "")
    if key.strip() == "Key.esc":
        listener.stop()
        gamepad_tester.stop_event.set()
        gamepad_thread.join()
        print("Exiting...")
        exit(0)
    print(key)


print("Listening for keypresses... Press Escape or Ctrl+C to quit.")


gamepad_thread = threading.Thread(target=gamepad_tester.gamepad_tester_main, daemon=True)
gamepad_thread.start()


listener = Listener(on_press=check_key_press)
listener.start()

listener.join()
