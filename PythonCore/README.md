# Python Core
## data.py

#### stores allof the data like X, Y shifts 

ShiftX (mm): by default 0,
indect the shift on the X axis

ShiftY (mm): by default 0,
indect the shift on the Y axis

the other properties are on the readme on master/settings

    @staticmethod 
    def set_setting(vals: dict):

gets a dict and updated the data.py properties 


    @staticmethod
    def set_up(size: np.array):
    
get the image size after croping and 
set the ShiftX, ShiftY accordingly (in mm)

## prase_nested_svg.py

convet .svg to array of lines 

get the svg line
`NestedSvgParser(<file name>).get_array()`

that will return an np.array in the next  format 

                posid
       xpos: [  ..... ]
       ypos: [  ..... ]
       

