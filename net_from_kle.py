import os
from math import ceil

os.environ['KICAD_SYMBOL_DIR'] = '/home/e/code/keyboard/pcb/keyboard_20201130'
print(os.environ.get('KICAD_SYMBOL_DIR'))
from skidl import *
active_lib = "key_testing"

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
                    y_locs.append(-1 * current_location[1])
                    if number_of_keys <20:
                        print('current x space:', current_key_x_space, ' current key w:', current_key_width, ' h:', current_key_height)
                    mods = '' 
                    prev_key_width = current_key_width
                    prev_key_x_space = current_key_x_space
                except:
                    print('error on key:', number_of_keys)
                char = ''
            if char == '"' and quote_count == 1 and not prev_char == '\\':
                quote_count = 0
           
            prev_char = char 
        print(number_of_keys - prev_number_of_keys)
        prev_number_of_keys = number_of_keys
        number_of_rows +=1
    coords = [x_locs, y_locs]
    print(coords)
    return number_of_keys, coords



class Spec:
    num_keys, coords = coords_from_kle('layout_60.txt')
    num_rows = ceil(num_keys ** (1/2))
    num_columns = ceil(num_keys ** (1/2))
    output_pins = [5, 6, 7, 8, 9, 10, 11, 12] # corresponding to pins '2', '3', and '4' on ProMicro
    input_pins = [13, 14, 15, 16, 17, 18, 19, 20] # corresponding to A0, A1, A2

# Create a single resistor for testing connections.
test_resistor, = 1 * Part(active_lib, 'resistor', TEMPLATE, footprint='Keebio-Parts:Resistor')
test_net = Net('test_net')
test_net+= test_resistor[1]

# Create pro_micro.
pro_micro, = 1 * Part(active_lib, 'pro_micro', TEMPLATE, footprint='Keebio-Parts:ArduinoProMicro')
gnd, vcc = Net('GND'), Net('VCC')

# Create empty matrices to hold things.
def create_matrix(m):
    return [[0]*m for _ in range(m)]
switches = create_matrix(Spec.num_rows)  # Create empty matrices to hold switches and diodes.
diodes = create_matrix(Spec.num_rows) 
sd_connections = create_matrix(Spec.num_rows) # create a matrix to hold connections between switches and diodes
d_in_connections = [None] * Spec.num_columns  # create a list to hold connections between diodes and inputs 
row_connections = [None] * Spec.num_rows # Create a list for the output nets for each row.
pulldown_nets = [None] * Spec.num_columns # Create list for pulldown nets between resistors and input pins.
keys_made = 0
for i in range(Spec.num_rows): # Assume square matrix for now...
    row_connections[i] = Net('row_out' + str(i)) # initialize the row connections
    
    for j in range(Spec.num_columns):
        if not keys_made == Spec.num_keys:
            # Create switches.
            switch, = 1 * Part(active_lib, 'cherry_1u_rgb', TEMPLATE, footprint='keyboard:cherry_1u_rgb')
            switches[i][j] = switch 
            # Create diodes.
            diode, = 1 * Part(active_lib, 'diode', TEMPLATE, footprint='Diode_SMD:D_SOD-123')
            diodes[i][j] = diode 
   
            # make the row output connections 
            row_connections[i] += switches[i][j][6], pro_micro[Spec.output_pins[i]]

            # Attach a switch pin to a diode.
            sd_connections[i][j] = Net('sd' + str(i) + str(j))
            sd_connections[i][j] += switches[i][j][5], diodes[i][j][2]

       
            # Connect the other side of diode to the inputs.
            if i == 0:
                d_in_connections[j] = Net('d_in'+str(j)) # initialize the connections
            
            d_in_connections[j] += diodes[i][j][1], pro_micro[Spec.input_pins[j]] # make the connections
            keys_made += 1
print('desired number of keys:', Spec.num_keys)
print(keys_made)
generate_netlist()
