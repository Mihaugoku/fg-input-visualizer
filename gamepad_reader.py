import joystickapi
import time
import threading
import __main__

num = joystickapi.joyGetNumDevs()
ret, caps, startinfo = False, None, None
for id in range(num):
    ret, caps = joystickapi.joyGetDevCaps(id)
    if ret:
        gamepad_str = f"Gamepad detected: {caps.szPname}"
        print(f"{'=' * len(gamepad_str)}\n{gamepad_str}\n{'=' * len(gamepad_str)}\n")
        ret, startinfo = joystickapi.joyGetPosEx(id)
        break
else:
    no_gamepad = "No gamepad detected. If the game is set to gamepad mode, connect one and restart this program, or set config to keyboard."
    print(f"{'=' * len(no_gamepad)}\n{no_gamepad}\n{'=' * len(no_gamepad)}\n")

axis_states = [["axis_x", 0], ["axis_y", 0], ["axis_z", 0]]
rotation_states = [["rotation_y", 0], ["rotation_x", 0], ["rotation_z", 0]]

button_states = [
    ["face_1", False],
    ["face_2", False],
    ["face_3", False],
    ["face_4", False],
    ["button_l1", False],
    ["button_r1", False],
    ["button_select", False],
    ["button_start", False],
    ["button_l3", False],
    ["button_r3", False],
    ["button_l2", False],
    ["button_r2", False]
]

joystick_threshold = 0

pov = 65535
hdir = 0
vdir = 0
dp_dir = -1

stop_event = threading.Event()


def set_joystick_threshold(threshold):
    global joystick_threshold
    joystick_threshold = min(1, max(0, threshold)) * 32768


def gamepad_main():
    global pov, hdir, vdir, dp_dir
    while not stop_event.is_set():
        time.sleep(0.005)
        # if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():  # detect ESC
        #     run = False

        ret, info = joystickapi.joyGetPosEx(id)
        if ret:
            pov = info.dwPOV
            if pov == 65535:
                dp_dir = -1
            else:
                dp_dir = pov // 4500
            translate_dpad(dp_dir)

            btns = [(1 << i) & info.dwButtons != 0 for i in range(caps.wNumButtons)]
            axisXYZ = [info.dwXpos-startinfo.dwXpos, info.dwYpos-startinfo.dwYpos, info.dwZpos-startinfo.dwZpos]
            axisRUV = [info.dwRpos-startinfo.dwRpos, info.dwUpos-startinfo.dwUpos, info.dwVpos-startinfo.dwVpos]
            for btn in range(len(btns)):
                if btns[btn] != button_states[btn][1]:
                    button_states[btn][1] = btns[btn]
                    if btns[btn] is True:
                        __main__.check_key_press(button_states[btn][0])
                    else:
                        __main__.check_key_release(button_states[btn][0])

            for axis in range(len(axisXYZ)):
                # Check for z axis (l2, r2 buttons)
                if axis == 2:
                    if axisXYZ[axis] > joystick_threshold:
                        if button_states[10][1] is False:
                            __main__.check_key_press(button_states[10][0])
                        button_states[10][1] = True
                    else:
                        if button_states[10][1] is True:
                            __main__.check_key_release(button_states[10][0])
                        button_states[10][1] = False
                    if axisXYZ[axis] < -joystick_threshold:
                        if button_states[11][1] is False:
                            __main__.check_key_press(button_states[11][0])
                        button_states[11][1] = True
                    else:
                        if button_states[11][1] is True:
                            __main__.check_key_release(button_states[11][0])
                        button_states[11][1] = False
                else:
                    if axisXYZ[axis] != axis_states[axis][1]:
                        axis_states[axis][1] = axisXYZ[axis]

            if axis_states[0][1] < -joystick_threshold:
                hdir -= 1
            elif axis_states[0][1] > joystick_threshold:
                hdir += 1

            if axis_states[1][1] < -joystick_threshold:
                vdir -= 1
            elif axis_states[1][1] > joystick_threshold:
                vdir += 1

            hdir = max(-1, min(1, hdir))
            vdir = max(-1, min(1, vdir))

            if hdir == -1:
                __main__.check_key_press(__main__.dir_config["left"])
            elif hdir == 1:
                __main__.check_key_press(__main__.dir_config["right"])
            else:
                __main__.check_key_release(__main__.dir_config["left"])
                __main__.check_key_release(__main__.dir_config["right"])

            if vdir == -1:
                __main__.check_key_press(__main__.dir_config["up"])
            elif vdir == 1:
                __main__.check_key_press(__main__.dir_config["down"])
            else:
                __main__.check_key_release(__main__.dir_config["up"])
                __main__.check_key_release(__main__.dir_config["down"])

            for axis in range(len(axisRUV)):
                if axisRUV[axis] != rotation_states[axis][1]:
                    rotation_states[axis][1] = axisRUV[axis]

            hdir = 0
            vdir = 0


def translate_dpad(dir_index):
    global hdir, vdir

    match dir_index:
        case 7 | 0 | 1:
            vdir -= 1
        case 3 | 4 | 5:
            vdir += 1

    match dir_index:
        case 1 | 2 | 3:
            hdir += 1
        case 5 | 6 | 7:
            hdir -= 1
