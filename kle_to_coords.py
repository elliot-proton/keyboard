# script to convert keyboard layout editor to coordinates to use for pcb layout scripting

# Each line is a row on the keyboard
# something in quotes is a key
# the thing inside the quotes in what is printed on the key, not really necessary for getting the layout coordinates
# {x:1} means provide 1 unit of space before the next key in ""
# {y:0.5} means provide 0.5 unites of spaces vertically before the next key in ""
import matplotlib.pyplot as plt
layout_file = open('layout.txt', 'r')
number_of_rows   = 0
number_of_keys   = 0
prev_number_of_keys   = 0
current_key_x_space = 0 
quote_count = 0
bracket_count = 0
key_width = 1
key_coords = []
y_locs = []
x_locs = []
y_space = 0
current_location = [0,0]
modstring = ''
mods = ''
prev_char = ''
build_modstring = 0
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

print(len(key_coords))
plt.scatter(x_locs, y_locs, marker='s')
plt.xlim(0, 25)
plt.ylim(-20,5)
plt.minorticks_on()
plt.grid(which = 'minor')
plt.savefig('fig.png')
