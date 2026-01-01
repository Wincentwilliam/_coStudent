import sys
import re
from pathlib import Path
from typing import List, Optional

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
    'class','constructor', 'function', 'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
    'let', 'do', 'if', 'else', 'while', 'return'
}

class Token:
    def __init__(self, kind: str, value: str, line: int):
        self.kind = kind
        self.value = value
        self.line = line

class Tokenizer:
    def __init__(self, text: str):
        self.tokens: List[Token] = []
        self.pos = 0
        line_num = 1
        for m in re.finditer(TOK_REGEX, text):
            kind = m.lastgroup
            val = m.group(0)
            if kind == 'WS' or kind == 'COMMENT':
                line_num += val.count('\n')
                continue
            if kind == 'ID' and val in KEYWORDS:
                kind = 'KEYWORD'
            self.tokens.append(Token(kind, val, line_num))

    def has_more(self) -> bool: return self.pos < len(self.tokens)
    def peek(self) -> Optional[Token]: return self.tokens[self.pos] if self.has_more() else None
    def advance(self) -> Optional[Token]:
        t = self.peek()
        if t: self.pos += 1
        return t
    def expect(self, value: str = None, kind: str = None) -> Token:
        t = self.advance()
        if not t: raise SyntaxError(f"Unexpected EOF, expected {value or kind}")
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
        self.class_scope = {}
        self.sub_scope = {}
        self.counts = {'static': 0, 'field': 0, 'arg': 0, 'var': 0}

    def start_subroutine(self):
        self.sub_scope.clear()
        self.counts['arg'] = 0
        self.counts['var'] = 0

    def define(self, name: str, typ: str, kind: str):
        idx = self.counts[kind]
        self.counts[kind] += 1
        target = self.class_scope if kind in ('static', 'field') else self.sub_scope
        target[name] = (typ, kind, idx)

    def _get(self, name: str):
        return self.sub_scope.get(name) or self.class_scope.get(name)

    def kind_of(self, name: str): return self._get(name)[1] if self._get(name) else None
    def type_of(self, name: str): return self._get(name)[0] if self._get(name) else None
    def index_of(self, name: str): return self._get(name)[2] if self._get(name) else None

# -------------------------
# VM Writer
# -------------------------
class VMWriter:
    def __init__(self, path: Path):
        self.f = open(path, 'w')
    def write_push(self, seg: str, idx: int): self.f.write(f"push {seg} {idx}\n")
    def write_pop(self, seg: str, idx: int):  self.f.write(f"pop {seg} {idx}\n")
    def write_arithmetic(self, cmd: str):     self.f.write(f"{cmd}\n")
    def write_label(self, label: str):        self.f.write(f"label {label}\n")
    def write_goto(self, label: str):         self.f.write(f"goto {label}\n")
    def write_if(self, label: str):           self.f.write(f"if-goto {label}\n")
    def write_call(self, name: str, n: int):  self.f.write(f"call {name} {n}\n")
    def write_function(self, name: str, n: int): self.f.write(f"function {name} {n}\n")
    def write_return(self):                   self.f.write("return\n")
    def close(self):                          self.f.close()

# -------------------------
# Compilation Engine
# -------------------------
class CompilationEngine:
    OP_MAP = {'+':'add', '-':'sub', '&':'and', '|':'or', '<':'lt', '>':'gt', '=':'eq',
              '*':'call Math.multiply 2', '/':'call Math.divide 2'}
    UNARY_MAP = {'-':'neg', '~':'not'}
    SEG_MAP = {'static':'static', 'field':'this', 'arg':'argument', 'var':'local'}

    def __init__(self, tokenizer: Tokenizer, writer: VMWriter):
        self.t = tokenizer
        self.w = writer
        self.sym = SymbolTable()
        self.class_name = ""
        self.label_id = 0

    def new_label(self, prefix: str) -> str:
        self.label_id += 1
        return f"{prefix}_{self.label_id}"

    def compile_class(self):
        self.t.expect('class')
        self.class_name = self.t.expect(kind='ID').value
        self.t.expect('{')
        while self.t.peek() and self.t.peek().value in ('static', 'field'):
            self.compile_var_dec(is_class=True)
        while self.t.peek() and self.t.peek().value in ('constructor', 'function', 'method'):
            self.compile_subroutine()
        self.t.expect('}')

    def compile_var_dec(self, is_class=False):
        kind = self.t.advance().value
        typ = self.t.advance().value
        while True:
            name = self.t.expect(kind='ID').value
            self.sym.define(name, typ, kind)
            if self.t.peek().value != ',': break
            self.t.advance()
        self.t.expect(';')

    def compile_subroutine(self):
        sub_kind = self.t.advance().value
        self.t.advance() # ret type
        sub_name = self.t.expect(kind='ID').value
        self.sym.start_subroutine()
        
        if sub_kind == 'method':
            self.sym.define('this', self.class_name, 'arg')
        
        self.t.expect('(')
        self.compile_parameter_list()
        self.t.expect(')')
        
        # Subroutine Body
        self.t.expect('{')
        n_locals = 0
        while self.t.peek().value == 'var':
            self.t.advance()
            typ = self.t.advance().value
            while True:
                self.sym.define(self.t.expect(kind='ID').value, typ, 'var')
                n_locals += 1
                if self.t.peek().value != ',': break
                self.t.advance()
            self.t.expect(';')
            
        self.w.write_function(f"{self.class_name}.{sub_name}", n_locals)
        if sub_kind == 'constructor':
            self.w.write_push('constant', self.sym.counts['field'])
            self.w.write_call('Memory.alloc', 1)
            self.w.write_pop('pointer', 0)
        elif sub_kind == 'method':
            self.w.write_push('argument', 0)
            self.w.write_pop('pointer', 0)

        self.compile_statements()
        self.t.expect('}')

    def compile_parameter_list(self):
        if self.t.peek().value == ')': return
        while True:
            typ = self.t.advance().value
            name = self.t.expect(kind='ID').value
            self.sym.define(name, typ, 'arg')
            if self.t.peek().value != ',': break
            self.t.advance()

    def compile_statements(self):
        while self.t.peek() and self.t.peek().value != '}':
            stmt = self.t.peek().value
            if stmt == 'let': self.compile_let()
            elif stmt == 'if': self.compile_if()
            elif stmt == 'while': self.compile_while()
            elif stmt == 'do': self.compile_do()
            elif stmt == 'return': self.compile_return()
            else: break

    def compile_let(self):
        self.t.expect('let')
        name = self.t.expect(kind='ID').value
        is_array = False
        if self.t.peek().value == '[':
            is_array = True
            self.t.advance()
            self.compile_expression()
            self.t.expect(']')
            self.w.write_push(self.SEG_MAP[self.sym.kind_of(name)], self.sym.index_of(name))
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
            self.w.write_pop(self.SEG_MAP[self.sym.kind_of(name)], self.sym.index_of(name))

    def compile_do(self):
        self.t.expect('do')
        self.compile_term() # Term handles calls
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
        l_false = self.new_label("IF_FALSE")
        l_end = self.new_label("IF_END")
        self.t.expect('if'); self.t.expect('(')
        self.compile_expression()
        self.t.expect(')')
        self.w.write_arithmetic('not')
        self.w.write_if(l_false)
        self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_goto(l_end)
        self.w.write_label(l_false)
        if self.t.peek().value == 'else':
            self.t.advance(); self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_label(l_end)

    def compile_while(self):
        l_start = self.new_label("WHILE_START")
        l_end = self.new_label("WHILE_END")
        self.w.write_label(l_start)
        self.t.expect('while'); self.t.expect('(')
        self.compile_expression()
        self.t.expect(')')
        self.w.write_arithmetic('not')
        self.w.write_if(l_end)
        self.t.expect('{'); self.compile_statements(); self.t.expect('}')
        self.w.write_goto(l_start)
        self.w.write_label(l_end)

    def compile_expression(self):
        self.compile_term()
        while self.t.peek() and self.t.peek().value in self.OP_MAP:
            op = self.t.advance().value
            self.compile_term()
            self.w.write_arithmetic(self.OP_MAP[op])

    def compile_term(self):
        t = self.t.advance()
        if t.kind == 'INT':
            self.w.write_push('constant', int(t.value))
        elif t.kind == 'STRING':
            s = t.value[1:-1]
            self.w.write_push('constant', len(s))
            self.w.write_call('String.new', 1)
            for char in s:
                self.w.write_push('constant', ord(char))
                self.w.write_call('String.appendChar', 2)
        elif t.kind == 'KEYWORD':
            if t.value == 'this': self.w.write_push('pointer', 0)
            elif t.value in ('null', 'false'): self.w.write_push('constant', 0)
            elif t.value == 'true': 
                self.w.write_push('constant', 0)
                self.w.write_arithmetic('not')
        elif t.value == '(':
            self.compile_expression()
            self.t.expect(')')
        elif t.value in self.UNARY_MAP:
            op = t.value
            self.compile_term()
            self.w.write_arithmetic(self.UNARY_MAP[op])
        elif t.kind == 'ID':
            name = t.value
            nxt = self.t.peek().value
            if nxt == '[':
                self.t.advance()
                self.compile_expression()
                self.t.expect(']')
                self.w.write_push(self.SEG_MAP[self.sym.kind_of(name)], self.sym.index_of(name))
                self.w.write_arithmetic('add')
                self.w.write_pop('pointer', 1)
                self.w.write_push('that', 0)
            elif nxt in ('(', '.'):
                self.compile_call(name)
            else:
                self.w.write_push(self.SEG_MAP[self.sym.kind_of(name)], self.sym.index_of(name))

    def compile_call(self, name: str):
        n_args = 0
        if self.t.peek().value == '.':
            self.t.advance()
            sub_name = self.t.expect(kind='ID').value
            typ = self.sym.type_of(name)
            if typ: # Method call on instance
                self.w.write_push(self.SEG_MAP[self.sym.kind_of(name)], self.sym.index_of(name))
                full_name, n_args = f"{typ}.{sub_name}", 1
            else: # Static call
                full_name, n_args = f"{name}.{sub_name}", 0
        else: # Internal method call
            self.w.write_push('pointer', 0)
            full_name, n_args = f"{self.class_name}.{name}", 1
        
        self.t.expect('(')
        n_args += self.compile_expression_list()
        self.t.expect(')')
        self.w.write_call(full_name, n_args)

    def compile_expression_list(self) -> int:
        n = 0
        if self.t.peek().value != ')':
            self.compile_expression(); n = 1
            while self.t.peek().value == ',':
                self.t.advance(); self.compile_expression(); n += 1
        return n

# -------------------------
# Driver
# -------------------------
def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    for f in (path.glob('*.jack') if path.is_dir() else [path]):
        tokenizer = Tokenizer(f.read_text())
        writer = VMWriter(f.with_suffix('.vm'))
        engine = CompilationEngine(tokenizer, writer)
        try:
            engine.compile_class()
            print(f"Done: {f.name}")
        except Exception as e:
            print(f"Error in {f.name}: {e}")
        finally:
            writer.close()

if __name__ == '__main__':
    main()