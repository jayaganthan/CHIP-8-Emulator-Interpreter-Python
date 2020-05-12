__author__ = 'jaya'

# External imports
import time
import pygame
from random import randrange

# Local imports
from log import create_logger

# Setup logger
logger = create_logger(__name__)

# Set logging level
DEBUG = 10
NOTSET = 0
logger.setLevel(NOTSET)

class CPU(object):

    def __init__(self, binary='roms/PONG', screen=None, sound='pong.wav'):
        """
        Method to initialize CPU with required buffers
        and registers.
        :param binary: Path to binary file.
        :param screen: Pygame screen object.
        """
        self.is_running = False
        self.total_memory = 4096  # 4096 Bytes - 4kb
        self.memory_buffer = bytearray([0]*self.total_memory)
        self.registers = CPU.Registers()
        self.program_counter = 0
        self.stack = [0] * 16
        self.binary_file = binary
        self.binary_size_in_bytes = 0
        self.program_end_point = 0
        self.screen = screen
        # This dictionary is organized to resemble the 1977 COSMAC VIP's keyboard
        self.keyboard_mapping = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
        }
        self.keys_pressed = [0] * 16
        self.hex_to_binary_display = {
            0x0: [0xF0, 0x90, 0x90, 0x90, 0xF0],
            0x1: [0x20, 0x60, 0x20, 0x20, 0x70],
            0x2: [0xF0, 0x10, 0xF0, 0x80, 0xF0],
            0x3: [0xF0, 0x10, 0xF0, 0x10, 0xF0],
            0x4: [0x90, 0x90, 0xF0, 0x10, 0x10],
            0x5: [0xF0, 0x80, 0xF0, 0x10, 0xF0],
            0x6: [0xF0, 0x80, 0xF0, 0x90, 0xF0],
            0x7: [0xF0, 0x10, 0x20, 0x40, 0x40],
            0x8: [0xF0, 0x90, 0xF0, 0x90, 0xF0],
            0x9: [0xF0, 0x90, 0xF0, 0x10, 0xF0],
            0xA: [0xF0, 0x90, 0xF0, 0x90, 0x90],
            0xB: [0xE0, 0x90, 0xE0, 0x90, 0xE0],
            0xC: [0xF0, 0x80, 0x80, 0x80, 0xF0],
            0xD: [0xE0, 0x90, 0x90, 0x90, 0xE0],
            0xE: [0xF0, 0x80, 0xF0, 0x80, 0xF0],
            0xF: [0xF0, 0x80, 0xF0, 0x80, 0x80]
        }
        self.current_instruction = None
        self.function_map = {
            0x0: self.zero,
            0x1: self.one,
            0x2: self.two,
            0x3: self.three,
            0x4: self.four,
            0x5: self.five,
            0x6: self.six,
            0x7: self.seven,
            0x8: self.eight,
            0x9: self.nine,
            0xA: self.a,
            0xB: self.b,
            0xC: self.c,
            0xD: self.d,
            0xE: self.e,
            0xF: self.f
        }
        self.cpu_cycle_start_time = 0
        self.cpu_cycle_end_time = 0
        # shift_Vy is a compatibility flag that can be toggled off/on
        # shift VX instead of VY. Check instructions 8XY6 and 8XYE. Many games
        # like "BLINKY" requires it off
        self.shift_Vy = False
        self.initialize_sound(sound)

    def initialize_sound(self, music_file):
        """
        Initialize pygame music
        :param music_file: path to music file
        :return: None
        """
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)

    def play_music(self):
        """
        Beep or play music once
        :return: None
        """
        pygame.mixer.music.play()

    def destroy_display(self):
        """
        Destroy pygame display object
        :return: None
        """
        self.screen.destroy()

    def get_debug_data(self):
        """
        Dump CPU Memory and registers for easy debugging.
        :return: String containing all the data
        """
        return_string = str()
        return_string += "\nOpcode Executed: 0x{:04X}, x: 0x{:01X}, y: 0x{:01X}, kk: 0x{:02X}, nnn: 0x{:03X}, n: 0x{:01X}\n".\
            format(self.current_instruction.opcode, self.current_instruction.x, self.current_instruction.y,
                   self.current_instruction.kk, self.current_instruction.nnn, self.current_instruction.n)
        return_string += "Stack: {}\n".format(' '.join(map(hex,self.stack)))
        return_string += "Program Counter: 0x{:04X}\n".format(self.program_counter)
        return_string += "V Registers: {}\n".format(' '.join(map(hex,self.registers.v)))
        return_string += "Instruction register: 0x{:04X}\n".format(self.registers.i)
        return_string += "Delay timer: {}\n".format(self.registers.delay_timer)
        return_string += "Sound timer: {}\n".format(self.registers.sound_timer)
        return_string += "Keys pressed: {}\n".format(' '.join(map(str,self.keys_pressed)))
        # return_string += "Display: \n"
        # if self.screen.needs_screen_update:
        #     return_string += self.screen.get_debug_data()
        return return_string

    def initialize_cpu(self):
        """
        Validate the given binary, initialize fonts and set PC
        :return: None
        """
        logger.debug("Initializing CPU")
        self.copy_fonts_to_memory()
        self.validate_binary()
        self.process_binary()
        logger.debug("Set Program counter to Memory address 512(0x200)")
        self.program_counter = 0x200
        logger.debug("CPU stared running")
        self.is_running = True

    def copy_fonts_to_memory(self):
        """
        Copy default hex sprite to memory
        :return:
        """
        logger.debug("Copying hex fonts to memory")
        index = 0
        for key in range(16):
            self.memory_buffer[index: index+5] = self.hex_to_binary_display[key]
            index += 5
        logger.debug("Fonts copied to memory successfully")

    def validate_binary(self):
        """
        Validate if all the opcodes are valid in given binary.
        :return:
        """
        logger.debug("Validating binary {}".format(self.binary_file))
        fh = open(self.binary_file, 'rb')
        contents = bytearray(fh.read())
        logger.debug("Size of binary: 0x{:02X}({}) bytes".format(len(contents), len(contents)))
        count = 0
        while count < len(contents)-1:
            opcode = (contents[count] << 8) | (contents[count+1])
            lookup_opcode = (opcode & 0xf000) >> 12
            if lookup_opcode in self.function_map:
                count += 2
                continue
            else:
                raise Exception("Invalid opcode 0x{:04x} at location {}".format(opcode, count))
        logger.debug("Validated binary successfully. No Errors")

    def process_binary(self):
        """
        Save binary contents to memory
        :return: None
        """
        logger.debug("Processing binary {}".format(self.binary_file))
        fh = open(self.binary_file, 'rb')
        contents = bytearray(fh.read())
        self.binary_size_in_bytes = len(contents)
        logger.debug("Binary size in bytes: 0x{:02X}({})".format(self.binary_size_in_bytes, self.binary_size_in_bytes))
        logger.debug("Copying binary contents to memory")
        self.memory_buffer[0x200: 0x200 + self.binary_size_in_bytes] = contents[:]
        self.program_end_point = 0x200+self.binary_size_in_bytes
        logger.debug("Binary copied to memory successfully")

    def update_keys_pressed(self, ascii_key, event_type):
        """
        Update key press events for given key
        :param ascii_key: ASCII value of pressed key. Get it from Pygame constants.
        :param event_type: Key up or down event
        :return: None
        """
        if ascii_key in self.keyboard_mapping:
            logger.debug("{} is pressed".format(ascii_key))
            key = self.keyboard_mapping[ascii_key]
            if event_type == pygame.KEYDOWN:
                self.keys_pressed[key] = 1
            elif event_type == pygame.KEYUP:
                self.keys_pressed[key]  = 0

    def execute_one_instruction(self):
        """
        Executes one CPU instruction
        Increments program counter after execution.
        :return: None
        """
        if self.program_counter <= self.program_end_point:
            logger.debug("Execute one instruction")
            # Each opcode is 2 bytes
            opcode = (self.memory_buffer[self.program_counter] << 8) | (self.memory_buffer[self.program_counter+1])
            self.current_instruction = CPU.CurrentInstruction(opcode)
            self.execute_opcode()
            self.cpu_cycle_end_time = time.time()
            # self.current_instruction.clear()
            if (self.cpu_cycle_end_time - self.cpu_cycle_start_time) >= 1/60:
                if self.registers.delay_timer > 0:
                    self.registers.delay_timer -= 1

                if self.registers.sound_timer > 0:
                    self.registers.sound_timer -= 1
                    self.play_music()
                self.cpu_cycle_start_time = self.cpu_cycle_end_time
            self.program_counter += 2
        else:
            logger.debug("Program reached end. Stop CPU execution")
            self.is_running = False

    def execute_opcode(self):
        """
        Execute opcode pointed by current instruction
        :return: None
        """
        logger.debug("Current opcode: 0x{:04X}".format(self.current_instruction.opcode))
        lookup_opcode = (self.current_instruction.opcode & 0xf000) >> 12
        logger.debug("Lookup code: 0x{:01X}".format(lookup_opcode))
        self.lookup_and_execute_opcode(lookup_opcode)

    def lookup_and_execute_opcode(self, lookup_opcode):
        """
        Execute opcode if there is a function to mapped to it. Else fail.
        :param lookup_opcode: lookup code to find the function.
        :return: None
        """
        if lookup_opcode in self.function_map:
            self.function_map[lookup_opcode]()
        else:
            logger.debug("Unable to find function for opcode: 0x{:04X}".format(lookup_opcode))
            raise Exception("Unable to find function for opcode: 0x{:04X}".format(lookup_opcode))

    def read_n_bytes_from_memory(self, address, number_of_bytes):
        """
        Read n number of bytes from memory starting at given address
        :param address: Address to start reading
        :param number_of_bytes: Number of bytes to read
        :return: Data read at given location.
        """
        logger.debug("Reading {} bytes from address 0x{:03X}".format(number_of_bytes, address))
        return self.memory_buffer[address: address+number_of_bytes]

    def convert_number_to_binary_list(self, number):
        """
        Convert given decimal number to binary number.
        Parse the binary number and store each bits in a list at same order.
        Example: 0xF2 will be converted to [1,1,1,1,0,0,1,0]
        :param number: Decimal/Hex number
        :return: List representation of given number in binary
        """
        return_list = list()
        for i in range(7, -1, -1):
            bit = (number & (1 << i)) >> i # extract each bit from bit 7 to bit 0
            ret = 1 if bit else 0
            return_list.append(ret)
        return return_list

    def convert_hex_sprite_to_binary_list(self, hex_list):
        """
        Convert list of hex numbers to binary list
        Example: [0xF0, 0xF2] will be converted to = [[1,1,1,1,0,0,0,0], [1,1,1,1,0,0,1,0]]
        :param hex_list: list of hex numbers
        :return: List containing converted numbers to binary list
        """
        return_list = list()
        for hex_number in hex_list:
            return_list.append(self.convert_number_to_binary_list(hex_number))
        return return_list

    def save_sprite_to_display_buffer(self, x_pos, y_pos, sprite_data):
        """
        Saves given sprite data at display buffer. Image is not drawn
        immediately to the screen. Is is only draw while drawing the entire
        frame at the end of CPU cycle.
        :param x_pos: x co-ordinate in display
        :param y_pos: y co-ordinate in display
        :param sprite_data: sprite data in binary format
        :return: None
        """
        sprite = self.convert_hex_sprite_to_binary_list(sprite_data)
        logger.debug("Draw sprite at (x,y) => ({},{})".format(x_pos, y_pos))
        self.registers.v[0xF] = 0
        for row in range(len(sprite)):
            bits = sprite[row]
            for column in range(len(bits)):
                x = column + x_pos
                y = row + y_pos
                # handle pixel roll over
                if x > self.screen.width - 1: x = x % self.screen.width
                if y > self.screen.height - 1: y = y % self.screen.height
                # logger.debug("(sprite_x, sprite_y) => ({},{}".format(x,y))
                new_pixel_color = 1 if bits[column] else 0
                existing_pixel_color = self.screen.get_pixel(x,y)

                if (existing_pixel_color & new_pixel_color) == 1:
                        self.registers.v[0xF] = 1
                self.screen.save_pixel(x, y, existing_pixel_color^new_pixel_color)

        self.screen.needs_screen_update = True

    def zero(self):
        if self.current_instruction.opcode == 0x00e0:
            """
            00E0 - CLS
            Clear the display.
            """
            logger.debug("CLS")
            self.screen.clear_display_buffer()

        elif self.current_instruction.opcode == 0x00ee:
            """
            00EE - RET
            Return from a subroutine.
            The interpreter sets the program counter to the address at the top of the stack,
            then subtracts 1 from the stack pointer.
            """
            logger.debug("RET")
            self.program_counter = self.stack.pop()
        else:
            """
            0nnn - SYS addr
            Jump to a machine code routine at nnn.
            This instruction is only used on the old computers on which Chip-8 was originally implemented.
            It is ignored by modern interpreters.
            """
            logger.debug("SYS 0x{:03X}".format(self.current_instruction.nnn))
            # just ignore for now
            pass

    def one(self):
        """
        1nnn - JP addr
        Jump to location nnn.
        The interpreter sets the program counter to nnn.
        """
        logger.debug("JP 0x{:03X}".format(self.current_instruction.nnn))
        self.program_counter = self.current_instruction.nnn
        self.program_counter -= 2 # account for +2 at end

    def two(self):
        """
        2nnn - CALL addr
        Call subroutine at nnn.
        The interpreter increments the stack pointer, then puts the current PC on the top of the stack.
        The PC is then set to nnn.
        """
        logger.debug("CALL 0x{:03X}".format(self.current_instruction.nnn))
        self.stack.append(self.program_counter)
        self.program_counter = self.current_instruction.nnn
        self.program_counter -= 2 # to adjust +2 at end

    def three(self):
        """
        3xkk - SE Vx, byte
        Skip next instruction if Vx = kk.
        The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
        """
        logger.debug("SE V{:01X}, 0x{:02X}".format(self.current_instruction.x, self.current_instruction.kk))
        if self.registers.v[self.current_instruction.x] == self.current_instruction.kk:
            self.program_counter += 2

    def four(self):
        """
        4xkk - SNE Vx, byte
        Skip next instruction if Vx != kk.
        The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
        """
        logger.debug("SE V{:01X}, 0x{:02X}".format(self.current_instruction.x, self.current_instruction.kk))
        if self.registers.v[self.current_instruction.x] != self.current_instruction.kk:
            self.program_counter += 2

    def five(self):
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy.
        The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
        """
        logger.debug("SE V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
        if self.registers.v[self.current_instruction.x] == self.registers.v[self.current_instruction.y]:
            self.program_counter += 2

    def six(self):
        """
        6xkk - LD Vx, byte
        Set Vx = kk.
        The interpreter puts the value kk into register Vx.
        """
        logger.debug("LD V{:01X}, 0x{:02X}".format(self.current_instruction.x, self.current_instruction.kk))
        self.registers.v[self.current_instruction.x] = self.current_instruction.kk

    def seven(self):
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk.
        Adds the value kk to the value of register Vx, then stores the result in Vx.
        """
        logger.debug("ADD V{:01X}, 0x{:02X}".format(self.current_instruction.x, self.current_instruction.kk))
        self.registers.v[self.current_instruction.x] += self.current_instruction.kk
        self.registers.v[self.current_instruction.x] &= 0xFF # truncate to 8 bits

    def eight(self):
        if self.current_instruction.n == 0:
            """
            8xy0 - LD Vx, Vy
            Set Vx = Vy.
            Stores the value of register Vy in register Vx.
            """
            logger.debug("LD V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            self.registers.v[self.current_instruction.x] = self.registers.v[self.current_instruction.y]
        elif self.current_instruction.n == 1:
            """
            8xy1 - OR Vx, Vy
            Set Vx = Vx OR Vy.
            Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx.
            A bitwise OR compares the corresponding bits from two values, and if either bit is 1,
            then the same bit in the result is also 1. Otherwise, it is 0.
            """
            logger.debug("OR V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            self.registers.v[self.current_instruction.x] |= self.registers.v[self.current_instruction.y]
        elif self.current_instruction.n == 2:
            """
            8xy2 - AND Vx, Vy
            Set Vx = Vx AND Vy.
            Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx.
            A bitwise AND compares the corresponding bits from two values, and if both bits are 1,
            then the same bit in the result is also 1. Otherwise, it is 0.
            """
            logger.debug("AND V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            self.registers.v[self.current_instruction.x] &= self.registers.v[self.current_instruction.y]
        elif self.current_instruction.n == 3:
            """
            8xy3 - XOR Vx, Vy
            Set Vx = Vx XOR Vy.
            Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx.
            An exclusive OR compares the corresponding bits from two values, and if the bits are not both the same,
            then the corresponding bit in the result is set to 1. Otherwise, it is 0.
            """
            logger.debug("XOR V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            self.registers.v[self.current_instruction.x] ^= self.registers.v[self.current_instruction.y]
        elif self.current_instruction.n == 4:
            """
            8xy4 - ADD Vx, Vy
            Set Vx = Vx + Vy, set VF = carry.
            The values of Vx and Vy are added together.
            If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0.
            Only the lowest 8 bits of the result are kept, and stored in Vx.
            """
            logger.debug("ADD V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            self.registers.v[self.current_instruction.x] += self.registers.v[self.current_instruction.y]
            if (self.registers.v[self.current_instruction.x] > 0xFF):
                self.registers.v[0xF] = 1
            else:
                self.registers.v[0xF] = 0
            self.registers.v[self.current_instruction.x] &= 0xFF # truncate to 8 bits
        elif self.current_instruction.n == 5:
            """
            8xy5 - SUB Vx, Vy
            Set Vx = Vx - Vy, set VF = NOT borrow.
            If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
            """
            logger.debug("SUB V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            if self.registers.v[self.current_instruction.x] > self.registers.v[self.current_instruction.y]:
                self.registers.v[0xF] = 1
            else:
                self.registers.v[0xF] = 0
            self.registers.v[self.current_instruction.x] -= self.registers.v[self.current_instruction.y]
            self.registers.v[self.current_instruction.x] &= 0xFF # truncate to 8 bits
        elif self.current_instruction.n == 6:
            """
            8xy6 - SHR Vx {, Vy}
            Set Vx = Vx SHR 1.
            If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
            """
            logger.debug("SHR My V{:01X}".format(self.current_instruction.x))
            if self.shift_Vy:
                self.registers.v[0xF] = self.registers.v[self.current_instruction.y] & 0x01
                self.registers.v[self.current_instruction.x]  = self.registers.v[self.current_instruction.y] >> 1
            else:
                self.registers.v[0xF] = self.registers.v[self.current_instruction.x] & 0x01
                self.registers.v[self.current_instruction.x] >>= 1
        elif self.current_instruction.n == 7:
            """
            8xy7 - SUBN Vx, Vy
            Set Vx = Vy - Vx, set VF = NOT borrow.
            If Vy > Vx, then VF is set to 1, otherwise 0.
            Then Vx is subtracted from Vy, and the results stored in Vx.
            """
            logger.debug("SUBN V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
            if self.registers.v[self.current_instruction.y] > self.registers.v[self.current_instruction.x]:
                self.registers.v[0xF] = 1
            else:
                self.registers.v[0xF] = 0
            self.registers.v[self.current_instruction.x] = self.registers.v[self.current_instruction.y] - self.registers.v[self.current_instruction.x]
            self.registers.v[self.current_instruction.x] &= 0xFF # truncate to 8 bits
        elif self.current_instruction.n == 0xe:
            """
            8xyE - SHL Vx {, Vy}
            Set Vx = Vx SHL 1.
            If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0.
            Then Vx is multiplied by 2.
            """
            logger.debug("SHL V{:01X}".format(self.current_instruction.x))
            if self.shift_Vy:
                self.registers.v[0xF] = 1 if (self.registers.v[self.current_instruction.y] & 0x80) else 0
                self.registers.v[self.current_instruction.x] = self.registers.v[self.current_instruction.y] << 1
            else:
                self.registers.v[0xF] = 1 if(self.registers.v[self.current_instruction.x] & 0x80) else 0
                self.registers.v[self.current_instruction.x] = self.registers.v[self.current_instruction.x] << 1
            self.registers.v[self.current_instruction.x] &= 0xFF # truncate to 8 bits

    def nine(self):
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy.
        The values of Vx and Vy are compared, and if they are not equal,
        the program counter is increased by 2.
        """
        logger.debug("SNE V{:01X}, V{:01X}".format(self.current_instruction.x, self.current_instruction.y))
        if self.registers.v[self.current_instruction.x] != self.registers.v[self.current_instruction.y]:
            self.program_counter += 2

    def a(self):
        """
        Annn - LD I, addr
        Set I = nnn.
        The value of register I is set to nnn.
        """
        logger.debug("LB I, 0x{:03X}".format(self.current_instruction.nnn))
        self.registers.i = self.current_instruction.nnn

    def b(self):
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0.
        The program counter is set to nnn plus the value of V0.
        """
        logger.debug("JP V0, 0x{:03X}".format(self.current_instruction.nnn))
        self.program_counter = self.current_instruction.nnn + self.registers.v[0]
        self.program_counter -= 2 # account for +2 at the end

    def c(self):
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk.
        The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk.
        The results are stored in Vx. See instruction 8xy2 for more information on AND.
        """
        logger.debug("RND V{:01X}, byte".format(self.current_instruction.x))
        self.registers.v[self.current_instruction.x] = randrange(0,255) & self.current_instruction.kk

    def d(self):
        """
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        The interpreter reads n bytes from memory, starting at the address stored in I.
        These bytes are then displayed as sprites on screen at coordinates (Vx, Vy).
        Sprites are XORed onto the existing screen. If this causes any pixels to be erased,
        VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it
        is outside the coordinates of the display, it wraps around to the opposite side of the screen.
        See instruction 8xy3 for more information on XOR, and section 2.4,
        Display, for more information on the Chip-8 screen and sprites.
        """
        logger.debug("DRW V{:01X}, V{:01X}, 0x{:03X}".format(self.current_instruction.x, self.current_instruction.y, self.current_instruction.n))
        sprite_data = self.read_n_bytes_from_memory(self.registers.i , self.current_instruction.n)
        self.save_sprite_to_display_buffer(self.registers.v[self.current_instruction.x], self.registers.v[self.current_instruction.y], sprite_data)

    def e(self):
        if (self.current_instruction.opcode & 0x00ff) == 0x9e:
            """
            Ex9E - SKP Vx
            Skip next instruction if key with the value of Vx is pressed.
            Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position,
            PC is increased by 2.
            """
            logger.debug("SKP V{:01X}".format(self.current_instruction.x))
            key_to_check = self.registers.v[self.current_instruction.x]
            if self.keys_pressed[key_to_check] == 1:
                self.program_counter += 2
        else:
            """
            ExA1 - SKNP Vx
            Skip next instruction if key with the value of Vx is not pressed.
            Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position,
            PC is increased by 2.
            """
            logger.debug("SKNP V{:01X}".format(self.current_instruction.x))
            key_to_check = self.registers.v[self.current_instruction.x]
            if self.keys_pressed[key_to_check] == 0:
                self.program_counter += 2  # CHECK-THIS

    def f(self):
        if self.current_instruction.kk == 0x07:
            """
            Fx07 - LD Vx, DT
            Set Vx = delay timer value.
            The value of DT is placed into Vx.
            """
            logger.debug("LD V{:01X}, DT".format(self.current_instruction.x))
            self.registers.v[self.current_instruction.x] = self.registers.delay_timer
        elif self.current_instruction.kk == 0x0A:
            """
            Fx0A - LD Vx, K
            Wait for a key press, store the value of the key in Vx.
            All execution stops until a key is pressed, then the value of that key is stored in Vx.
            """
            logger.debug("LD V{:01X}, K".format(self.current_instruction.x))
            logger.debug("Wait for key press")

            for index in range(16):
                if self.keys_pressed[index]:
                    logger.debug("Key {} is pressed".format(index))
                    self.registers.v[self.current_instruction.x] = index
                    break
            else:
                # if no key is pressed execute the same instruction again and again
                # until a key is pressed
                self.program_counter -= 2 # account for +2 at end of cycle

        elif self.current_instruction.kk == 0x15:
            """
            Fx15 - LD DT, Vx
            Set delay timer = Vx.
            DT is set equal to the value of Vx.
            """
            logger.debug("LD DT, V{:01X}".format(self.current_instruction.x))
            self.registers.delay_timer = self.registers.v[self.current_instruction.x]
        elif self.current_instruction.kk == 0x18:
            """
            Fx18 - LD ST, Vx
            Set sound timer = Vx.
            ST is set equal to the value of Vx.
            """
            logger.debug("LD ST, V{:01X}".format(self.current_instruction.x))
            self.registers.sound_timer = self.registers.v[self.current_instruction.x]
        elif self.current_instruction.kk == 0x1E:
            """
            Fx1E - ADD I, Vx
            Set I = I + Vx.
            The values of I and Vx are added, and the results are stored in I.
            """
            logger.debug("ADD I, V{:01X}".format(self.current_instruction.x))
            self.registers.i += self.registers.v[self.current_instruction.x]
        elif self.current_instruction.kk == 0x29:
            """
            Fx29 - LD F, Vx
            Set I = location of sprite for digit Vx.
            The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
            See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
            """
            logger.debug("LD F, V{:01X}".format(self.current_instruction.x))
            number = self.registers.v[self.current_instruction.x]
            self.registers.i = number * 5
        elif self.current_instruction.kk == 0x33:
            """
            Fx33 - LD B, Vx
            Store BCD representation of Vx in memory locations I, I+1, and I+2.
            The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I,
            the tens digit at location I+1, and the ones digit at location I+2.
            """
            logger.debug("LD B, V{:01X}".format(self.current_instruction.x))
            decimal_value = self.registers.v[self.current_instruction.x]
            self.memory_buffer[self.registers.i] = decimal_value // 100
            self.memory_buffer[self.registers.i+1] = (decimal_value % 100) // 10
            self.memory_buffer[self.registers.i+2] = (decimal_value % 100) % 10

        elif self.current_instruction.kk == 0x55:
            """
            Fx55 - LD [I], Vx
            Store registers V0 through Vx in memory starting at location I.
            The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
            """
            logger.debug("LD [0x{:03X}], V{:01X}".format(self.registers.i, self.current_instruction.x))
            for index in range(0, self.current_instruction.x+1):
                self.memory_buffer[self.registers.i + index] = self.registers.v[index]
            # self.registers.i += (self.current_instruction.x + 1)
        elif self.current_instruction.kk == 0x65:
            """
            Fx65 - LD Vx, [I]
            Read registers V0 through Vx from memory starting at location I.
            The interpreter reads values from memory starting at location I into registers V0 through Vx.
            """
            logger.debug("LD V{:01X}, [0x{:03X}]".format(self.current_instruction.x, self.registers.i))
            for index in range(0, self.current_instruction.x + 1):
                self.registers.v[index] = self.memory_buffer[self.registers.i + index]
                self.registers.v[index] &= 0xFF
            # self.registers.i += (self.current_instruction.x + 1)

    class CurrentInstruction(object):
        def __init__(self, opcode=0):
            self.opcode = opcode
            self.x = (self.opcode & 0x0f00) >> 8
            self.y = (self.opcode & 0x00f0) >> 4
            self.kk = (self.opcode & 0x00ff)
            self.nnn = (self.opcode & 0x0fff)
            self.n = (self.opcode & 0x000f)

        def clear(self):
            self.opcode = 0
            self.x = 0
            self.y = 0
            self.kk = 0
            self.nnn = 0
            self.n = 0

    class Registers(object):
        def __init__(self):
            self.v = [0] * 16
            self.i = 0
            self.delay_timer = 0
            self.sound_timer = 0
