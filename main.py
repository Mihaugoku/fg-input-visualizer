# Fighting Game input visualizer - a tool for visualizing game input in an arcade-stick style
# Author - @mihaugoku

import tkinter as tk
import math

from pynput.keyboard import Listener
from PIL import Image, ImageTk, ImageDraw

key_states = {
    "left": False,
    "right": False,
    "up": False,
    "down": False,
    "LP": False,
    "MP": False,
    "HP": False,
    "LK": False,
    "MK": False,
    "HK": False
}

line_trails = []


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
    global key_states, window, stick, coord_tuples, stick_radius, stick_position_index

    stick_pos = 4

    if key_states["left"]:
        stick_pos -= 1
    if key_states["right"]:
        stick_pos += 1
    if key_states["up"]:
        stick_pos -= 3
    if key_states["down"]:
        stick_pos += 3

    old_position = stick_position_index
    stick_position_index = stick_pos
    window.moveto(stick, coord_tuples[stick_pos][0] - stick_radius, coord_tuples[stick_pos][1] - stick_radius)

    if stick_pos != old_position:
        flip = None
        if (stick_pos == 0 and old_position == 1) or (stick_pos == 1 and old_position == 0) or (stick_pos == 7 and old_position == 8) or (stick_pos == 8 and old_position == 7):
            flip = 'y'
        if (stick_pos == 3 and old_position == 0) or (stick_pos == 0 and old_position == 3) or (stick_pos == 5 and old_position == 8) or (stick_pos == 8 and old_position == 5):
            flip = 'x'
        create_line_trail(coord_tuples[old_position][0], coord_tuples[old_position][1], coord_tuples[stick_pos][0], coord_tuples[stick_pos][1], flip, fill='red', alpha=1)


def redraw_key_states():
    global btn_images, window, key_states

    if key_states["LP"]:
        window.itemconfig(btn_images[0], image=btn_image_assets_pressed[0])
    else:
        window.itemconfig(btn_images[0], image=btn_image_assets_unpressed[0])

    if key_states["MP"]:
        window.itemconfig(btn_images[1], image=btn_image_assets_pressed[1])
    else:
        window.itemconfig(btn_images[1], image=btn_image_assets_unpressed[1])

    if key_states["HP"]:
        window.itemconfig(btn_images[2], image=btn_image_assets_pressed[2])
    else:
        window.itemconfig(btn_images[2], image=btn_image_assets_unpressed[2])

    if key_states["LK"]:
        window.itemconfig(btn_images[3], image=btn_image_assets_pressed[3])
    else:
        window.itemconfig(btn_images[3], image=btn_image_assets_unpressed[3])

    if key_states["MK"]:
        window.itemconfig(btn_images[4], image=btn_image_assets_pressed[4])
    else:
        window.itemconfig(btn_images[4], image=btn_image_assets_unpressed[4])

    if key_states["HK"]:
        window.itemconfig(btn_images[5], image=btn_image_assets_pressed[5])
    else:
        window.itemconfig(btn_images[5], image=btn_image_assets_unpressed[5])


def check_key_press(key):
    global key_states

    if str(key) == 'Key.left':
        key_states["left"] = True
    elif str(key) == 'Key.right':
        key_states["right"] = True
    elif str(key) == 'Key.up':
        key_states["up"] = True
    elif str(key) == 'Key.down':
        key_states["down"] = True

    redraw_stick_position()

    if str(key) == "'a'":
        key_states["LP"] = True
    elif str(key) == "'s'":
        key_states["MP"] = True
    elif str(key) == "'d'":
        key_states["HP"] = True
    elif str(key) == "'z'":
        key_states["LK"] = True
    elif str(key) == "'x'":
        key_states["MK"] = True
    elif str(key) == "'c'":
        key_states["HK"] = True

    redraw_key_states()


def check_key_release(key):
    global key_states

    if str(key) == 'Key.left':
        key_states["left"] = False
    elif str(key) == 'Key.right':
        key_states["right"] = False
    elif str(key) == 'Key.up':
        key_states["up"] = False
    elif str(key) == 'Key.down':
        key_states["down"] = False

    redraw_stick_position()

    if str(key) == "'a'":
        key_states["LP"] = False
    elif str(key) == "'s'":
        key_states["MP"] = False
    elif str(key) == "'d'":
        key_states["HP"] = False
    elif str(key) == "'z'":
        key_states["LK"] = False
    elif str(key) == "'x'":
        key_states["MK"] = False
    elif str(key) == "'c'":
        key_states["HK"] = False

    redraw_key_states()


# Create window
root = tk.Tk(screenName="Input Visualizer", baseName=None, className="Tk", useTk=True)

btn_image_assets_unpressed, btn_image_assets_pressed, btn_images = [], [], []
for i in range(6):
    img = Image.open(f"assets/btn_{i}.png")
    transparent_img = Image.open(f"assets/btn_{i}.png")
    transparent_img.putalpha(128)
    btn_image_assets_unpressed.append(ImageTk.PhotoImage(transparent_img))
    btn_image_assets_pressed.append(ImageTk.PhotoImage(img))

# Set window dimensions
window_width = 400
window_height = 180
root.geometry(f"{window_width}x{window_height}")

# Create main canvas
window = tk.Canvas(root, width=window_width, height=window_height, highlightthickness=0, bg="#000000")
window.pack()

# Draw an octagon of radius 50, where origin is in center
pol_xorig = window_height / 2
pol_yorig = window_height / 2
pol_rad = 70

# Octagon coordinates start from the UP position, traveling clockwise
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

octagon = window.create_polygon(polygon_coords, outline="#ffffff", width=3)

# Draw a circle at the center. This will be used to track directional keys like an arcade stick
stick_radius = 20
stick_img = Image.open("assets/btn_stick.png")
stick_imgtk = ImageTk.PhotoImage(stick_img)
stick = window.create_image(pol_xorig, pol_yorig, image=stick_imgtk, anchor="c")
window.tag_raise(stick)

# Test - listen for key input, then draw some text on the canvas
listener = Listener(on_press=check_key_press, on_release=check_key_release)

# Start global key listener
listener.start()
listener.wait()

# Set up starting buttons and positions
stick_position_index = 4

redraw_stick_position()

for x in range(6):
    btn_images.append(window.create_image(pol_xorig * 2 + 30 + 64 * (x % 3), pol_yorig - 32 + 64 * (x // 3), image=btn_image_assets_unpressed[x], anchor="c"))

# Set up window dragging without a border
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


window.bind("<ButtonPress-1>", start_move)
window.bind('<B1-Motion>', move_window)

# Make the window borderless
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.95)
root.wm_attributes("-transparentcolor", "black")

# Set up trail updates for moving the stick around
root.after(100, update_line_trails)

# Run mainloop
root.mainloop()

# Stop global key listener
listener.stop()
