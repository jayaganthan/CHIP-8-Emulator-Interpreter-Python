# CHIP-8 Emulator/Interpreter

## What is CHIP-8?
As per [Wikpedia](https://en.wikipedia.org/wiki/CHIP-8)
>CHIP-8 is an interpreted programming language, developed by Joseph Weisbecker. It was initially used on the COSMAC VIP and Telmac 1800 8-bit microcomputers in the mid-1970s. CHIP-8 programs are run on a CHIP-8 virtual machine. It was made to allow video games to be more easily programmed for these computers.

This is a simple emulator writen in Python to emulate CHIP-8 virtual machine. It works on both Python 3 and 2.7.

## Requirements
Script uses pygame module for display and sound.
Pygame can be easily insatalled using pip.
```
pip install pygame
```
Pygame website - https://www.pygame.org/news

## Screenshots
![chip-8-screenshot](/screenshots/chip-8.JPG?raw=true "CHIP-8")
![ping-pong-screenshot](/screenshots/ping-pong.JPG?raw=true "Ping Pong")
![missile-screenshot](/screenshots/missile.JPG?raw=true "Missile")

## Keyboard 
Original CHIP-8 keyboard had 16 keys. <br>
**CHIP-8 Keyboard layout** <br>
| 1 | 2 | 3 | C | <br>      
| 4 | 5 | 6 | D | <br>
| 7 | 8 | 9 | E | <br>
| A | 0 | B | F | <br>
    
**Mapped to PC keyboard** <br>
| 1 | 2 | 3 | 4 | <br>      
| Q | W | E | R | <br>
| A | S | D | F | <br>
| Z | X | C | V | <br>

## Technical Reference
If you would like to know more about technical specifications please refer the below website.
This is a excellent refernce by Cowgod which will easily help you to get started.
http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

## Usage
```
app.py <PATH_TO_ROM>
```

## Roms
I have included only test ROMS in this repository. A simple google search will get you roms for games like PONG, INVADERS, etc.

**Test Roms included in this repository:**
1. Rom to test all opcodes - Taken from this repo - [Link](https://github.com/corax89/chip8-test-rom). Credits to [corax89](https://github.com/corax89)
2. BC_test - Taken from - [Link](https://slack-files.com/T3CH37TNX-F3RF5KT43-0fb93dbd1f) - Credits to author BestCoder. Test documentation - [Link](https://slack-files.com/T3CH37TNX-F3RKEUKL4-b05ab4930d)
3. Sample - Simple test to print stored hex sprites - Taken from repo - [Link](https://github.com/giawa/chip8) - Credits to [giawa](https://github.com/giawa)

## PR
PRs are welcome for any improvements.

## License
MIT
