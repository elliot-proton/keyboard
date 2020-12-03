# keyboard
A collection of scripts to create keyboard pcb files with Python and KiCAD

How to use:
1. create a keyboard layout at http://www.keyboard-layout-editor.com/
2. copy the layout to a file named `layout.txt` in the same directory as the scripts
3. run `net_from_kle.py` to create a KiCAD compatible netlist.
4. load this netlist in `PCBNEW` from within KiCAD
5. use the PCBNEW terminal to run `layout_from_kle.py` and refresh the board with `pcbnew.Refresh()`
6. route the board. Freerouting works well as an open source autorouter.

Limitations
- currently pro-micro only, so 64-key boards are the maximum.
- mounting holes or pcb mount stab holes must be done by hand.

# TODO:
- Create RGB net connections & decide on RGB control scheme
- Switch to microcontroller on board, instead of pro-micro
- Consolidate into a single program
