class Parse:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def cur_token(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def sled_token(self):
        self.pos += 1

    def expr(self):
        return self.add()

    def add(self):
        node = self.mul()
        while self.cur_token() and self.cur_token()[1] in ('+','-'):
            op = self.cur_token()[1]
            self.sled_token()
            node = (op, node, self.mul())
        return node

    def mul(self):
        node = self.pow()
        while self.cur_token() and self.cur_token()[1] in ('*','/','//','%'):
            op = self.cur_token()[1]
            self.sled_token()
            node = (op, node, self.pow())
        return node

    def pow(self):
        node = self.unary()
        if self.cur_token() and self.cur_token()[1] == '**':
            self.sled_token()
            node = ('**', node, self.pow())
        return node

    def unary(self):
        if self.cur_token() and self.cur_token()[1] in ('+','-'):
            op = self.cur_token()[1]
            self.sled_token()
            return (op, self.unary())
        return self.primary()

    def primary(self):
        token = self.cur_token()
        if not token:
            raise Exception("плохой конец выражения")
        if token[0] == 'NUM':
            value = token[1]
            self.sled_token()
            return value
        elif token[1] == '(':
            self.sled_token()
            expr = self.expr()
            if not self.cur_token() or self.cur_token()[1] != ')':
                raise Exception("Незакрытая скобка")
            self.sled_token()
            return expr
        else:
            raise Exception(f"Неожиданный токен: {token}")


def tokenize(expression):
    tokens = []
    i = 0
    while i < len(expression):
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char.isdigit():
            num = ''
            while i < len(expression) and expression[i].isdigit():
                num += expression[i]
                i += 1
            tokens.append(('NUM', int(num)))
            continue
        if char in '+-*/()%':
            if i + 1 < len(expression) and char + expression[i + 1] in ('**', '//'):
                tokens.append(('OP', char + expression[i + 1]))
                i += 2
            else:
                tokens.append(('OP', char))
                i += 1
            continue
        raise Exception(f"плохой символ: {char}")
    return tokens


def schet(ast):
    if type(ast) in (int, float):
        return ast
    if len(ast) == 2:
        oper, val = ast
        if oper == '+':
            return schet(val)
        if oper == '-':
            return schet(val)
    if len(ast) == 3:
        oper, left, right = ast
        a = schet(left)
        b = schet(right)
        if oper == '+':
            return a + b
        if oper == '-':
            return a - b
        if oper == '*':
            return a * b
        if oper == '/':
            return a / b
        if oper == '//':
            return a // b
        if oper == '%':
            return a % b
        if oper == '**':
            return a ** b
    raise Exception("Неизвестная операция")


while True:
    expression = input()
    try:
        tokens = tokenize(expression)
        parser = Parse(tokens)
        ast = parser.expr()
        result = schet(ast)
        print(result)
    except Exception as fu_ploho:
        print(f"Ошибка: {fu_ploho}")