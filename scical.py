#! /usr/bin/env python

"""
Input a calculator expression string or a RPN, output the result.

Todo: Verify the string and the RPN.
"""

import re
import itertools
from operator import add, sub, mul, truediv

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class Calculator:
    """ Calculator class calculating both calculator expression strings and RPN's """

    operator = [
        ('+', 'ADD', add, 'L2R'),
        ('-', 'SUB', sub, 'L2R'),
        ('*', 'MUL', mul, 'L2R'),
        ('/', 'DIV', truediv, 'R2L'),
        ('^', 'EXP', pow, 'R2L')
    ]

    brackets = [
        ('(', ')'),
        ('[', ']'),
        ('{', '}')
    ]

    rule_sequence = [
        ('X', ['EXP']),
        # B
        # O
        ('D', ['DIV']),
        ('M', ['MUL']),
        ('AS', ['ADD', 'SUB']),
    ]

    def __init__(self):
        self._token_type = dict((key, val) for key, val, op, direction in self.operator)
        self._token_type.update([(bracket, 'PAR') for bracket in itertools.chain(*self.brackets)])
        self._tokens = None
        self.rpn = None

    def from_expr(self, expr):
        """ Input a calculator string expression. Return the calculation result. """
        split_expr = re.findall(r'[\d.]+|[{}]'
                                .format(''.join(['\\'+token for token in self._token_type])), expr)
        self._tokens = [(self._token_type.get(x, 'NUM'), x) for x in split_expr]
        self.rpn = self._to_rpn()

        return self._to_result()

    def from_rpn(self, rpn_string):
        """ Input a RPN string, separated by space. Return the calculation result. """
        rpn = re.findall(r'[\d.]+|[{}]'
                         .format(''.join(['\\'+token for token in self._token_type])), rpn_string)
        self.rpn = [(self._token_type.get(value, 'NUM'), value) for value in rpn]

        return self._to_result()

    def _to_result(self):
        """ Convert computer-readble RPN to calculation result """
        def operate_rpn(rpn):
            """ A recursion function to calculate the RPN. """
            if len(rpn) == 1:
                return rpn[0]
            for i, item in enumerate(rpn):
                for _, token_type, operation, _ in self.operator:
                    if item[0] == token_type:
                        new_rpn = rpn[:i-2] \
                                  + [('NUM', operation(float(rpn[i-2][1]), float(rpn[i-1][1])))] \
                                  + rpn[i+1:]
                        return operate_rpn(new_rpn)
            return rpn[0]

        return operate_rpn(self.rpn)[1]

    def _to_rpn(self):
        """ Convert list of tokens to a computer-readable RPN """
        tokens = self._tokens

        def find_matching_brackets(input_bracket):
            """ Input a bracket and detect the bracket pair in the list of tokens. """
            to_find = None
            for bracket_pair in self.brackets:
                if input_bracket in bracket_pair:
                    if input_bracket == bracket_pair[0]:
                        to_find = bracket_pair[1]
                    else:
                        to_find = bracket_pair[0]
                    break

            for token in tokens:
                if token[1] == to_find:
                    return token
            return None

        num_stack = []
        op_stack = [[]]
        min_rule = None
        bracket_level = 0

        def purge():
            """ Purge the operation stack to the number stack """
            nonlocal op_stack

            for operation in op_stack[bracket_level][::-1]:
                num_stack.append(operation)
            op_stack[bracket_level] = []

        def purge_on_rule_violation(token):
            """ Detects whether BODMAS has be violated. If so, purge the RPN. """
            logging.debug('Rule violation, purging...')

            def get_rule_seq(token):
                """ Return the sequence of operation according to BODMAS. """
                for i, item in enumerate(self.rule_sequence):
                    if token[0] in item[1]:
                        return i
                return -1

            nonlocal min_rule  # The previous order of operations.

            if min_rule is not None:
                if get_rule_seq(token) > min_rule:
                    purge()
                    min_rule = None
                else:
                    min_rule = get_rule_seq(token)
            else:
                min_rule = get_rule_seq(token)

        pair_bracket = None

        logging.debug('Bracket level: %s', bracket_level)
        for token in tokens:
            if pair_bracket == token:
                purge()
                pair_bracket = None
                op_stack = op_stack[:-1]
                bracket_level -= 1
                logging.debug('Found closing bracket, purging...')
                logging.debug('Op_stack: %s', op_stack)
                logging.debug('Bracket level: %s', bracket_level)
            elif token[0] == 'NUM':
                num_stack.append(token)
                logging.debug('Num_stack: %s', num_stack)
            elif token[0] == 'PAR':
                pair_bracket = find_matching_brackets(token[1])
                op_stack.append([])
                bracket_level += 1
                logging.debug('Found opening bracket')
                logging.debug('Bracket level: %s', bracket_level)
            else:
                purge_on_rule_violation(token)
                op_stack[bracket_level].append(token)
                logging.debug('Op_stack: %s', op_stack)

        purge()  # Finalizing purge so that everything is outputted.

        return num_stack

    def to_rpn(self):
        """ Outputs a human readable RPN """
        return [token[1] for token in self._to_rpn()]


def parse(expr):
    """ Short hand to parse calculator string expression """
    calculator = Calculator()
    return calculator.from_expr(expr)


def parse_rpn(rpn_string):
    """ Short hand to parse RPN """
    calculator = Calculator()
    return calculator.from_rpn(rpn_string)


def main():
    """ Main function """
    formula = '162 / (2 + 1 ) ^4'
    calculator = Calculator()
    print(calculator.from_expr(formula))


if __name__ == '__main__':
    main()
