import re
import itertools
from operator import add, sub, mul, truediv, pow


class Calculator:
    def __init__(self):
        self.operator = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '^': 'EXP',
        }

        self.brackets = [
            ('(', ')'),
            ('[', ']'),
            ('{', '}')
        ]

        self._token_type = self.operator.copy()
        self._token_type.update([(bracket, 'PAR') for bracket in itertools.chain(*self.brackets)])

    def from_expr(self, expr):
        split_expr = re.findall('[\d.]+|[{}]'.format(''.join(['\\'+token for token in self._token_type])), expr)
        self._tokens = [(self._token_type.get(x, 'NUM'), x) for x in split_expr]
        self._rpn = self._to_rpn()

    def from_rpn(self, rpn_string):
        rpn = rpn_string.split(' ')
        self._rpn = [(self._token_type.get(value, 'NUM'), value) for value in rpn]

    def result(self):
        calc_map = {
            'ADD': add,
            'SUB': sub,
            'MUL': mul,
            'DIV': truediv,
            'EXP': pow,
        }

        def operate_rpn(rpn):
            if len(rpn) == 1:
                return rpn[0]
            for i, item in enumerate(rpn):
                type, value = item
                if type in self.operator.values():
                    new_rpn = rpn[:i-2] \
                              + [('NUM', calc_map[type](float(rpn[i-2][1]), float(rpn[i-1][1])))] \
                              + rpn[i+1:]
                    return operate_rpn(new_rpn)

        return operate_rpn(self._rpn)[1]


    def _to_rpn(self):
        rule_sequence = [
            ('X', ['EXP']),
            # B
            # O
            ('D', ['DIV']),
            ('M', ['MUL']),
            ('AS', ['ADD', 'SUB']),
        ]

        result = []
        op_order = 0
        tokens = self._tokens
        used_token = []
        all_brackets = list(itertools.chain(*self.brackets))

        def find_matching_brackets(input_bracket):
            to_find = None
            for bracket_pair in self.brackets:
                if input_bracket in bracket_pair:
                    if input_bracket == bracket_pair[0]:
                        to_find = bracket_pair[1]
                    else:
                        to_find = bracket_pair[0]
                    break

            for i, token in enumerate(tokens):
                if token[1] == to_find:
                    return i
            return -1

        for rule in rule_sequence:
            for i, token in enumerate(tokens):
                if token in used_token:
                    continue
                if token[0] in rule[1]:
                    result.append((op_order, token))
                    used_token.append(token)
                    op_order += 1
                    adjacent = [i-1, i+1]
                    for j in [i-1, i+1]:
                        if tokens[j][1] in all_brackets:
                            adjacent.append(find_matching_brackets(tokens[j][1]))
                    for j in adjacent:
                        result.append((op_order, tokens[j]))
                        used_token.append(token)
                    op_order += 1

        return [token for rule_order, token in sorted(result, reverse=True) if token[1] not in all_brackets]

    def to_rpn(self):
        return [token[1] for token in self._to_rpn()]


def parse(expr):
    calculator = Calculator()
    calculator.from_expr(expr)
    return calculator.result()


def parse_rpn(rpn_string):
    calculator = Calculator()
    calculator.from_rpn(rpn_string)
    return calculator.result()


if __name__ == '__main__':
    formula = '( 6 - 3) ^2 - 11'
    print(parse(formula))
    rpn_string = '162 2 1 + 4 ^ /'
    print(parse_rpn(rpn_string))
