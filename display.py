__author__ = 'jaya'

# External Imports
from pygame import display, Color, Rect, draw
import os

# Constants
DEFAULT_HEIGHT = 32
DEFAULT_WIDTH = 64
DEFAULT_SCALE = 10
LIGHT_GREEN = Color(0x99, 0xBD, 0x2A)
DARK_GREEN = Color(0x2F, 0x63, 0x33)
WHITE = Color(0xFF, 0xFF, 0xFF)
BLACK = Color(0x00, 0x00, 0x00)
BACKGROUND_COLOR = WHITE
FOREGROUND_COLOR = BLACK
COLOURS_MAP = {
    0: BACKGROUND_COLOR,
    1: FOREGROUND_COLOR,
    'background_color': BACKGROUND_COLOR,
    'foreground_color': FOREGROUND_COLOR
}

class Chip8Screen(object):
    def __init__(self, height=DEFAULT_HEIGHT, width=DEFAULT_WIDTH, scale=DEFAULT_SCALE):
        """
        Initialize display buffer
        :param height: height of the screen.
        :param width: width of the screen
        :param scale: scale factor by which display needs to be scaled. Original CHIP-8 display is only 64*32 size.
        """
        self.height = height
        self.width = width
        self.scale = scale
        self.window = None
        self.display_buffer = [0]*width*height
        self.needs_screen_update = False

    def initialize_display(self):
        """
        Initialize pygame display.
        :return: None
        """
        display.init()
        width = self.width * self.scale
        height = self.height * self.scale
        size = (width, height)
        self.window = display.set_mode(size)
        display.set_caption('CHIP8 Emulator')
        self.clear_screen()
        self.update_display()

    def clear_display_buffer(self):
        """
        Clear display buffer
        :return: None
        """
        for i in range(len(self.display_buffer)):
            self.display_buffer[i] = 0
        self.needs_screen_update = True

    def clear_screen(self):
        """
        Clear pygame display
        :return: None
        """
        self.window.fill(COLOURS_MAP['background_color'])

    def update_display(self):
        """
        Update pygame display
        :return: None
        """
        display.flip()

    def save_pixel(self, x, y, pixel_color):
        """
        Save given color at given position in display buffer.
        :param x: x co-ordinate
        :param y: y co-ordinate
        :param pixel_color: color to use
        :return: None
        """
        index = x + (y * self.width)
        self.display_buffer[index] = pixel_color

    def get_pixel(self, x, y):
        """
        Get existing color at given position
        :param x: x co-ordinate
        :param y: y co-ordinate
        :return: color(1 or 0)
        """
        index = x + (y * self.width)
        pixel_colour = self.display_buffer[index]
        return pixel_colour

    def draw_frame(self):
        """
        Update pygame display with display buffer data
        :return: None
        """
        self.window.fill(COLOURS_MAP['background_color'])
        counter = 0
        for y in range(self.height):
            for x in range(self.width):
                x_pos = x * self.scale
                y_pos = y * self.scale
                # Skip 0(background color) as we are already clearing screen at beginning.
                if self.display_buffer[counter]:
                    pixel = Rect(x_pos, y_pos, self.scale, self.scale)
                    draw.rect(self.window, COLOURS_MAP['foreground_color'], pixel)
                counter += 1
        self.update_display()
        self.needs_screen_update = False

    def draw_frame_to_console(self):
        """
        Dumps display buffer to console.
        :return: None
        """
        self.clear_console()
        counter = 0
        for y in range(self.height):
            line = str()
            for x in range(self.width):
                colour = 'x' if self.display_buffer[counter] else ' '
                line += colour
                counter += 1
            print(line)
        self.needs_screen_update = False

    def get_debug_data(self):
        """
        Returns display buffer data as string
        :return: string containing display buffer data
        """
        counter = 0
        return_string = str()
        for y in range(self.height):
            for x in range(self.width):
                colour = 'x' if self.display_buffer[counter] else ' '
                return_string += colour
                counter += 1
            return_string += "\n"
        return return_string


    def clear_console(self):
        """
        Clear console
        :return: None
        """
        if os.name == 'nt': # Windows
            os.system('cls')
        else:
            os.system('clear')

    def destroy(self):
        """
        destroy pygame display
        :return:
        """
        display.quit()
