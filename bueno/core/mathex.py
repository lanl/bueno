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

import ast
import operator
import typing

from bueno.core import metacls


class _TheCalculator(metaclass=metacls.Singleton):  # pylint: disable=R0903
    '''
    Private class that is responsible for all the heavy lifting behind
    evaluate().
    '''
    def __init__(self) -> None:
        # The current input string.
        self.input = ''
        # Supported unary operators.
        self.uni_ops = {
            ast.USub: operator.neg
        }
        # Supported binary operators.
        self.bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow
        }

    @typing.no_type_check
    def _nice_syntax_error_msg(self, msg: str, node=None) -> str:
        pos = len(self.input)
        if node is not None:
            pos = node.col_offset
        emsg = F'{__name__}: Syntax error at index {pos} ({msg}).'
        offset = '~' * pos
        mark = offset + '^'
        return F'{emsg}\n{self.input}\n{mark}'

    @typing.no_type_check
    def _eval(self, node):
        if isinstance(node, ast.Expression):
            return self._eval(node.body)
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.UnaryOp):
            nodeop_type = type(node.op)
            nodeop_op = self.uni_ops.get(nodeop_type, None)
            if nodeop_op is None:
                msg = 'Unexpected operator'
                raise SyntaxError(self._nice_syntax_error_msg(msg, node))
            return nodeop_op(self._eval(node.operand))
        if isinstance(node, ast.BinOp):
            nodeop_type = type(node.op)
            nodeop_op = self.bin_ops.get(nodeop_type, None)
            if nodeop_op is None:
                msg = 'Unexpected operator'
                raise SyntaxError(self._nice_syntax_error_msg(msg, node))
            return nodeop_op(self._eval(node.left), self._eval(node.right))
        msg = 'An error occurred while evaluating the following expression'
        raise SyntaxError(self._nice_syntax_error_msg(msg, node))

    def evaluate(self, estr: str) -> int:
        '''
        Attempts to evaluate the provided expression. Returns the value yielded
        by the provided arithmetic expression cast to an integer.  If the
        provided expression is malformed, then an exception is raised.
        '''
        self.input = estr
        node = ast.parse(estr, mode='eval')
        return int(self._eval(node))


def evaluate(expr: str) -> int:
    '''
    Evaluates the given arithmetic expression and returns its result cast to an
    integer.  If the provided expression is malformed, then an exception is
    raised.
    '''
    return _TheCalculator().evaluate(expr)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
