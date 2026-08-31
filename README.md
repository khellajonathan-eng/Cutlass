# Cutlass
Cutlass is a Python game engine focused on procedural map generation and room-based games

## Getting Sarted

## Version
1.1.2.2 - Beta
Note:  I know there is version and versioning, but here I'm outright telling you the version without anything else.

## Features
Procedural Map Generation
Room-Based navigation
Room and Global Events
Multiple Generation modes
Pathfinding
Player inventory and credits
Mod loading and API
`.cutl` files for save files and optional for mod files
Custom error handling

## Generation Modes
Cutlass currently supports **5** generation modes

#### Syntaxxing
The `generaterooms` command has its syntax going like this.
Note: This will only show the *necessary* Syntaxxing for generation. If you want to have other features such as `mode` or `loot`, please go down to the paragraph after the modes.

```py
import Cutlass
testmap = Cutlass.Map("Test Map")
testmap.generaterooms(2, "room a", "room b", "room c", "room d", "room e")
#generaterooms(exits, rooms, options)
```

### Default
Default random-based generation. Connects rooms at random.

Example:
```python
import Cutlass
testmap = Cutlass.Map("Test Map")
testmap.generaterooms(2, "room a", "room b", "room c", "room d", "room e")
#the command naturally defaults to default mode.
```

### Tree
Creates a connected tree.

Example:
```python
testmap.generaterooms(mode="tree")
#the arguments shown in default were actually the default arguments for the command. you can also just do generaterooms().
#there is now a tree room generation type in testmap.lor, which is the map's list of rooms.
```

### Hub
Creates rooms that are all connected to a central point, or a "hub".

Example:
```python
testmap.generaterooms(mode="hub.room a")
#there is now a hub room generation type in testmap.lor
#the .room a means that room a will now be the central room. hub is the only mode that has a . in its mode definition as of 1.1.2.2
```

### Linear
Creates rooms in one long line based on the order you give it.

Example:
```python
testmap.generaterooms(mode="linear")
#there is now a linear room generation type in testmap.lor
```

### Grid
My personal favorite.
Creates rooms that use a 2D map grid using coordinates that are defined by room.gridcoords.

Example:
```python
testmap.generaterooms(mode="grid")
#this now has a grid room generation type in testmap.lor, but unlike all the other modes, it uses attributes from those rooms.
```

### Generation Mode Submodes
Every mode has generation **Submodes** which can define how it is generated.
Linear has two-way and shuffled, Hub also has two-way, the list goes on.
How you use them is that they are split by slashes.
If no options are made, then it defaults to its normal mode. Linear stays the same, grid mode just places rooms randomly, etc.


Example:
```python
testmap.generaterooms(mode="linear/shuffled/twoway")
#now it has a modified version of the linear room generation type in testmap.lor
```

Note: If you ran these all side by side, it will deny you with Error 10: Cannot have duplicate rooms. If you wish to learn more about the custom error handling system, please continue further.

## Generation Modification
This is the `def` line for `generaterooms`
```python
def generaterooms(self, num=2, *ro, debug=False, hidden=None, showit=False, loot=None, needs=None, buys=None, truehide=None, mode="default"):
```
As you can see, there are a lot more than just exits, rooms and mode.
These are the room modifications (other than debug and showit) that can modify rooms.
These are what they all do.

### Generation Modifications and what they do.

`hidden` accepts a **list** of [room names].
It makes it so that when you first call diffroom() (the main tool for modification) and the command realizes you are not in a map or room, it will not be shown in the startup menu.

`loot` accepts a **dictionary** of {room names: [loot given]}. (the value ***MUST*** be a list for all modifications accepting a dictionary!)
It makes it so that when you first enter the room inside the **key**, it gives you the item(s) inside the **value** part of the dictionary and appends them to `player.inventory`

`needs` accepts a **dictionary** of {room names: [items needed]}
It makes it so that when you want to enter the room, the item(s) in the value must be in your inventory before it will let you go into the room inside the **key**.

`buys` accepts a **list** of [room names]
It makes it so that whenever you enter the room, you get into a sort of "merchant selling you their wares" scene. You choose whatever was given from `loot`, and then that gets given to your inventory.

`truehide` accepts a **dictionary** of {room names: [items needed]}
It makes it so that the room at the **key** will need the item(s) at the **value** in order to even be shown whenever you are trying to move.

Note: `needs` and `truehide` can lead to dead ends!

## Save Files and modding

As of recent updates, Cutlass now supports save/load files, and as of, well, less recent updates, it can load code onto the terminal to execute it.

### Save or Load (SoL)

Whenever you wish to save what data you have, you must do the following:
```python
#1: Use the command
SoL.saveto("this is a test file!")
#Done! :D
```
It saves it to a custom `.cutl` file (short for cutlass) with pickle serialization.
Whenever you wish to get said saved data, you must do this:
```python
SoL.loadfrom("I/don't/know/what/to/put/here/this is a test file.cutl")
#note: if you don't use .cutl files, it will shut you down with Error 34: Must use .cutl files!
```

### Mods (yes, that's what the class is called.)

When you wish to have a separate file execute code, you can do the following.

```python
Mods.loadmod("I/don't/know/what/to/put/here/whatever file you want to load.cutl")
#Note: .cutl files are not mandatory for the loadmod!
```

It will do a security check, then execute it.

OKAY, SERIOUSLY IMPORTANT NOTE: Just because it has a security check does **NOT** mean it is automatically safe. It only checks for the obvious things like exec() or import os. **ONLY** load files from whom you trust. And even if you do, you should examine the given files anyway.

## Credits
This is a solo project.
Mr. Created Everything: airbreather5277 aka mynameisajoke
## Versioning
It uses a four-part Versioning system.
REVAMP.MAJOR.MINOR.PATCH
or as I like to call it
REAL HUGE.BIGBUTNOTHUGE.PRETTYSMALLBUTSTILLWORTHNOTING.OKAYTHISISREALSMALL
Cutlass is in 1.1.2.2

## Why Cutlass?
It is a procedural map generator that could be used for many things.

Also, I just needed a name that sounds cool. Cutlass seemed nice.
