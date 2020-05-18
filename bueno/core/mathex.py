#
# Copyright (c)      2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Mathematical expression evaluation module.
'''

from bueno.core import metacls

from bueno.core.ply import lex
from bueno.core.ply import yacc

import typing


# A significant amount of code below was taken from the PLY classcalc example
# contributed by David McNab. Modifications made by the bueno developers.
# Some nice documentation is found here:
# https://ply.readthedocs.io/en/latest/ply.html
#
# *** We disable type checking here because of complications silencing the lex
# *** and yacc mypy errors. FIXME(skg) someday.
class _TheCalculator(metaclass=metacls.Singleton):
    tokens = (
        'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'MOD',
        'LPAREN', 'RPAREN'
    )

    # Tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\*\*'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ignore = ' \t'

    # Parsing rules
    precedence = (  # Ordered from lowest to highest precedence
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('right', 'UMINUS'),
        ('right', 'EXP')
    )

    def __init__(self) -> None:
        self.input = ''
        # Build the lexer and parser.
        self.lexer = lex.lex(module=self)  # type: ignore
        self.parser = yacc.yacc(module=self)  # type: ignore

    @typing.no_type_check
    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError as e:
            emsg = F'{__name__}: {e} (erroneous value is {t.value}).'
            emsg += F'\nInput was: {self.input}'
            raise(ValueError(emsg))
        return t

    @typing.no_type_check
    def t_error(self, t):
        emsg = F"{__name__}: Illegal character detected: '{t.value[0]}'."
        emsg += F'\nInput was: {self.input}'
        raise SyntaxError(emsg)

    @typing.no_type_check
    def p_statement_expr(self, p):
        'statement : expression'
        p[0] = p[1]

    @typing.no_type_check
    def p_expression_binop(self, p):
        '''
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | expression MOD expression
                   | expression EXP expression
        '''
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]

    @typing.no_type_check
    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    @typing.no_type_check
    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    @typing.no_type_check
    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    @typing.no_type_check
    def p_error(self, p):
        emsg = self._nice_syntax_error_msg(p)
        raise SyntaxError(emsg)

    @typing.no_type_check
    def _nice_syntax_error_msg(self, p=None):
        pos = len(self.input)
        if p is not None:
            pos = p.lexpos
        emsg = F"{__name__}: Syntax error at index {pos}."
        offset = '~' * pos
        mark = offset + '^'
        return F'{emsg}\n{self.input}\n{mark}'

    def evaluate(self, s: str) -> int:
        # Keep a copy around at class scope for nicer error reporting.
        self.input = s
        resstr = self.parser.parse(self.input, self.lexer)
        result = 0
        try:
            result = int(resstr)
        except ValueError:
            e = 'An error occurred while attempting to evaluate the following:'
            pab = 'This is probably a bug, so please file a report.'
            raise ValueError(F'{e}\n{s}\n{pab}')
        return result


def evaluate(expr: str) -> int:
    '''
    Evaluates the given string using integer arithmetic and returns its result.
    If the provided expression is malformed, then an exception is raised.
    '''
    return _TheCalculator().evaluate(expr)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
