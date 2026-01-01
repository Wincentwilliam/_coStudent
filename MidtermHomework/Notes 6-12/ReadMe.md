# Homework 6: Hack Assembler

## AI Acknowledgment
This chapter was completed with the support of Artificial Intelligence.
AI Tool: GOOGLE AI STUDIO (GEMINI)
Link: https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221pMTc2KxxQIAS5gHTmbTpkU24ceU4vMfR%22%5D,%22action%22:%22open%22,%22userId%22:%22113497521968724205844%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing

## Homework Description
In this Project is part of the **Nand2Tetris** curriculum. The goal is to develop a software assembler that translates programs written in the symbolic **Hack Assembly Language** into the binary machine code used by the Hack hardware platform.

The assembler handles:
- **A-Instructions**: Addressing constants and memory locations (e.g., `@100`).
- **C-Instructions**: Computational operations, destination routing, and jump logic (e.g., `D=D+M;JMP`).
- **Symbols**: Automatic management of predefined symbols (R0-R15, SCREEN, etc.), labels for branching, and variables.

---

## Technical Implementation
The assembler is written in **Python** and utilizes a **two-pass logic**:

1.  **First Pass**: Scans the source code for label definitions (e.g., `(LOOP)`) and adds them to the Symbol Table with their corresponding ROM addresses.
2.  **Second Pass**: Translates instructions into 16-bit binary strings. It identifies symbols/variables and assigns them unique RAM addresses starting from `16`.

### Source Code (`6.py`)
```python
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
```
---
# Homework 7: VM Translator 

## AI Acknowledgment
This chapter was completed with the support of Artificial Intelligence.
AI Tool: GOOGLE AI STUDIO (GEMINI)
Link: https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2218sv2i6zKX9fsjuVNrPkK5QjiDqt_QPG7%22%5D,%22action%22:%22open%22,%22userId%22:%22113497521968724205844%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing

## Description
This project is a **Virtual Machine (VM) Translator** built for the Nand2Tetris Computer Architecture course (Homework 7). It translates VM code into Hack Assembly language (.asm). This is the first part of the translator, focusing on stack arithmetic and memory access commands.

## Features Implemented
- **Stack Arithmetic**: Implementation of `add`, `sub`, `neg`, `eq`, `gt`, `lt`, `and`, `or`, and `not`.
- **Memory Access**: Full support for `push` and `pop` commands across all standard segments:
  - `constant`
  - `local`, `argument`, `this`, `that`
  - `temp`
  - `pointer`
  - `static`

## Project Structure
- **7.py**: The main Python translator script.
- **StackArithmetic/**: Test folders for arithmetic operations (`SimpleAdd`, `StackTest`).
- **MemoryAccess/**: Test folders for memory segments (`BasicTest`, `PointerTest`, `StaticTest`).
- **README.md**: Project documentation.

## How to Run the Translator

To translate a `.vm` file into a `.asm` file, use the following command in your terminal:

```powershell
python 7.py <Path_to_VM_File>
```

---
