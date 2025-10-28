lab1/
├── src/
│   ├── main.py
│   ├── calculator.py
│   ├── constants.py
│   └── __init__.py
├── tests/
│   ├── test_calculator.py
│   └── __init__.py
├── uv.lock
├── report.pdf (не нашла как его сделать)
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
"""Константы для калькулятора."""

SUPPORTED_OPERATIONS = {'+', '-', '*', '/', '//', '%', '**'}
BRACKETS = {'(', ')'}
WHITESPACE_CHARS = {' ', '\t', '\n'}

"""Модуль калькулятора для вычисления арифметических выражений."""

from typing import List, Tuple, Union, Any
from .constants import SUPPORTED_OPERATIONS, BRACKETS, WHITESPACE_CHARS


class Parser:
    """Парсер для разбора математических выражений."""
    
    def __init__(self, tokens: List[Tuple[str, Any]]) -> None:
        """
        Инициализация парсера.
        
        Args:
            tokens: Список токенов для разбора
        """
        self.tokens = tokens
        self.position = 0
    
    def get_current_token(self) -> Union[Tuple[str, Any], None]:
        """
        Получить текущий токен.
        
        Returns:
            Текущий токен или None если токены закончились
        """
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]
    
    def next_token(self) -> None:
        """Перейти к следующему токену."""
        self.position += 1
    
    def parse_expression(self) -> Any:
        """
        Разобрать выражение.
        
        Returns:
            Абстрактное синтаксическое дерево выражения
        """
        return self.parse_addition()
    
    def parse_addition(self) -> Any:
        """
        Разобрать операции сложения и вычитания.
        
        Returns:
            AST для операций + и -
        """
        node = self.parse_multiplication()
        
        while (self.get_current_token() and 
               self.get_current_token()[1] in ('+', '-')):
            operator = self.get_current_token()[1]
            self.next_token()
            node = (operator, node, self.parse_multiplication())
        
        return node
    
    def parse_multiplication(self) -> Any:
        """
        Разобрать операции умножения, деления и остатка.
        
        Returns:
            AST для операций *, /, //, %
        """
        node = self.parse_power()
        
        while (self.get_current_token() and 
               self.get_current_token()[1] in ('*', '/', '//', '%')):
            operator = self.get_current_token()[1]
            self.next_token()
            node = (operator, node, self.parse_power())
        
        return node
    
    def parse_power(self) -> Any:
        """
        Разобрать операцию возведения в степень.
        
        Returns:
            AST для операции **
        """
        node = self.parse_unary()
        
        if self.get_current_token() and self.get_current_token()[1] == '**':
            self.next_token()
            node = ('**', node, self.parse_power())
        
        return node
    
    def parse_unary(self) -> Any:
        """
        Разобрать унарные операции.
        
        Returns:
            AST для унарных + и -
        """
        if (self.get_current_token() and 
            self.get_current_token()[1] in ('+', '-')):
            operator = self.get_current_token()[1]
            self.next_token()
            return (operator, self.parse_unary())
        
        return self.parse_primary()
    
    def parse_primary(self) -> Any:
        """
        Разобрать первичные выражения (числа и скобки).
        
        Returns:
            AST для чисел или выражений в скобках
            
        Raises:
            Exception: При синтаксических ошибках
        """
        token = self.get_current_token()
        if not token:
            raise Exception("Неожиданный конец выражения")
        
        if token[0] == 'NUMBER':
            value = token[1]
            self.next_token()
            return value
        
        elif token[1] == '(':
            self.next_token()
            expression = self.parse_expression()
            
            if not self.get_current_token() or self.get_current_token()[1] != ')':
                raise Exception("Незакрытая скобка")
            
            self.next_token()
            return expression
        
        else:
            raise Exception(f"Неожиданный токен: {token}")


def tokenize(expression: str) -> List[Tuple[str, Any]]:
    """
    Разбить строку на токены.
    
    Args:
        expression: Строка с математическим выражением
        
    Returns:
        Список токенов
        
    Raises:
        Exception: При наличии неподдерживаемых символов
    """
    tokens = []
    index = 0
    
    while index < len(expression):
        char = expression[index]
        
        if char in WHITESPACE_CHARS:
            index += 1
            continue
        
        if char.isdigit():
            number_str = ''
            while index < len(expression) and expression[index].isdigit():
                number_str += expression[index]
                index += 1
            tokens.append(('NUMBER', int(number_str)))
            continue
        
        if char in SUPPORTED_OPERATIONS or char in BRACKETS:
            if (index + 1 < len(expression) and 
                char + expression[index + 1] in ('**', '//')):
                tokens.append(('OPERATOR', char + expression[index + 1]))
                index += 2
            else:
                tokens.append(('OPERATOR', char))
                index += 1
            continue
        
        raise Exception(f"Неподдерживаемый символ: {char}")
    
    return tokens


def evaluate_ast(ast: Any) -> Union[int, float]:
    """
    Вычислить значение абстрактного синтаксического дерева.
    
    Args:
        ast: Абстрактное синтаксическое дерево
        
    Returns:
        Результат вычисления выражения
        
    Raises:
        Exception: При неизвестных операциях или делении на ноль
    """
    if isinstance(ast, (int, float)):
        return ast
    
    if len(ast) == 2:
        operator, value = ast
        if operator == '+':
            return evaluate_ast(value)
        if operator == '-':
            return -evaluate_ast(value)
    
    if len(ast) == 3:
        operator, left, right = ast
        left_value = evaluate_ast(left)
        right_value = evaluate_ast(right)
        
        if operator == '+':
            return left_value + right_value
        elif operator == '-':
            return left_value - right_value
        elif operator == '*':
            return left_value * right_value
        elif operator == '/':
            if right_value == 0:
                raise Exception("Деление на ноль")
            return left_value / right_value
        elif operator == '//':
            if right_value == 0:
                raise Exception("Деление на ноль")
            return left_value // right_value
        elif operator == '%':
            if right_value == 0:
                raise Exception("Деление на ноль")
            return left_value % right_value
        elif operator == '**':
            return left_value ** right_value
    
    raise Exception("Неизвестная операция")


def calculate_expression(expression: str) -> Union[int, float]:
    """
    Вычислить математическое выражение.
    
    Args:
        expression: Строка с математическим выражением
        
    Returns:
        Результат вычисления
        
    Raises:
        Exception: При ошибках разбора или вычисления
    """
    tokens = tokenize(expression)
    parser = Parser(tokens)
    ast = parser.parse_expression()
    return evaluate_ast(ast)
