from pyparsing import ParserElement, infixNotation, opAssoc, CaselessKeyword, Word, alphas, alphanums, pyparsing_unicode, Suppress, Regex
from typing import Callable

class ASTNode:
    def __init__(self) -> None:
        pass
    
    def visit(self, visit_fun):
        return visit_fun(self)

class ANDNode(ASTNode):
    def __init__(self, lchild: ASTNode, rchild: ASTNode) -> None:
        super().__init__()
        self.type = "AND"
        self.lchild = lchild
        self.rchild = rchild

class ORNode(ASTNode):
    def __init__(self, lchild: ASTNode, rchild: ASTNode) -> None:
        super().__init__()
        self.type = "OR"
        self.lchild = lchild
        self.rchild = rchild

class NOTNode(ASTNode):
    def __init__(self, child: ASTNode) -> None:
        super().__init__()
        self.type = "NOT"
        self.child = child

class QUERYNode(ASTNode):
    def __init__(self, query: str) -> None:
        super().__init__()
        self.type = "QUERY"
        self.query = query


class QueryCompilerFrontEnd:
    def __init__(self) -> None:
        ParserElement.setDefaultWhitespaceChars(' \t')
        identifier = Regex(r"[\w\u4e00-\u9fff]+")
        AND = CaselessKeyword("AND")
        OR = CaselessKeyword("OR")
        NOT = CaselessKeyword("NOT")
        LPAREN = Suppress("(")
        RPAREN = Suppress(")")

        self.parser = infixNotation(
            identifier,
            [
                (NOT, 1, opAssoc.RIGHT),
                (AND, 2, opAssoc.LEFT),
                (OR, 2, opAssoc.LEFT),
                (LPAREN, 1, opAssoc.LEFT),
                (RPAREN, 1, opAssoc.RIGHT),
            ],
        )
    
    def _build_ast(self, parsed_list: list):
        if type(parsed_list) == str:
            return QUERYNode(parsed_list)
        if parsed_list[0] == 'NOT' or parsed_list[0] == 'not':
            child = self._build_ast(parsed_list[1])
            return NOTNode(child)
        elif parsed_list[1] == 'AND' or parsed_list[0] == 'and':
            lchild = self._build_ast(parsed_list[0])
            rchild = self._build_ast(parsed_list[2])
            return ANDNode(lchild, rchild)
        elif parsed_list[1] == 'OR' or parsed_list[0] == 'or':
            lchild = self._build_ast(parsed_list[0])
            rchild = self._build_ast(parsed_list[2])
            return ORNode(lchild, rchild)
        return ASTNode()
    
    def parse(self, query: str):
        parsed_list = self.parser.parseString(query).as_list()
        ast = self._build_ast(parsed_list[0])
        return ast

class QueryCompiler:
    def __init__(self, all_ids: list, retrieve_func: Callable) -> None:
        self.frontend = QueryCompilerFrontEnd()
        self.all_ids = all_ids
        self.retrieve_func = retrieve_func
        return

    def execute(self, query: str, precise=False):
        ast = self.frontend.parse(query)
        def visit_fun(ast_node: ASTNode):
            if isinstance(ast_node, ANDNode):
                lans = ast_node.lchild.visit(visit_fun)
                rans = ast_node.rchild.visit(visit_fun)
                ans = [x for x in lans if x in rans]
                return ans
            if isinstance(ast_node, ORNode):
                lans = ast_node.lchild.visit(visit_fun)
                rans = ast_node.rchild.visit(visit_fun)
                ans = lans + rans
                return ans
            if isinstance(ast_node, NOTNode):
                ans = ast_node.child.visit(visit_fun)
                return [x for x in self.all_ids if x not in ans]
            if isinstance(ast_node, QUERYNode):
                ans = self.retrieve_func([ast_node.query], precise=precise)[0]
                return ans
            return NotImplementedError()
        return ast.visit(visit_fun)

    def filter(self, query: str, words: list[str]):
        ast = self.frontend.parse(query)
        def visit_fun(ast_node: ASTNode):
            if isinstance(ast_node, ANDNode):
                lans = ast_node.lchild.visit(visit_fun)
                rans = ast_node.rchild.visit(visit_fun)
                return lans and rans
            if isinstance(ast_node, ORNode):
                lans = ast_node.lchild.visit(visit_fun)
                rans = ast_node.rchild.visit(visit_fun)
                return lans or rans
            if isinstance(ast_node, NOTNode):
                ans = ast_node.child.visit(visit_fun)
                return not ans
            if isinstance(ast_node, QUERYNode):
                for word in words:
                    if ast_node.query in word:
                        return True
                return False
            return NotImplementedError()
        return ast.visit(visit_fun)
        



