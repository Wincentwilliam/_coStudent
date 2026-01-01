import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional

# -------------------------
# Tokenizer
# -------------------------
TOKEN_SPEC = [
    ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),
    ('STRING',  r'"[^"\n]*"'),
    ('INT',     r'\d+'),
    ('ID',      r'[A-Za-z_][A-Za-z0-9_]*'),
    ('SYMBOL',  r'[{}()\[\].,;+\-*/&|<>=~]'),
    ('WS',      r'[ \t\r\n]+'),
]
TOK_REGEX = '|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC)
KEYWORDS = {
    'class','constructor','function','method','field','static','var',
    'int','char','boolean','void','true','false','null','this',
    'let','do','if','else','while','return'
}

class Token:
    def __init__(self, kind: str, value: str, line: int):
        self.kind = kind
        self.value = value
        self.line = line
    def __repr__(self):
        return f"Token({self.kind!r}, {self.value!r}, line={self.line})"

class Tokenizer:
    def __init__(self, text: str):
        self.tokens: List[Token] = []
        self.pos = 0
        self._tokenize(text)

    def _tokenize(self, text: str):
        line_num = 1
        for m in re.finditer(TOK_REGEX, text):
            kind = m.lastgroup
            val = m.group(0)
            if kind == 'WS':
                line_num += val.count('\n')
                continue
            if kind == 'COMMENT':
                line_num += val.count('\n')
                continue
            if kind == 'ID' and val in KEYWORDS:
                kind = 'KEYWORD'
            self.tokens.append(Token(kind, val, line_num))

    def has_more(self) -> bool:
        return self.pos < len(self.tokens)
    
    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.has_more() else None
    
    def advance(self) -> Optional[Token]:
        t = self.peek()
        if t: self.pos += 1
        return t

    def expect(self, value: Optional[str] = None, kind: Optional[str] = None) -> Token:
        t = self.advance()
        if not t:
            raise SyntaxError(f"Unexpected EOF, expected {value or kind}")
        if kind and t.kind != kind:
            raise SyntaxError(f"Line {t.line}: Expected {kind}, got {t.kind} ('{t.value}')")
        if value and t.value != value:
            raise SyntaxError(f"Line {t.line}: Expected '{value}', got '{t.value}'")
        return t

# -------------------------
# Symbol Table
# -------------------------
class SymbolTable:
    def __init__(self):
        self.class_scope = {}  # name -> (type, kind, index)
        self.sub_scope = {}
        self.counts = {'static': 0, 'field': 0, 'arg': 0, 'var': 0}

    def start_subroutine(self):
        self.sub_scope.clear()
        self.counts['arg'] = 0
        self.counts['var'] = 0

    def define(self, name: str, typ: str, kind: str):
        idx = self.counts[kind]
        self.counts[kind] += 1
        table = self.class_scope if kind in ('static', 'field') else self.sub_scope
        table[name] = (typ, kind, idx)

    def _lookup(self, name: str):
        return self.sub_scope.get(name) or self.class_scope.get(name)

    def kind_of(self, name: str) -> Optional[str]:
        res = self._lookup(name)
        return res[1] if res else None

    def type_of(self, name: str) -> Optional[str]:
        res = self._lookup(name)
        return res[0] if res else None

    def index_of(self, name: str) -> Optional[int]:
        res = self._lookup(name)
        return res[2] if res else None

# -------------------------
# VM Writer
# -------------------------
class VMWriter:
    def __init__(self, path: Path):
        self.f = open(path, 'w')

    def write(self, line: str): self.f.write(line + '\n')
    def write_push(self, seg: str, idx: int): self.write(f'push {seg} {idx}')
    def write_pop(self, seg: str, idx: int):  self.write(f'pop {seg} {idx}')
    def write_arithmetic(self, cmd: str):     self.write(cmd)
    def write_label(self, label: str):        self.write(f'label {label}')
    def write_goto(self, label: str):         self.write(f'goto {label}')
    def write_if(self, label: str):           self.write(f'if-goto {label}')
    def write_call(self, name: str, n: int):  self.write(f'call {name} {n}')
    def write_function(self, name: str, n: int): self.write(f'function {name} {n}')
    def write_return(self):                   self.write('return')
    def close(self):                          self.f.close()

# -------------------------
# Compilation Engine (Project 11 Logic)
# -------------------------
class CompilationEngine:
    OP_MAP = {'+':'add','-':'sub','*':'call Math.multiply 2','/':'call Math.divide 2',
              '&':'and','|':'or','<':'lt','>':'gt','=':'eq'}
    UNARY_MAP = {'-':'neg','~':'not'}

    def __init__(self, tokenizer: Tokenizer, writer: VMWriter, sym: SymbolTable):
        self.t = tokenizer
        self.w = writer
        self.sym = sym
        self.class_name = ""
        self.label_count = 0

    def get_label(self, prefix: str) -> str:
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def kind_to_seg(self, kind: str) -> str:
        return {'static':'static', 'field':'this', 'arg':'argument', 'var':'local'}.get(kind, '')

    def compile_class(self):
        self.t.expect('class', 'KEYWORD')
        self.class_name = self.t.expect(kind='ID').value
        self.t.expect('{', 'SYMBOL')
        
        while self.t.peek() and self.t.peek().value in ('static', 'field'):
            self.compile_class_var_dec()
        while self.t.peek() and self.t.peek().value in ('constructor', 'function', 'method'):
            self.compile_subroutine()
            
        self.t.expect('}', 'SYMBOL')

    def compile_class_var_dec(self):
        kind = self.t.advance().value # static | field
        typ = self.t.advance().value  # type
        names = [self.t.expect(kind='ID').value]
        while self.t.peek().value == ',':
            self.t.advance()
            names.append(self.t.expect(kind='ID').value)
        for name in names:
            self.sym.define(name, typ, kind)
        self.t.expect(';', 'SYMBOL')

    def compile_subroutine(self):
        sub_type = self.t.advance().value # constructor | function | method
        self.t.advance() # return type
        name = self.t.expect(kind='ID').value
        
        self.sym.start_subroutine()
        if sub_type == 'method':
            self.sym.define('this', self.class_name, 'arg')
            
        self.t.expect('(', 'SYMBOL')
        self.compile_parameter_list()
        self.t.expect(')', 'SYMBOL')
        
        # Subroutine Body
        self.t.expect('{', 'SYMBOL')
        n_locals = 0
        while self.t.peek().value == 'var':
            n_locals += self.compile_var_dec()
            
        self.w.write_function(f"{self.class_name}.{name}", n_locals)
        
        if sub_type == 'constructor':
            self.w.write_push('constant', self.sym.counts['field'])
            self.w.write_call('Memory.alloc', 1)
            self.w.write_pop('pointer', 0)
        elif sub_type == 'method':
            self.w.write_push('argument', 0)
            self.w.write_pop('pointer', 0)

        self.compile_statements()
        self.t.expect('}', 'SYMBOL')

    def compile_parameter_list(self):
        if self.t.peek().value == ')': return
        typ = self.t.advance().value
        name = self.t.expect(kind='ID').value
        self.sym.define(name, typ, 'arg')
        while self.t.peek().value == ',':
            self.t.advance()
            typ = self.t.advance().value
            name = self.t.expect(kind='ID').value
            self.sym.define(name, typ, 'arg')

    def compile_var_dec(self) -> int:
        self.t.expect('var', 'KEYWORD')
        typ = self.t.advance().value
        count = 1
        self.sym.define(self.t.expect(kind='ID').value, typ, 'var')
        while self.t.peek().value == ',':
            self.t.advance()
            self.sym.define(self.t.expect(kind='ID').value, typ, 'var')
            count += 1
        self.t.expect(';', 'SYMBOL')
        return count

    def compile_statements(self):
        while self.t.peek() and self.t.peek().value != '}':
            val = self.t.peek().value
            if val == 'let': self.compile_let()
            elif val == 'if': self.compile_if()
            elif val == 'while': self.compile_while()
            elif val == 'do': self.compile_do()
            elif val == 'return': self.compile_return()

    def compile_let(self):
        self.t.expect('let')
        var_name = self.t.expect(kind='ID').value
        is_array = False
        if self.t.peek().value == '[':
            is_array = True
            self.t.advance()
            self.compile_expression()
            self.t.expect(']')
            self.w.write_push(self.kind_to_seg(self.sym.kind_of(var_name)), self.sym.index_of(var_name))
            self.w.write_arithmetic('add')

        self.t.expect('=')
        self.compile_expression()
        self.t.expect(';')

        if is_array:
            self.w.write_pop('temp', 0)
            self.w.write_pop('pointer', 1)
            self.w.write_push('temp', 0)
            self.w.write_pop('that', 0)
        else:
            self.w.write_pop(self.kind_to_seg(self.sym.kind_of(var_name)), self.sym.index_of(var_name))

    def compile_do(self):
        self.t.expect('do')
        self.compile_term() # Handles subroutine calls
        self.w.write_pop('temp', 0)
        self.t.expect(';')

    def compile_return(self):
        self.t.expect('return')
        if self.t.peek().value != ';':
            self.compile_expression()
        else:
            self.w.write_push('constant', 0)
        self.w.write_return()
        self.t.expect(';')

    def compile_if(self):
        l1, l2 = self.get_label("IF_FALSE"), self.get_label("IF_END")
        self.t.expect('if'); self.t.expect('(')
        self.compile_expression()
        self.t.expect(')')
        self.w.write_arithmetic('not')
        self.w.write_if(l1)
        self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_goto(l2)
        self.w.write_label(l1)
        if self.t.peek().value == 'else':
            self.t.advance()
            self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_label(l2)

    def compile_while(self):
        l1, l2 = self.get_label("WHILE_EXP"), self.get_label("WHILE_END")
        self.w.write_label(l1)
        self.t.expect('while'); self.t.expect('(')
        self.compile_expression()
        self.t.expect(')')
        self.w.write_arithmetic('not')
        self.w.write_if(l2)
        self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_goto(l1)
        self.w.write_label(l2)

    def compile_expression(self):
        self.compile_term()
        while self.t.peek().value in self.OP_MAP:
            op = self.t.advance().value
            self.compile_term()
            self.w.write_arithmetic(self.OP_MAP[op])

    def compile_term(self):
        tok = self.t.advance()
        if tok.kind == 'INT':
            self.w.write_push('constant', int(tok.value))
        elif tok.kind == 'STRING':
            s = tok.value[1:-1]
            self.w.write_push('constant', len(s))
            self.w.write_call('String.new', 1)
            for char in s:
                self.w.write_push('constant', ord(char))
                self.w.write_call('String.appendChar', 2)
        elif tok.kind == 'KEYWORD':
            if tok.value == 'this': self.w.write_push('pointer', 0)
            elif tok.value in ('false', 'null'): self.w.write_push('constant', 0)
            elif tok.value == 'true': 
                self.w.write_push('constant', 0)
                self.w.write_arithmetic('not')
        elif tok.value == '(':
            self.compile_expression()
            self.t.expect(')')
        elif tok.value in self.UNARY_MAP:
            op = tok.value
            self.compile_term()
            self.w.write_arithmetic(self.UNARY_MAP[op])
        elif tok.kind == 'ID':
            name = tok.value
            if self.t.peek().value == '[': # Array
                self.t.advance()
                self.compile_expression()
                self.t.expect(']')
                self.w.write_push(self.kind_to_seg(self.sym.kind_of(name)), self.sym.index_of(name))
                self.w.write_arithmetic('add')
                self.w.write_pop('pointer', 1)
                self.w.write_push('that', 0)
            elif self.t.peek().value in ('(', '.'): # Subroutine Call
                self.compile_call(name)
            else: # Var
                self.w.write_push(self.kind_to_seg(self.sym.kind_of(name)), self.sym.index_of(name))

    def compile_call(self, first_id: str):
        n_args = 0
        obj_name = first_id
        if self.t.peek().value == '.':
            self.t.advance()
            sub_name = self.t.expect(kind='ID').value
            typ = self.sym.type_of(obj_name)
            if typ: # Method call on object
                self.w.write_push(self.kind_to_seg(self.sym.kind_of(obj_name)), self.sym.index_of(obj_name))
                full_name = f"{typ}.{sub_name}"
                n_args = 1
            else: # Static call
                full_name = f"{obj_name}.{sub_name}"
        else: # Implicit method call on this
            self.w.write_push('pointer', 0)
            full_name = f"{self.class_name}.{obj_name}"
            n_args = 1
        
        self.t.expect('(')
        n_args += self.compile_expression_list()
        self.t.expect(')')
        self.w.write_call(full_name, n_args)

    def compile_expression_list(self) -> int:
        count = 0
        if self.t.peek().value != ')':
            self.compile_expression()
            count = 1
            while self.t.peek().value == ',':
                self.t.advance()
                self.compile_expression()
                count += 1
        return count

# -------------------------
# Driver
# -------------------------
def main():
    if len(sys.argv) < 2: return
    path = Path(sys.argv[1])
    files = list(path.glob('*.jack')) if path.is_dir() else [path]
    
    for f in files:
        tokenizer = Tokenizer(f.read_text())
        writer = VMWriter(f.with_suffix('.vm'))
        engine = CompilationEngine(tokenizer, writer, SymbolTable())
        try:
            engine.compile_class()
            print(f"Compiled: {f.name}")
        except SyntaxError as e:
            print(f"Error in {f.name}: {e}")
        finally:
            writer.close()

if __name__ == '__main__':
    main()