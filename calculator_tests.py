import pytest

# ==================== КОД КАЛЬКУЛЯТОРА ====================

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
            return -schet(val)
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
            if b == 0:
                raise Exception("Деление на ноль")
            return a / b
        if oper == '//':
            if b == 0:
                raise Exception("Деление на ноль")
            return a // b
        if oper == '%':
            if b == 0:
                raise Exception("Деление на ноль")
            return a % b
        if oper == '**':
            return a ** b
    raise Exception("Неизвестная операция")

def calculate(expression):
    tokens = tokenize(expression)
    parser = Parse(tokens)
    ast = parser.expr()
    return schet(ast)

# ==================== ТЕСТЫ Pytest ====================

def test_add():
    assert calculate("7 + 8") == 15
    assert calculate("15 + 25 + 35") == 75

def test_sub():
    assert calculate("17 - 9") == 8
    assert calculate("6 - 19") == -13

def test_mul():
    assert calculate("5 * 6") == 30
    assert calculate("3 * 4 * 5") == 60

def test_div():
    assert calculate("15 / 3") == 5
    assert calculate("11 / 4") == 2.75

def test_int_div():
    assert calculate("17 // 5") == 3
    assert calculate("9 // 2") == 4

def test_mod():
    assert calculate("14 % 5") == 4
    assert calculate("8 % 3") == 2

def test_pow():
    assert calculate("3 ** 4") == 81
    assert calculate("4 ** 3") == 64

def test_priority():
    assert calculate("5 + 6 * 7") == 47
    assert calculate("(5 + 6) * 7") == 77
    assert calculate("4 * 5 + 6") == 26
    assert calculate("3 ** 4 * 5") == 405
    assert calculate("4 * 3 ** 2") == 36

def test_unary():
    assert calculate("-8") == -8
    assert calculate("+12") == 12
    assert calculate("-3 ** 2") == -9
    assert calculate("-(7 + 8)") == -15

def test_complex():
    assert calculate("7 + 8 * 9 - 10") == 69
    assert calculate("(7 + 8) * (9 - 4)") == 75
    assert calculate("17 // 5 + 17 % 5") == 6
    assert calculate("2 ** 3 ** 2") == 512
    assert calculate("100 - 50 + 25 * 2") == 100

def test_spaces():
    assert calculate("  7  +  8  ") == 15
    assert calculate("( 7 + 8 ) * 9") == 135

def test_zero_division():
    with pytest.raises(Exception, match="Деление на ноль"):
        calculate("15 / 0")
    with pytest.raises(Exception, match="Деление на ноль"):
        calculate("20 // 0")
    with pytest.raises(Exception, match="Деление на ноль"):
        calculate("25 % 0")

def test_bad_chars():
    with pytest.raises(Exception, match="плохой символ"):
        calculate("7 # 8")
    with pytest.raises(Exception, match="плохой символ"):
        calculate("xyz")

def test_bad_brackets():
    with pytest.raises(Exception, match="Незакрытая скобка"):
        calculate("(7 + 8")

def test_bad_tokens():
    with pytest.raises(Exception, match="Неожиданный токен"):
        calculate("7 + )")
    with pytest.raises(Exception, match="Неожиданный токен"):
        calculate("* 5")

def test_simple():
    assert calculate("0") == 0
    assert calculate("1") == 1
    assert calculate("0 * 999") == 0
    assert calculate("1 ** 999") == 1
    assert calculate("999 // 999") == 1
    assert calculate("1000 - 1000") == 0

def test_big_numbers():
    assert calculate("100 + 200") == 300
    assert calculate("500 * 2") == 1000
    assert calculate("1000 // 10") == 100

def test_brackets():
    assert calculate("((7 + 8) * 3)") == 45
    assert calculate("(2 * (3 + 4))") == 14
    assert calculate("((10 - 5) * (3 + 2))") == 25

# Функция для запуска калькулятора
def main():
    print("Калькулятор запущен. Введите выражения для вычисления.")
    print("Для выхода введите 'exit'")
    
    while True:
        try:
            expression = input("> ").strip()
            if expression.lower() in ('exit', 'quit', 'выход'):
                break
            if not expression:
                continue
            
            result = calculate(expression)
            print(f"Результат: {result}")
            
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])