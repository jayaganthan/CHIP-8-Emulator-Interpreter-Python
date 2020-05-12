__author__ = "jaya"

# External imports
import pygame
import sys

# local imports
from log import create_logger
from display import Chip8Screen
from cpu import CPU

# set up logger
logger = create_logger(__name__)

# set logging level
DEBUG = 10
NOTSET = 0
logger.setLevel(NOTSET)

def main_loop(binary):
    # initialize pygame display
    ch8_screen = Chip8Screen(scale=10)
    ch8_screen.initialize_display()

    # initialize registers and memory
    cpu = CPU(binary=binary, screen=ch8_screen, sound='pong.wav')

    # Load and validate binary. set PC.
    cpu.initialize_cpu()

    # game loop
    while cpu.is_running:
        # execute one instruction and increment PC
        cpu.execute_one_instruction()

        # print debug data
        logger.debug(cpu.get_debug_data())

        # update display if required
        if cpu.screen.needs_screen_update:
            cpu.screen.draw_frame()

        # Check for keyboard events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                ascii_key = event.key
                cpu.update_keys_pressed(ascii_key, event.type)
            if event.type == pygame.QUIT:
                cpu.is_running = False
                cpu.destroy_display()

        # For smooth frame rates
        pygame.time.wait(1)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main_loop(binary=sys.argv[1])
    else:
        print("USAGE: app.py <ROM_PATH>")


