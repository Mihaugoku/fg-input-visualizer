# Fighting Game input visualizer - a tool for visualizing game input in an arcade-stick style
# Author - @mihaugoku

import tkinter as tk
import math

from pynput.keyboard import Listener
from PIL import Image, ImageTk, ImageDraw, ImageEnhance

import config_reader

config_reader.validate_configs()
config_reader.config_game = config_reader.select_game()

config = config_reader.read_config()

k = config_reader.read_key_config()
dir_config = k[0]
key_config = k[1]
combo_config = config_reader.read_combo_config()

stick_positions = {
    "left": False,
    "right": False,
    "up": False,
    "down": False
}

key_states = {}

for fg_key in key_config:
    key_states[fg_key.keyname] = False

line_trails = []

if config["chromakey"] != "0":
    config["background"] = "#000000"


def update_line_trails():
    global line_trails, window

    alpha_interval = 24

    for i in range(len(line_trails)):
        img = ImageTk.getimage(line_trails[i][0]).convert("RGBA")
        img2 = img.copy()
        img2.putalpha(max(line_trails[i][2] - alpha_interval, 0))
        img.paste(img2, img)
        img = ImageTk.PhotoImage(img)
        line_trails[i][0] = img
        line_trails[i][2] -= alpha_interval
        window.itemconfig(line_trails[i][1], image=line_trails[i][0])

    for i in reversed(range(len(line_trails))):
        if line_trails[i][2] <= 0:
            window.delete(line_trails[i][1])
            line_trails.pop(i)

    root.after(17, update_line_trails)


def create_line_trail(x1, y1, x2, y2, flip=None, **options):
    x1 += 4
    y1 += 4
    x2 += 4
    y2 += 4

    if 'alpha' in options:
        if x2 > x1:
            anchor_side_horizontal = 'w'
            x_offset = -4
        else:
            anchor_side_horizontal = 'e'
            x_offset = 4
        if y2 > y1:
            anchor_side_vertical = 'n'
            y_offset = -4
        else:
            anchor_side_vertical = 's'
            y_offset = 4
        anchor_side = anchor_side_vertical + anchor_side_horizontal

        line_x1 = 0
        line_y1 = 0
        line_x2 = abs(int(x2) - int(x1))
        line_y2 = abs(int(y2) - int(y1))

        if flip is not None:
            if flip == 'x':
                line_x1, line_x2 = line_x2, line_x1
            elif flip == 'y':
                line_y1, line_y2 = line_y2, line_y1

        alpha = int(options.pop('alpha') * 255)
        fill = options.pop('fill')
        fill = root.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (abs(int(x2) - int(x1)) + 8, abs(int(y2) - int(y1)) + 8))
        draw = ImageDraw.Draw(image)
        draw.line((line_x1, line_y1, line_x2, line_y2), fill=fill, width=10)
        img = ImageTk.PhotoImage(draw._image)
        img_object = window.create_image(x1 + x_offset, y1 + y_offset, image=img, anchor=anchor_side)
        line_trails.append([img, img_object, 255])


def redraw_stick_position():
    global key_states, window, stick, coord_tuples, stick_radius, stick_position_index, stick_positions

    stick_pos = 4

    if stick_positions["left"]:
        stick_pos -= 1
    if stick_positions["right"]:
        stick_pos += 1
    if stick_positions["up"]:
        stick_pos -= 3
    if stick_positions["down"]:
        stick_pos += 3

    old_position = stick_position_index
    stick_position_index = stick_pos
    window.moveto(stick, coord_tuples[stick_pos][0] - stick_radius, coord_tuples[stick_pos][1] - stick_radius)

    # Fix some weird trail flipping BS that i didn't feel like doing properly
    if stick_pos != old_position:
        flip = None
        if (stick_pos == 0 and old_position == 1) or (stick_pos == 1 and old_position == 0) or (stick_pos == 7 and old_position == 8) or (stick_pos == 8 and old_position == 7):
            flip = 'y'
        if (stick_pos == 3 and old_position == 0) or (stick_pos == 0 and old_position == 3) or (stick_pos == 5 and old_position == 8) or (stick_pos == 8 and old_position == 5):
            flip = 'x'
        create_line_trail(coord_tuples[old_position][0], coord_tuples[old_position][1], coord_tuples[stick_pos][0], coord_tuples[stick_pos][1], flip, fill='red', alpha=1)


def redraw_key_states():
    global btn_image_objects, window, key_states

    for fg_key in key_config:
        if key_states[fg_key.keyname]:
            window.itemconfig(btn_image_objects[fg_key.index], image=btn_image_assets_pressed[fg_key.index])
        else:
            window.itemconfig(btn_image_objects[fg_key.index], image=btn_image_assets_unpressed[fg_key.index])


def check_key_press(key):
    global key_states, stick_positions

    key = str(key).replace("'", "")

    if key == dir_config["left"]:
        stick_positions["left"] = True
    elif key == dir_config["right"]:
        stick_positions["right"] = True
    elif key == dir_config["up"]:
        stick_positions["up"] = True
    elif key == dir_config["down"]:
        stick_positions["down"] = True

    redraw_stick_position()

    for combo_key in combo_config:
        if key == combo_key.keycode:
            for fg_key in combo_key.keynames:
                key_states[fg_key] = True

    for fg_key in key_config:
        if key == f"{fg_key.keycode}":
            key_states[fg_key.keyname] = True

    redraw_key_states()


def check_key_release(key):
    global key_states

    key = str(key).replace("'", "")

    if key == dir_config["left"]:
        stick_positions["left"] = False
    elif key == dir_config["right"]:
        stick_positions["right"] = False
    elif key == dir_config["up"]:
        stick_positions["up"] = False
    elif key == dir_config["down"]:
        stick_positions["down"] = False

    redraw_stick_position()

    for combo_key in combo_config:
        if key == combo_key.keycode:
            for fg_key in combo_key.keynames:
                key_states[fg_key] = False

    for fg_key in key_config:
        if key == f"{fg_key.keycode}":
            key_states[fg_key.keyname] = False

    redraw_key_states()


# Create window
root = tk.Tk(screenName="Input Visualizer", baseName=None, className="Tk", useTk=True)

# Create button images with unpressed ones being 50% opacity
btn_image_assets_unpressed, btn_image_assets_pressed, btn_image_objects = [], [], []
for fg_key in key_config:
    img = Image.open(fg_key.asset)
    unpressed_img = Image.open(fg_key.asset)
    # unpressed_img2 = .copy()
    # unpressed_img2.brightness
    # transparent_img.paste(transparent_img2, transparent_img)
    unpressed_img = ImageEnhance.Brightness(unpressed_img).enhance(0.33)
    btn_image_assets_unpressed.append(ImageTk.PhotoImage(unpressed_img))
    btn_image_assets_pressed.append(ImageTk.PhotoImage(img))

# Set window dimensions
window_width = config["window_size"][0]
window_height = config["window_size"][1]
root.geometry(f"{window_width}x{window_height}")

# Create main canvas
window = tk.Canvas(root, width=window_width, height=window_height, highlightthickness=0, bg=config["background"])
window.pack()

# Draw arcade stick octagon, with coordinates starting from the UP position, traveling clockwise
pol_xorig = config['stick_position'][0]
pol_yorig = config['stick_position'][1]
pol_rad = int(config["stick_radius"])

polygon_coords = [
    pol_xorig + math.cos(math.degrees(45)) * pol_rad, pol_yorig - math.sin(math.degrees(45)) * pol_rad,
    pol_xorig, pol_yorig - pol_rad,
    pol_xorig - math.cos(math.degrees(45)) * pol_rad, pol_yorig - math.sin(math.degrees(45)) * pol_rad,
    pol_xorig + pol_rad, pol_yorig,
    pol_xorig - math.cos(math.degrees(45)) * pol_rad, pol_yorig + math.sin(math.degrees(45)) * pol_rad,
    pol_xorig, pol_yorig + pol_rad,
    pol_xorig + math.cos(math.degrees(45)) * pol_rad, pol_yorig + math.sin(math.degrees(45)) * pol_rad,
    pol_xorig - pol_rad, pol_yorig,
]

coord_tuples = []
coord_order = [0, 1, 2, 7, 3, 6, 5, 4]
for i in range(len(coord_order)):
    coord_tuples.append((polygon_coords[coord_order[i] * 2], polygon_coords[coord_order[i] * 2 + 1]))
coord_tuples.insert(4, (pol_xorig, pol_yorig))

octagon = window.create_polygon(polygon_coords, outline="#ffffff", fill=config["background"], width=3)

# Draw a circle at the center. This will be used to track directional keys like an arcade stick
stick_radius = 20
stick_img = Image.open("assets/btn_stick.png")
stick_imgtk = ImageTk.PhotoImage(stick_img)
stick = window.create_image(pol_xorig, pol_yorig, image=stick_imgtk, anchor="c")
window.tag_raise(stick)

# Start global key listener
listener = Listener(on_press=check_key_press, on_release=check_key_release)

listener.start()
listener.wait()

# Set up starting buttons and positions
stick_position_index = 4
redraw_stick_position()

# Create action buttons from config instead
for fg_key in key_config:
    btn_image_objects.append(window.create_image(fg_key.x, fg_key.y, image=btn_image_assets_unpressed[fg_key.index], anchor="c"))

# Set up window dragging without a title bar
lastx, lasty = 0, 0


def start_move(event):
    global lastx, lasty
    lastx = event.x_root
    lasty = event.y_root


def move_window(event):
    global lastx, lasty
    deltax = event.x_root - lastx
    deltay = event.y_root - lasty
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry("+%s+%s" % (x, y))
    lastx = event.x_root
    lasty = event.y_root


# Let the user drag the window
window.bind("<ButtonPress-1>", start_move)
window.bind('<B1-Motion>', move_window)

# Make the window borderless, always on top and chromakeyed on Windows
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", config["opacity"])
if config['chromakey'] != '0':
    root.wm_attributes("-transparentcolor", config["background"])

# Set up trail updates for moving the stick around
root.after(100, update_line_trails)

root.mainloop()

# Stop global key listener when shutting program down
listener.stop()
