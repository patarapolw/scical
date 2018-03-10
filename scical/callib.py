from operator import add,sub,mul,truediv
from collections import namedtuple

RuleMatch = namedtuple('RuleMatch', ['name', 'matched'])

rule_map = {
    'add': ['mul ADD add', 'mul'],
    'mul': ['atom MUL mul', 'atom'],
    'atom': ['NUM', 'LPAR add RPAR', 'neg'],
    'neg': ['ADD atom'],
}


def match(rule_name, tokens):
    if tokens and rule_name == tokens[0].name:  # Match a token?
        return RuleMatch(tokens[0], tokens[1:])
    for expansion in rule_map.get(rule_name, ()):  # Match a rule?
        remaining_tokens = tokens
        matched_subrules = []
        for subrule in expansion.split():
            matched, remaining_tokens = match(subrule, remaining_tokens)
            if not matched:
                break  # no such luck. next expansion!
            matched_subrules.append(matched)
        else:
            return RuleMatch(rule_name, matched_subrules), remaining_tokens
    return None, None  # match not found


fix_assoc_rules = 'add', 'mul'


def _recurse_tree(tree, func):
    return map(func, tree.matched) if tree.name in rule_map else tree[1]


def flatten_right_associativity(tree):
    new = _recurse_tree(tree, flatten_right_associativity)
    if tree.name in fix_assoc_rules and len(new) == 3 and new[2].name == tree.name:
        new[-1:] = new[-1].matched
    return RuleMatch(tree.name, new)


def build_left_associativity(tree):
    new_nodes = _recurse_tree(tree, build_left_associativity)
    if tree.name in fix_assoc_rules:
        while len(new_nodes) > 3:
            new_nodes[:3] = [RuleMatch(tree.name, new_nodes[:3])]
    return RuleMatch(tree.name, new_nodes)


bin_calc_map = {'*': mul, '/': truediv, '+': add, '-': sub}


def calc_binary(x):
    while len(x) > 1:
        x[:3] = [bin_calc_map[x[1]](x[0], x[2])]
    return x[0]


calc_map = {
    'NUM': float,
    'atom': lambda x: x[len(x) != 1],
    'neg': lambda op, num: (num, -num)[op == '-'],
    'mul': calc_binary,
    'add': calc_binary,
}


def evaluate(tree):
    solutions = _recurse_tree(tree, evaluate)
    return calc_map.get(tree.name, lambda x: x)(solutions)
