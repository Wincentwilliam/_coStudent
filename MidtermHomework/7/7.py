import sys
import os

class Parser:
    """Handles the parsing of a single .vm file."""
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.lines = [line.split('//')[0].strip() for line in f.readlines() if line.split('//')[0].strip()]
        self.current_line = -1

    def has_more_commands(self):
        return self.current_line + 1 < len(self.lines)

    def advance(self):
        self.current_line += 1
        self.command = self.lines[self.current_line].split()

    def command_type(self):
        arithmetic = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        if self.command[0] in arithmetic: return "C_ARITHMETIC"
        if self.command[0] == 'push': return "C_PUSH"
        if self.command[0] == 'pop': return "C_POP"
        return None

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC": return self.command[0]
        return self.command[1]

    def arg2(self):
        return int(self.command[2])


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    def __init__(self, output_filename):
        self.file = open(output_filename, 'w')
        self.filename = os.path.basename(output_filename).replace('.asm', '')
        self.label_count = 0
        self.segments = {
            'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'
        }

    def write_arithmetic(self, command):
        asm = []
        if command in ['add', 'sub', 'and', 'or']:
            asm += ["@SP", "AM=M-1", "D=M", "A=A-1"]
            if command == 'add': asm.append("M=D+M")
            elif command == 'sub': asm.append("M=M-D")
            elif command == 'and': asm.append("M=D&M")
            elif command == 'or': asm.append("M=D|M")
        elif command in ['neg', 'not']:
            asm += ["@SP", "A=M-1"]
            asm.append("M=-M" if command == 'neg' else "M=!M")
        elif command in ['eq', 'gt', 'lt']:
            label = f"LABEL_{self.label_count}"
            self.label_count += 1
            asm += ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", f"@{label}_TRUE"]
            if command == 'eq': asm.append("D;JEQ")
            elif command == 'gt': asm.append("D;JGT")
            elif command == 'lt': asm.append("D;JLT")
            asm += ["@SP", "A=M-1", "M=0", f"@{label}_END", "0;JMP", f"({label}_TRUE)", "@SP", "A=M-1", "M=-1", f"({label}_END)"]
        
        self.file.write(f"// {command}\n" + "\n".join(asm) + "\n")

    def write_push_pop(self, command_type, segment, index):
        asm = []
        if command_type == "C_PUSH":
            if segment == 'constant':
                asm += [f"@{index}", "D=A"]
            elif segment in self.segments:
                asm += [f"@{self.segments[segment]}", "D=M", f"@{index}", "A=D+A", "D=M"]
            elif segment == 'temp':
                asm += [f"@{5 + index}", "D=M"]
            elif segment == 'pointer':
                asm += [f"@{'THIS' if index == 0 else 'THAT'}", "D=M"]
            elif segment == 'static':
                asm += [f"@{self.filename}.{index}", "D=M"]
            
            asm += ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

        elif command_type == "C_POP":
            if segment in self.segments:
                asm += [f"@{self.segments[segment]}", "D=M", f"@{index}", "D=D+A", "@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]
            elif segment == 'temp':
                asm += ["@SP", "AM=M-1", "D=M", f"@{5 + index}", "M=D"]
            elif segment == 'pointer':
                asm += ["@SP", "AM=M-1", "D=M", f"@{'THIS' if index == 0 else 'THAT'}", "M=D"]
            elif segment == 'static':
                asm += ["@SP", "AM=M-1", "D=M", f"@{self.filename}.{index}", "M=D"]

        self.file.write(f"// {command_type} {segment} {index}\n" + "\n".join(asm) + "\n")

    def close(self):
        self.file.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <file.vm>")
        return

    path = sys.argv[1]
    output_path = path.replace('.vm', '.asm')
    
    parser = Parser(path)
    writer = CodeWriter(output_path)

    while parser.has_more_commands():
        parser.advance()
        c_type = parser.command_type()
        if c_type == "C_ARITHMETIC":
            writer.write_arithmetic(parser.arg1())
        elif c_type in ["C_PUSH", "C_POP"]:
            writer.write_push_pop(c_type, parser.arg1(), parser.arg2())

    writer.close()
    print(f"Translation finished. Created {output_path}")

if __name__ == "__main__":
    main()