# PrusaUga
#### Make your own drawing on any flat cake, even if you suck at drawing


## Adding to console

`console.py` is the console file, you should do a little twicks in the file acording to your system.

if you are in linux you can add alias file to make your console lines shorter as such:

 `alias prusa-uga='<the python file [which python]> /<file name>/PrushaUga/console.py'`

then add the alias_config file to .bashrc like so

`source ~/<file name>/alias_config.bash`

## How it works 

#### Take an svg path file in input it the svg path will be converted to gcode

## Setting

make sure you input the right settings `-s <version (float)>`

you can create your own settings by `--add <version (float)>, <path>` 
then you can edit your settings by 

`--edit <version (float)> --prop <property (string)> --value <value (type acording to the property)`

to remove a setting `--remove <version (float)>`

view your setteing list by `--list` and view a pasific setting `--show <vesion (float)>`

## Input, Writing & Ploting

You can plot your own drawings using matplotlib by `-p`

writing to a file is very simple just write `-w <path/(path + file name)>` the slicer will write two gcodes into the file

1. the OUTLINE than make sure that you are in staying inside the canvas
2. the acutal gcode. it can be viewed by sites like <link>https://ncviewer.com/</link>

You can input files by `-i <path + file name>.svg`

## Creating a new setting 

if you mant to create your own settings (mainly to change the printing resolution) you first create  your setting file (depends on your plagins) by default it 

`{
  "LineThickness": 0.5, // cm
"DrawingSize": [20, 20], // cm
  "HeadSpeedRatio": 0.125, // mm per mm
  "PenUpFore": 2,
  "PrintingSpeedFactor": 4,
}`

LineThickness: how thick is your Lines in cm (metter only in .PNG)

DrawingSize: your drawing size cm (Metter only in .PNG)

HeadSpeedRatio: how fast the head is 'pooping' the suse 

PenUpFore: how much to wait after a penup

PrintingSpeedFactor: the printing speed 

## Comments

.PNG support is 'working' but it lokes way better in .SVG

there is no UI yet but I would add it sometimes
