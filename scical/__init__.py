from collections import namedtuple
import re

from scical import callib


def parse(expr):
    token_map = {'+': 'ADD', '-': 'ADD',
                 '*': 'MUL', '/': 'MUL',
                 '(': 'LPAR', ')': 'RPAR'}

    Token = namedtuple('Token', ['name', 'value'])

    split_expr = re.findall('[\d.]+|[{}]'.format('\\'.join(token_map)), expr)
    tokens = [Token(token_map.get(x, 'NUM'), x) for x in split_expr]

    tree = callib.match('add', tokens)[0]
    tree = callib.flatten_right_associativity(tree)

    return callib.evaluate(tree)


if __name__ == '__main__':
    formula = '1.2 / (11+3)'
    print(parse(formula))
