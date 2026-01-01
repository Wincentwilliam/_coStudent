import os
import sys

class Parser:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.lines = [line.split('//')[0].strip() for line in f if line.split('//')[0].strip()]
        self.current_command = None
        self.line_ptr = -1

    def has_more_commands(self):
        return self.line_ptr < len(self.lines) - 1

    def advance(self):
        self.line_ptr += 1
        self.current_command = self.lines[self.line_ptr].split()

    def command_type(self):
        cmd = self.current_command[0]
        arithmetic = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        if cmd in arithmetic: return "C_ARITHMETIC"
        if cmd == 'push': return "C_PUSH"
        if cmd == 'pop': return "C_POP"
        if cmd == 'label': return "C_LABEL"
        if cmd == 'goto': return "C_GOTO"
        if cmd == 'if-goto': return "C_IF"
        if cmd == 'function': return "C_FUNCTION"
        if cmd == 'call': return "C_CALL"
        if cmd == 'return': return "C_RETURN"

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC": return self.current_command[0]
        return self.current_command[1]

    def arg2(self):
        return int(self.current_command[2])

class CodeWriter:
    def __init__(self, output_filename):
        self.file = open(output_filename, 'w')
        self.filename = ""
        self.label_count = 0
        self.current_function = "GLOBAL"

    def set_filename(self, filename):
        self.filename = os.path.basename(filename).replace(".vm", "")

    def write_init(self):
        """Bootstrap: Set SP=256, set LCL/ARG/THIS/THAT to 0, call Sys.init."""
        self._write_asm(["// Bootstrap code", "@256", "D=A", "@SP", "M=D"])
        # Initialize LCL, ARG, THIS, THAT to 0 to prevent garbage memory errors
        for ptr in ["LCL", "ARG", "THIS", "THAT"]:
            self._write_asm([f"@{ptr}", "M=0"])
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        self._write_asm([f"// {command}"])
        if command in ['add', 'sub', 'and', 'or', 'eq', 'gt', 'lt']:
            self._pop_stack_to_d() # y
            self._write_asm(["@SP", "AM=M-1"]) # Point to x and decrement SP
            if command == 'add': self._write_asm(["M=D+M"])
            elif command == 'sub': self._write_asm(["M=M-D"])
            elif command == 'and': self._write_asm(["M=D&M"])
            elif command == 'or': self._write_asm(["M=D|M"])
            elif command in ['eq', 'gt', 'lt']:
                label_true = f"TRUE_{self.label_count}"
                label_end = f"END_ARITH_{self.label_count}"
                self.label_count += 1
                self._write_asm(["D=M-D", f"@{label_true}"])
                if command == 'eq': self._write_asm(["D;JEQ"])
                elif command == 'gt': self._write_asm(["D;JGT"])
                elif command == 'lt': self._write_asm(["D;JLT"])
                self._write_asm(["@SP", "A=M", "M=0", f"@{label_end}", "0;JMP", f"({label_true})", "@SP", "A=M", "M=-1", f"({label_end})"])
            self._write_asm(["@SP", "M=M+1"])
        elif command in ['neg', 'not']:
            self._write_asm(["@SP", "A=M-1"])
            if command == 'neg': self._write_asm(["M=-M"])
            elif command == 'not': self._write_asm(["M=!M"])

    def write_push_pop(self, command_type, segment, index):
        self._write_asm([f"// {command_type} {segment} {index}"])
        if command_type == "C_PUSH":
            if segment == "constant":
                self._write_asm([f"@{index}", "D=A"])
            elif segment in ["local", "argument", "this", "that"]:
                seg_map = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
                self._write_asm([f"@{seg_map[segment]}", "D=M", f"@{index}", "A=D+A", "D=M"])
            elif segment == "temp":
                self._write_asm([f"@{5+index}", "D=M"])
            elif segment == "pointer":
                self._write_asm([f"@{'THIS' if index == 0 else 'THAT'}", "D=M"])
            elif segment == "static":
                self._write_asm([f"@{self.filename}.{index}", "D=M"])
            self._push_d_to_stack()
        else: # C_POP
            if segment in ["local", "argument", "this", "that"]:
                seg_map = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
                self._write_asm([f"@{seg_map[segment]}", "D=M", f"@{index}", "D=D+A", "@R13", "M=D"])
                self._pop_stack_to_d()
                self._write_asm(["@R13", "A=M", "M=D"])
            elif segment == "temp":
                self._pop_stack_to_d()
                self._write_asm([f"@{5+index}", "M=D"])
            elif segment == "pointer":
                self._pop_stack_to_d()
                self._write_asm([f"@{'THIS' if index == 0 else 'THAT'}", "M=D"])
            elif segment == "static":
                self._pop_stack_to_d()
                self._write_asm([f"@{self.filename}.{index}", "M=D"])

    def write_label(self, label):
        self._write_asm([f"({self.current_function}${label})"])

    def write_goto(self, label):
        self._write_asm([f"@{self.current_function}${label}", "0;JMP"])

    def write_if(self, label):
        self._pop_stack_to_d()
        self._write_asm([f"@{self.current_function}${label}", "D;JNE"])

    def write_function(self, function_name, num_locals):
        self.current_function = function_name
        self._write_asm([f"({function_name})"])
        for _ in range(num_locals):
            self._write_asm(["@0", "D=A"])
            self._push_d_to_stack()

    def write_call(self, function_name, num_args):
        ret_label = f"RET_ADDR_{self.label_count}"
        self.label_count += 1
        self._write_asm([f"@{ret_label}", "D=A"])
        self._push_d_to_stack()
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self._write_asm([f"@{seg}", "D=M"])
            self._push_d_to_stack()
        self._write_asm(["@SP", "D=M", "@5", "D=D-A", f"@{num_args}", "D=D-A", "@ARG", "M=D", "@SP", "D=M", "@LCL", "M=D", f"@{function_name}", "0;JMP", f"({ret_label})"])

    def write_return(self):
        self._write_asm(["@LCL", "D=M", "@R13", "M=D", "@5", "A=D-A", "D=M", "@R14", "M=D"])
        self._pop_stack_to_d()
        self._write_asm(["@ARG", "A=M", "M=D", "@ARG", "D=M+1", "@SP", "M=D"])
        for i, seg in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            self._write_asm(["@R13", "AM=M-1", "D=M", f"@{seg}", "M=D"])
        self._write_asm(["@R14", "A=M", "0;JMP"])

    def _push_d_to_stack(self):
        self._write_asm(["@SP", "A=M", "M=D", "@SP", "M=M+1"])

    def _pop_stack_to_d(self):
        self._write_asm(["@SP", "AM=M-1", "D=M"])

    def _write_asm(self, insts):
        for i in insts: self.file.write(i + "\n")

    def close(self):
        self.file.close()

def main():
    if len(sys.argv) != 2: return
    path = sys.argv[1].rstrip('/')
    is_dir = os.path.isdir(path)
    output_path = f"{path}/{os.path.basename(path)}.asm" if is_dir else path.replace(".vm", ".asm")
    vm_files = [f"{path}/{f}" for f in os.listdir(path) if f.endswith('.vm')] if is_dir else [path]

    cw = CodeWriter(output_path)
    if is_dir: cw.write_init()

    for vf in vm_files:
        p = Parser(vf)
        cw.set_filename(vf)
        while p.has_more_commands():
            p.advance()
            t = p.command_type()
            if t == "C_ARITHMETIC": cw.write_arithmetic(p.arg1())
            elif t in ["C_PUSH", "C_POP"]: cw.write_push_pop(t, p.arg1(), p.arg2())
            elif t == "C_LABEL": cw.write_label(p.arg1())
            elif t == "C_GOTO": cw.write_goto(p.arg1())
            elif t == "C_IF": cw.write_if(p.arg1())
            elif t == "C_FUNCTION": cw.write_function(p.arg1(), p.arg2())
            elif t == "C_CALL": cw.write_call(p.arg1(), p.arg2())
            elif t == "C_RETURN": cw.write_return()
    cw.close()

if __name__ == "__main__":
    main()