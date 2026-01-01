import sys
import os

class Assembler:
    def __init__(self):
        # 1. Predefined Symbols
        self.symbol_table = {
            "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
            "SCREEN": 16384, "KBD": 24576
        }
        for i in range(16):
            self.symbol_table[f"R{i}"] = i
        
        self.variable_address = 16

        # 2. Mnemonics Tables
        self.dest_table = {
            "null": "000", "M": "001", "D": "010", "MD": "011",
            "A": "100", "AM": "101", "AD": "110", "AMD": "111"
        }

        self.jump_table = {
            "null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
        }

        self.comp_table = {
            "0": "0101010", "1": "0111111", "-1": "0111010",
            "D": "0001100", "A": "0110000", "!D": "0001101",
            "!A": "0110001", "-D": "0001111", "-A": "0110011",
            "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
            "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
            "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
            "M": "1110000", "!M": "1110001", "-M": "1110011",
            "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
            "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
            "D|M": "1010101"
        }

    def clean_line(self, line):
        """Removes whitespace and comments."""
        line = line.split("//")[0]
        return line.strip()

    def first_pass(self, lines):
        """Builds the symbol table using Labels (LABEL)."""
        rom_address = 0
        cleaned_lines = []
        for line in lines:
            cleaned = self.clean_line(line)
            if not cleaned:
                continue
            if cleaned.startswith("(") and cleaned.endswith(")"):
                label = cleaned[1:-1]
                self.symbol_table[label] = rom_address
            else:
                cleaned_lines.append(cleaned)
                rom_address += 1
        return cleaned_lines

    def second_pass(self, lines):
        """Translates instructions to binary."""
        machine_code = []
        for line in lines:
            if line.startswith("@"):
                # A-Instruction
                val = line[1:]
                if val.isdigit():
                    address = int(val)
                else:
                    if val not in self.symbol_table:
                        self.symbol_table[val] = self.variable_address
                        self.variable_address += 1
                    address = self.symbol_table[val]
                machine_code.append(format(address, '016b'))
            else:
                # C-Instruction: dest=comp;jump
                dest, comp, jump = "null", "", "null"
                
                if "=" in line:
                    dest, line = line.split("=")
                if ";" in line:
                    comp, jump = line.split(";")
                else:
                    comp = line
                
                binary = "111" + self.comp_table[comp] + self.dest_table[dest] + self.jump_table[jump]
                machine_code.append(binary)
        return machine_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python Assembler.py file.asm")
        return

    input_file = sys.argv[1]
    output_file = input_file.replace(".asm", ".hack")

    with open(input_file, 'r') as f:
        lines = f.readlines()

    assembler = Assembler()
    # Step 1: Handle Labels
    intermediate_lines = assembler.first_pass(lines)
    # Step 2: Handle Variables and Mnemonics
    binary_output = assembler.second_pass(intermediate_lines)

    with open(output_file, 'w') as f:
        f.write("\n".join(binary_output) + "\n")

    print(f"Assembly successful. Generated {output_file}")

if __name__ == "__main__":
    main()