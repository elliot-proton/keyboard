
from pcbnew import * # import everything
import sys
kle_file = 'layout_60.txt'


def coords_from_kle(layout_file_name):

    layout_file = open(layout_file_name, 'r')
    number_of_rows, number_of_keys, prev_number_of_keys, current_key_x_space, quote_count, y_space, build_modstring  = 0, 0, 0, 0, 0, 0, 0
    key_coords, y_locs, x_locs = [],[], []
    current_location = [0,0]
    modstring, mods, prev_char = '', '', ''
    key_width = 1
    for line in layout_file.readlines():
        prev_key_width = 0
        current_location[0] = 0
        for char in line:
            if char =='{':
                build_modstring = 1
            if char =='}':
                for mod in modstring[1:].split(','):
                    if mod[0] == 'w':
                        current_key_width = float(mod.split(':')[1])
                        mods += 'w'
                    if mod[0] == 'h':
                        current_key_height = float(mod.split(':')[1])
                        mods += 'h'
                    if mod[0] == 'x':
                        current_key_x_space = float(mod.split(':')[1])
                        mods += 'x'
                    if mod[0] == 'y':
                        y_space += float(mod.split(':')[1])
                        mods += 'y'
                build_modstring = 0
                modstring = ''
            if 'w' not in mods:
                current_key_width = 1
            if 'h' not in mods:
                current_key_height = 0
            if 'x' not in mods:
                current_key_x_space = 0 
    #        if 'y' not in mods:
    #            y_space = 0
            
            if build_modstring:
                modstring += char 
    
    
            if char == '"' and quote_count == 0: # we have a new key
                number_of_keys += 1
                quote_count = 1
                try:
                    current_location[0] +=  current_key_width/2 +  prev_key_width/2+ current_key_x_space 
                    current_location[1] =  y_space +number_of_rows + 0.5 * current_key_height 
                    x_locs.append(current_location[0])
                    y_locs.append(current_location[1])
                    mods = '' 
                    prev_key_width = current_key_width
                    prev_key_x_space = current_key_x_space
                except:
                    print('error on key:', number_of_keys)
                char = ''
            if char == '"' and quote_count == 1 and not prev_char == '\\':
                quote_count = 0
           
            prev_char = char 
        prev_number_of_keys = number_of_keys
        number_of_rows +=1
    coords = [x_locs, y_locs]
    return number_of_keys, coords
board = pcbnew.GetBoard()

num_keys, coords = coords_from_kle(kle_file)
class Props:
    top_left = {'x':60e6, 'y':50e6}
    center_to_center = 19.05e6  # spacing between switches (mm)

nets = board.GetNetsByName()
for netname, net in nets.items():
    print("method2 netcode {}, name{}".format(net.GetNet(), netname))


for module in board.GetModules():
    print( "* Module: %s"%module.GetReference())
    print(module.GetValue())
    module.Value().SetVisible(True)      # set Value as Hidden
    module.Reference().SetVisible(True)   # set Reference as Visible

# assign switches to a list
switches = []
diodes = []
print(num_keys)
for i in range(num_keys):
    modref = "SW" + str(i + 1)
    switch = board.FindModuleByReference(modref)
    switches.append(switch)
    modref = "D" + str(i + 1)
    diode = board.FindModuleByReference(modref)
    diodes.append(diode)

#print(len(switches))
#for i in len(switches):
#    x = i * 20
#    switches[i].SetPosition(x, 50)
    

for i in range(num_keys):
    x = coords[0][i] * Props.center_to_center
    y = coords[1][i] * Props.center_to_center
    switches[i].SetPosition(wxPoint(x, y))
    diodes[i].Rotate(wxPoint(0,0), -90*10)
    diodes[i].Flip(wxPoint(0,0))
    diodes[i].SetPosition(wxPoint(x+10e6, y-3.45e6))

def draw_segment(x1,y1,x2,y2,layer=Edge_Cuts,thickness=0.15*IU_PER_MM):
    """Draws the line segment indicated by the x,y values
    on the given layer and with the given thickness."""
    board = GetBoard()
    ds=DRAWSEGMENT(board)
    board.Add(ds)
    ds.SetStart(wxPoint(x1,y1))
    ds.SetEnd(wxPoint(x2,y2))
    ds.SetLayer(layer)
    ds.SetWidth(max(1,int(thickness)))
    return ds


#draw_segment(50e6, 20e6, 115e6, 20e6)
#draw_segment(115e6, 20e6, 115e6, 100e6)
#draw_segment(50e6, 100e6, 115e6, 100e6)
#draw_segment(50e6, 20e6, 50e6, 100e6)

pro_micro = board.FindModuleByReference('PM1')
pro_micro.SetPosition(wxPoint(85e6,300e6))
