# Fighting Game Input Visualizer

A simple overlay tool for visualizing your input in a fighting game.

DISCLAIMER: This program is very much still work-in-progress. It doesn't support many very important features, for example gamepad input. I will get to it some day.

## Installation

Make sure you have Python installed on your computer. As this is an interpreted, and not compiled language, you need to install the interpreter first.

Once you install Python, install the required dependencies with `pip install -r requirements.txt`. There's a few libraries that are required to read keyboard input and draw the overlay.
If you have trouble installing or don't know what to do, just run `pip install pillow pynput`. These are the only libraries required.

## Usage

Open `run.bat` to run the program. It should hopefully open an empty terminal window. Any errors will be propelled there. You should also see a default Street Fighter 6 overlay.

To dispose of the program, simply close the terminal window, or ALT-F4 the focused overlay.
Dragging is available, and configuration is encouraged.

## Configuration

Program configuration is done in the `config.ini` file. INI files follow a "[Section], key=value" structure. The file's content is as follows:

`[config]` - This is where main config variables are stored.  
`backgroundcolor` - The window's background color. Only used, if `chromakey` is 0. This value is a hex color code. Use any online color picker to pick a color. When using colors other than black, it is recommended to set `opacity` to 1 and chromakey to 0. (Default "#000000" (black))  
`opacity` - Opacity of the window, separate from chroma-key, with 0 meaning invisible, 1 being fully opaque. (Default: 0.85)  
`chromakey` - Whether window background should be transparent. Use 1 to do it automatically, or if you don't want it, or would like to do it yourself, use 0.  
`windowsize` - Size of the overlay window in "width,height" in pixels. (Default: 400,180)  
`stickpos` - Position in "width,height" of the arcade stick visualizing directional input. (Default: 90,90)  
`stickradius` - Radius of the arcade stick in pixels. (Default: 70)  

`[keyconfig]` - This is where you will set your global mappings for things like directional input. Note that some key values in input fields will have the prefix "Key.". Visit the lower "Input" section to find out more about that.

`[overlay.game]` - In this section you will specify your names for buttons. They can be anything you want, and these names will be used later to configure things like sprites, bindings and even combo-keys.  
`mode` can be either "keyboard" or "gamepad".
Example from Street Fighter 6:
```
[overlay.sf6]
mode=keyboard
keynames=lp,mp,hp,lk,mk,hk 
```
The 6 buttons used in Street Fighter, named accordingly.

`[assets.game]` - This section defines game-specific sprites for buttons. Provide assets with the .png format, along with an x and y coordinate in format "keyname=x,y". For example:"lp=btn_lightpunch.png,240,60", where "lp" is defined previously in `[overlay.game]`.

`[keyconfig.game]` - This is where you will bind key inputs to your buttons. The format is "keyname=input".  
Example:  
`lp=j` - The light punch is mapped to "J"

> [!NOTE]
> Please note that the feature below has only been tested on a generic XBox gamepad. If you have a different pad/arcade stick/hitbox/whatever, and it's not working as intended, get in contact with me at https://discord.gg/sZ9eJDKURe  

`[joyconfig.game]` - Button config for gamepads & stuff.

Gamepad buttons:  
face_1 - A (XBox), Cross (PS)  
face_2 - B (XBox), Circle (PS)  
face_3 - X (XBox), Square (PS)  
face_4 - Y (XBox), Cross (PS)  
The rest should be self-explanatory  

> [!NOTE]
> If you are unsure what the name for the input you're mapping is, run `test.bat`, which will open an input tester for you. You can then press any button, and it will give you the name of it.

`[combokeys.game]` - Combo keys simulate you pressing multiple other buttons at the same time. For example how you can bind throws to a single button. The syntax is as follows: "keycode=keyname1,keyname2,..."  
Example:  
`f=mp,mk` - Binding the "F" key to light up medium punch and kick (Drive Parry in SF6)

## Issues

As i've said, this is a work-in-progress. If you find any bugs, please report them. You may raise a Github issue, contact me on Discord, or if you want, create a pull request.
