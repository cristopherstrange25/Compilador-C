import ply.yacc as yacc
from .lexer import Lexer
from .utils import format_ast_for_visualization

class Node:
    """Base class for AST nodes."""
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf

    def __str__(self):
        return f"{self.type}: {self.leaf if self.leaf else ''}"
    
    def to_dict(self):
        """Convert the node to a dictionary for JSON serialization."""
        result = {
            'type': self.type
        }
        if self.leaf is not None:
            result['value'] = str(self.leaf)
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result

class Parser:
    """
    Syntax analyzer for C code. Builds an Abstract Syntax Tree (AST) from tokens.
    """
    
    def __init__(self, lexer=None):
        """Initialize the parser with a lexer."""
        self.lexer = lexer if lexer else Lexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=True)
        self.ast = None
        self.errors = []
    
    # Grammar rules
    def p_translation_unit(self, p):
        '''
        translation_unit : external_declaration
                        | translation_unit external_declaration
        '''
        if len(p) == 2:
            p[0] = Node('translation_unit', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
    
    def p_external_declaration(self, p):
        '''
        external_declaration : function_definition
                            | declaration
        '''
        p[0] = Node('external_declaration', [p[1]])
    
    def p_function_definition(self, p):
        '''
        function_definition : declaration_specifiers declarator compound_statement
                           | declarator compound_statement
        '''
        if len(p) == 4:
            p[0] = Node('function_definition', [p[1], p[2], p[3]])
        else:
            p[0] = Node('function_definition', [p[1], p[2]])
    
    def p_declaration(self, p):
        '''
        declaration : declaration_specifiers init_declarator_list SEMI
                    | declaration_specifiers SEMI
        '''
        if len(p) == 4:
            p[0] = Node('declaration', [p[1], p[2]])
        else:
            p[0] = Node('declaration', [p[1]])
    
    def p_declaration_specifiers(self, p):
        '''
        declaration_specifiers : storage_class_specifier
                               | storage_class_specifier declaration_specifiers
                               | type_specifier
                               | type_specifier declaration_specifiers
                               | type_qualifier
                               | type_qualifier declaration_specifiers
        '''
        if len(p) == 2:
            p[0] = Node('declaration_specifiers', [p[1]])
        else:
            p[0] = Node('declaration_specifiers', [p[1], p[2]])
    
    def p_storage_class_specifier(self, p):
        '''
        storage_class_specifier : AUTO
                                | REGISTER
                                | STATIC
                                | EXTERN
                                | TYPEDEF
        '''
        p[0] = Node('storage_class_specifier', leaf=p[1])
    
    def p_type_specifier(self, p):
        '''
        type_specifier : VOID
                       | CHAR
                       | SHORT
                       | INT
                       | LONG
                       | FLOAT
                       | DOUBLE
                       | SIGNED
                       | UNSIGNED
                       | struct_or_union_specifier
                       | enum_specifier
                       | typedef_name
        '''
        if isinstance(p[1], str):
            p[0] = Node('type_specifier', leaf=p[1])
        else:
            p[0] = Node('type_specifier', [p[1]])
    
    def p_struct_or_union_specifier(self, p):
        '''
        struct_or_union_specifier : struct_or_union ID LBRACE struct_declaration_list RBRACE
                                  | struct_or_union LBRACE struct_declaration_list RBRACE
                                  | struct_or_union ID
        '''
        if len(p) == 6:
            p[0] = Node('struct_or_union_specifier', [p[1], Node('id', leaf=p[2]), p[4]])
        elif len(p) == 5:
            p[0] = Node('struct_or_union_specifier', [p[1], p[3]])
        else:
            p[0] = Node('struct_or_union_specifier', [p[1], Node('id', leaf=p[2])])
    
    def p_struct_or_union(self, p):
        '''
        struct_or_union : STRUCT
                        | UNION
        '''
        p[0] = Node('struct_or_union', leaf=p[1])
    
    def p_struct_declaration_list(self, p):
        '''
        struct_declaration_list : struct_declaration
                                | struct_declaration_list struct_declaration
        '''
        if len(p) == 2:
            p[0] = Node('struct_declaration_list', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
    
    def p_struct_declaration(self, p):
        '''
        struct_declaration : specifier_qualifier_list struct_declarator_list SEMI
        '''
        p[0] = Node('struct_declaration', [p[1], p[2]])
    
    def p_specifier_qualifier_list(self, p):
        '''
        specifier_qualifier_list : type_specifier
                                 | type_specifier specifier_qualifier_list
                                 | type_qualifier
                                 | type_qualifier specifier_qualifier_list
        '''
        if len(p) == 2:
            p[0] = Node('specifier_qualifier_list', [p[1]])
        else:
            p[0] = Node('specifier_qualifier_list', [p[1], p[2]])
    
    def p_struct_declarator_list(self, p):
        '''
        struct_declarator_list : struct_declarator
                               | struct_declarator_list COMMA struct_declarator
        '''
        if len(p) == 2:
            p[0] = Node('struct_declarator_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_struct_declarator(self, p):
        '''
        struct_declarator : declarator
                          | COLON constant_expression
                          | declarator COLON constant_expression
        '''
        if len(p) == 2:
            p[0] = Node('struct_declarator', [p[1]])
        elif len(p) == 3:
            p[0] = Node('struct_declarator', [p[2]])
        else:
            p[0] = Node('struct_declarator', [p[1], p[3]])
    
    def p_enum_specifier(self, p):
        '''
        enum_specifier : ENUM ID LBRACE enumerator_list RBRACE
                       | ENUM LBRACE enumerator_list RBRACE
                       | ENUM ID
        '''
        if len(p) == 6:
            p[0] = Node('enum_specifier', [Node('id', leaf=p[2]), p[4]])
        elif len(p) == 5:
            p[0] = Node('enum_specifier', [p[3]])
        else:
            p[0] = Node('enum_specifier', [Node('id', leaf=p[2])])
    
    def p_enumerator_list(self, p):
        '''
        enumerator_list : enumerator
                        | enumerator_list COMMA enumerator
        '''
        if len(p) == 2:
            p[0] = Node('enumerator_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_enumerator(self, p):
        '''
        enumerator : ID
                   | ID EQUALS constant_expression
        '''
        if len(p) == 2:
            p[0] = Node('enumerator', [Node('id', leaf=p[1])])
        else:
            p[0] = Node('enumerator', [Node('id', leaf=p[1]), p[3]])
    
    def p_type_qualifier(self, p):
        '''
        type_qualifier : CONST
                       | VOLATILE
        '''
        p[0] = Node('type_qualifier', leaf=p[1])
    
    def p_declarator(self, p):
        '''
        declarator : pointer direct_declarator
                   | direct_declarator
        '''
        if len(p) == 3:
            p[0] = Node('declarator', [p[1], p[2]])
        else:
            p[0] = Node('declarator', [p[1]])
    
    def p_direct_declarator(self, p):
        '''
        direct_declarator : ID
                          | LPAREN declarator RPAREN
                          | direct_declarator LBRACKET constant_expression RBRACKET
                          | direct_declarator LBRACKET RBRACKET
                          | direct_declarator LPAREN parameter_type_list RPAREN
                          | direct_declarator LPAREN identifier_list RPAREN
                          | direct_declarator LPAREN RPAREN
        '''
        if len(p) == 2:
            p[0] = Node('direct_declarator', [Node('id', leaf=p[1])])
        elif len(p) == 4 and p[1] == '(':
            p[0] = Node('direct_declarator', [p[2]])
        elif len(p) == 4 and p[2] == '(':
            p[0] = Node('direct_declarator', [p[1]])
        elif len(p) == 4:
            p[0] = Node('direct_declarator', [p[1]])
        else:
            p[0] = Node('direct_declarator', [p[1], p[3]])
    
    def p_pointer(self, p):
        '''
        pointer : TIMES
                | TIMES type_qualifier_list
                | TIMES pointer
                | TIMES type_qualifier_list pointer
        '''
        if len(p) == 2:
            p[0] = Node('pointer')
        elif len(p) == 3:
            if p[2].type == 'pointer':
                p[0] = Node('pointer', [p[2]])
            else:
                p[0] = Node('pointer', [p[2]])
        else:
            p[0] = Node('pointer', [p[2], p[3]])
    
    def p_type_qualifier_list(self, p):
        '''
        type_qualifier_list : type_qualifier
                            | type_qualifier_list type_qualifier
        '''
        if len(p) == 2:
            p[0] = Node('type_qualifier_list', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
    
    def p_parameter_type_list(self, p):
        '''
        parameter_type_list : parameter_list
                            | parameter_list COMMA ELLIPSIS
        '''
        if len(p) == 2:
            p[0] = Node('parameter_type_list', [p[1]])
        else:
            p[0] = Node('parameter_type_list', [p[1], Node('ellipsis')])
    
    def p_parameter_list(self, p):
        '''
        parameter_list : parameter_declaration
                       | parameter_list COMMA parameter_declaration
        '''
        if len(p) == 2:
            p[0] = Node('parameter_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_parameter_declaration(self, p):
        '''
        parameter_declaration : declaration_specifiers declarator
                              | declaration_specifiers abstract_declarator
                              | declaration_specifiers
        '''
        if len(p) == 3:
            p[0] = Node('parameter_declaration', [p[1], p[2]])
        else:
            p[0] = Node('parameter_declaration', [p[1]])
    
    def p_identifier_list(self, p):
        '''
        identifier_list : ID
                        | identifier_list COMMA ID
        '''
        if len(p) == 2:
            p[0] = Node('identifier_list', [Node('id', leaf=p[1])])
        else:
            p[1].children.append(Node('id', leaf=p[3]))
            p[0] = p[1]
    
    def p_initializer(self, p):
        '''
        initializer : assignment_expression
                    | LBRACE initializer_list RBRACE
                    | LBRACE initializer_list COMMA RBRACE
        '''
        if len(p) == 2:
            p[0] = Node('initializer', [p[1]])
        elif len(p) == 4:
            p[0] = Node('initializer', [p[2]])
        else:
            p[0] = Node('initializer', [p[2]])
    
    def p_initializer_list(self, p):
        '''
        initializer_list : initializer
                         | initializer_list COMMA initializer
        '''
        if len(p) == 2:
            p[0] = Node('initializer_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_type_name(self, p):
        '''
        type_name : specifier_qualifier_list
                  | specifier_qualifier_list abstract_declarator
        '''
        if len(p) == 2:
            p[0] = Node('type_name', [p[1]])
        else:
            p[0] = Node('type_name', [p[1], p[2]])
    
    def p_abstract_declarator(self, p):
        '''
        abstract_declarator : pointer
                            | direct_abstract_declarator
                            | pointer direct_abstract_declarator
        '''
        if len(p) == 2:
            p[0] = Node('abstract_declarator', [p[1]])
        else:
            p[0] = Node('abstract_declarator', [p[1], p[2]])
    
    def p_direct_abstract_declarator(self, p):
        '''
        direct_abstract_declarator : LPAREN abstract_declarator RPAREN
                                   | LBRACKET RBRACKET
                                   | LBRACKET constant_expression RBRACKET
                                   | direct_abstract_declarator LBRACKET RBRACKET
                                   | direct_abstract_declarator LBRACKET constant_expression RBRACKET
                                   | LPAREN RPAREN
                                   | LPAREN parameter_type_list RPAREN
                                   | direct_abstract_declarator LPAREN RPAREN
                                   | direct_abstract_declarator LPAREN parameter_type_list RPAREN
        '''
        if len(p) == 4 and p[1] == '(':
            p[0] = Node('direct_abstract_declarator', [p[2]])
        elif len(p) == 3:
            p[0] = Node('direct_abstract_declarator', [])
        elif len(p) == 4 and p[1] == '[':
            p[0] = Node('direct_abstract_declarator', [p[2]])
        elif len(p) == 4:
            p[0] = Node('direct_abstract_declarator', [p[1]])
        elif len(p) == 5 and p[2] == '[':
            p[0] = Node('direct_abstract_declarator', [p[1], p[3]])
        else:
            p[0] = Node('direct_abstract_declarator', [p[1], p[3]])
    
    def p_typedef_name(self, p):
        '''
        typedef_name : ID
        '''
        p[0] = Node('typedef_name', leaf=p[1])
    
    def p_init_declarator_list(self, p):
        '''
        init_declarator_list : init_declarator
                             | init_declarator_list COMMA init_declarator
        '''
        if len(p) == 2:
            p[0] = Node('init_declarator_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_init_declarator(self, p):
        '''
        init_declarator : declarator
                        | declarator EQUALS initializer
        '''
        if len(p) == 2:
            p[0] = Node('init_declarator', [p[1]])
        else:
            p[0] = Node('init_declarator', [p[1], p[3]])
    
    def p_compound_statement(self, p):
        '''
        compound_statement : LBRACE RBRACE
                           | LBRACE statement_list RBRACE
                           | LBRACE declaration_list RBRACE
                           | LBRACE declaration_list statement_list RBRACE
        '''
        if len(p) == 3:
            p[0] = Node('compound_statement', [])
        elif len(p) == 4:
            p[0] = Node('compound_statement', [p[2]])
        else:
            p[0] = Node('compound_statement', [p[2], p[3]])
    
    def p_declaration_list(self, p):
        '''
        declaration_list : declaration
                         | declaration_list declaration
        '''
        if len(p) == 2:
            p[0] = Node('declaration_list', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
    
    def p_statement_list(self, p):
        '''
        statement_list : statement
                       | statement_list statement
        '''
        if len(p) == 2:
            p[0] = Node('statement_list', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]
    
    def p_statement(self, p):
        '''
        statement : labeled_statement
                  | compound_statement
                  | expression_statement
                  | selection_statement
                  | iteration_statement
                  | jump_statement
        '''
        p[0] = Node('statement', [p[1]])
    
    def p_labeled_statement(self, p):
        '''
        labeled_statement : ID COLON statement
                          | CASE constant_expression COLON statement
                          | DEFAULT COLON statement
        '''
        if p[1] == 'case':
            p[0] = Node('labeled_statement', [Node('case'), p[2], p[4]])
        elif p[1] == 'default':
            p[0] = Node('labeled_statement', [Node('default'), p[3]])
        else:
            p[0] = Node('labeled_statement', [Node('id', leaf=p[1]), p[3]])
    
    def p_expression_statement(self, p):
        '''
        expression_statement : SEMI
                             | expression SEMI
        '''
        if len(p) == 2:
            p[0] = Node('expression_statement', [])
        else:
            p[0] = Node('expression_statement', [p[1]])
    
    def p_selection_statement(self, p):
        '''
        selection_statement : IF LPAREN expression RPAREN statement
                            | IF LPAREN expression RPAREN statement ELSE statement
                            | SWITCH LPAREN expression RPAREN statement
        '''
        if len(p) == 6 and p[1] == 'if':
            p[0] = Node('selection_statement', [Node('if'), p[3], p[5]])
        elif len(p) == 8:
            p[0] = Node('selection_statement', [Node('if_else'), p[3], p[5], p[7]])
        else:
            p[0] = Node('selection_statement', [Node('switch'), p[3], p[5]])
    
    def p_iteration_statement(self, p):
        '''
        iteration_statement : WHILE LPAREN expression RPAREN statement
                            | DO statement WHILE LPAREN expression RPAREN SEMI
                            | FOR LPAREN expression_statement expression_statement RPAREN statement
                            | FOR LPAREN expression_statement expression_statement expression RPAREN statement
        '''
        if p[1] == 'while':
            p[0] = Node('iteration_statement', [Node('while'), p[3], p[5]])
        elif p[1] == 'do':
            p[0] = Node('iteration_statement', [Node('do_while'), p[2], p[5]])
        elif len(p) == 7:
            p[0] = Node('iteration_statement', [Node('for'), p[3], p[4], Node('empty'), p[6]])
        else:
            p[0] = Node('iteration_statement', [Node('for'), p[3], p[4], p[5], p[7]])
    
    def p_jump_statement(self, p):
        '''
        jump_statement : GOTO ID SEMI
                       | CONTINUE SEMI
                       | BREAK SEMI
                       | RETURN SEMI
                       | RETURN expression SEMI
        '''
        if p[1] == 'goto':
            p[0] = Node('jump_statement', [Node('goto'), Node('id', leaf=p[2])])
        elif p[1] == 'continue':
            p[0] = Node('jump_statement', [Node('continue')])
        elif p[1] == 'break':
            p[0] = Node('jump_statement', [Node('break')])
        elif len(p) == 3:
            p[0] = Node('jump_statement', [Node('return')])
        else:
            p[0] = Node('jump_statement', [Node('return'), p[2]])
    
    def p_expression(self, p):
        '''
        expression : assignment_expression
                   | expression COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = Node('expression', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_assignment_expression(self, p):
        '''
        assignment_expression : conditional_expression
                              | unary_expression assignment_operator assignment_expression
        '''
        if len(p) == 2:
            p[0] = Node('assignment_expression', [p[1]])
        else:
            p[0] = Node('assignment_expression', [p[1], p[2], p[3]])
    
    def p_assignment_operator(self, p):
        '''
        assignment_operator : EQUALS
                            | TIMESEQUAL
                            | DIVEQUAL
                            | MODEQUAL
                            | PLUSEQUAL
                            | MINUSEQUAL
                            | LSHIFTEQUAL
                            | RSHIFTEQUAL
                            | ANDEQUAL
                            | XOREQUAL
                            | OREQUAL
        '''
        p[0] = Node('assignment_operator', leaf=p[1])
    
    def p_conditional_expression(self, p):
        '''
        conditional_expression : logical_or_expression
                               | logical_or_expression CONDOP expression COLON conditional_expression
        '''
        if len(p) == 2:
            p[0] = Node('conditional_expression', [p[1]])
        else:
            p[0] = Node('conditional_expression', [p[1], p[3], p[5]])
    
    def p_constant_expression(self, p):
        '''
        constant_expression : conditional_expression
        '''
        p[0] = Node('constant_expression', [p[1]])
    
    def p_logical_or_expression(self, p):
        '''
        logical_or_expression : logical_and_expression
                              | logical_or_expression LOR logical_and_expression
        '''
        if len(p) == 2:
            p[0] = Node('logical_or_expression', [p[1]])
        else:
            p[0] = Node('logical_or_expression', [p[1], p[3]], leaf='||')
    
    def p_logical_and_expression(self, p):
        '''
        logical_and_expression : inclusive_or_expression
                               | logical_and_expression LAND inclusive_or_expression
        '''
        if len(p) == 2:
            p[0] = Node('logical_and_expression', [p[1]])
        else:
            p[0] = Node('logical_and_expression', [p[1], p[3]], leaf='&&')
    
    def p_inclusive_or_expression(self, p):
        '''
        inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression OR exclusive_or_expression
        '''
        if len(p) == 2:
            p[0] = Node('inclusive_or_expression', [p[1]])
        else:
            p[0] = Node('inclusive_or_expression', [p[1], p[3]], leaf='|')
    
    def p_exclusive_or_expression(self, p):
        '''
        exclusive_or_expression : and_expression
                                | exclusive_or_expression XOR and_expression
        '''
        if len(p) == 2:
            p[0] = Node('exclusive_or_expression', [p[1]])
        else:
            p[0] = Node('exclusive_or_expression', [p[1], p[3]], leaf='^')
    
    def p_and_expression(self, p):
        '''
        and_expression : equality_expression
                       | and_expression AND equality_expression
        '''
        if len(p) == 2:
            p[0] = Node('and_expression', [p[1]])
        else:
            p[0] = Node('and_expression', [p[1], p[3]], leaf='&')
    
    def p_equality_expression(self, p):
        '''
        equality_expression : relational_expression
                            | equality_expression EQ relational_expression
                            | equality_expression NE relational_expression
        '''
        if len(p) == 2:
            p[0] = Node('equality_expression', [p[1]])
        else:
            p[0] = Node('equality_expression', [p[1], p[3]], leaf=p[2])
    
    def p_relational_expression(self, p):
        '''
        relational_expression : shift_expression
                              | relational_expression LT shift_expression
                              | relational_expression GT shift_expression
                              | relational_expression LE shift_expression
                              | relational_expression GE shift_expression
        '''
        if len(p) == 2:
            p[0] = Node('relational_expression', [p[1]])
        else:
            p[0] = Node('relational_expression', [p[1], p[3]], leaf=p[2])
    
    def p_shift_expression(self, p):
        '''
        shift_expression : additive_expression
                         | shift_expression LSHIFT additive_expression
                         | shift_expression RSHIFT additive_expression
        '''
        if len(p) == 2:
            p[0] = Node('shift_expression', [p[1]])
        else:
            p[0] = Node('shift_expression', [p[1], p[3]], leaf=p[2])
    
    def p_additive_expression(self, p):
        '''
        additive_expression : multiplicative_expression
                            | additive_expression PLUS multiplicative_expression
                            | additive_expression MINUS multiplicative_expression
        '''
        if len(p) == 2:
            p[0] = Node('additive_expression', [p[1]])
        else:
            p[0] = Node('additive_expression', [p[1], p[3]], leaf=p[2])
    
    def p_multiplicative_expression(self, p):
        '''
        multiplicative_expression : cast_expression
                                  | multiplicative_expression TIMES cast_expression
                                  | multiplicative_expression DIVIDE cast_expression
                                  | multiplicative_expression MODULO cast_expression
        '''
        if len(p) == 2:
            p[0] = Node('multiplicative_expression', [p[1]])
        else:
            p[0] = Node('multiplicative_expression', [p[1], p[3]], leaf=p[2])
    
    def p_cast_expression(self, p):
        '''
        cast_expression : unary_expression
                        | LPAREN type_name RPAREN cast_expression
        '''
        if len(p) == 2:
            p[0] = Node('cast_expression', [p[1]])
        else:
            p[0] = Node('cast_expression', [p[2], p[4]], leaf='cast')
    
    def p_unary_expression(self, p):
        '''
        unary_expression : postfix_expression
                         | PLUSPLUS unary_expression
                         | MINUSMINUS unary_expression
                         | unary_operator cast_expression
                         | SIZEOF unary_expression
                         | SIZEOF LPAREN type_name RPAREN
        '''
        if len(p) == 2:
            p[0] = Node('unary_expression', [p[1]])
        elif len(p) == 3:
            if p[1] == '++' or p[1] == '--':
                p[0] = Node('unary_expression', [p[2]], leaf=f'pre{p[1]}')
            else:
                p[0] = Node('unary_expression', [p[1], p[2]])
        elif p[1] == 'sizeof' and len(p) == 3:
            p[0] = Node('unary_expression', [p[2]], leaf='sizeof')
        else:
            p[0] = Node('unary_expression', [p[3]], leaf='sizeof')
    
    def p_unary_operator(self, p):
        '''
        unary_operator : AND
                       | TIMES
                       | PLUS
                       | MINUS
                       | NOT
                       | LNOT
        '''
        p[0] = Node('unary_operator', leaf=p[1])
    
    def p_postfix_expression(self, p):
        '''
        postfix_expression : primary_expression
                           | postfix_expression LBRACKET expression RBRACKET
                           | postfix_expression LPAREN RPAREN
                           | postfix_expression LPAREN argument_expression_list RPAREN
                           | postfix_expression PERIOD ID
                           | postfix_expression ARROW ID
                           | postfix_expression PLUSPLUS
                           | postfix_expression MINUSMINUS
        '''
        if len(p) == 2:
            p[0] = Node('postfix_expression', [p[1]])
        elif len(p) == 5 and p[2] == '[':
            p[0] = Node('postfix_expression', [p[1], p[3]], leaf='array')
        elif len(p) == 4 and p[2] == '(':
            p[0] = Node('postfix_expression', [p[1]], leaf='function_call')
        elif len(p) == 5 and p[2] == '(':
            p[0] = Node('postfix_expression', [p[1], p[3]], leaf='function_call')
        elif len(p) == 4 and p[2] == '.':
            p[0] = Node('postfix_expression', [p[1], Node('id', leaf=p[3])], leaf='.')
        elif len(p) == 4 and p[2] == '->':
            p[0] = Node('postfix_expression', [p[1], Node('id', leaf=p[3])], leaf='->')
        else:
            p[0] = Node('postfix_expression', [p[1]], leaf=f'post{p[2]}')
    
    def p_primary_expression(self, p):
        '''
        primary_expression : ID
                           | constant
                           | STRING_LITERAL
                           | LPAREN expression RPAREN
        '''
        if p[1] == '(':
            p[0] = Node('primary_expression', [p[2]])
        elif isinstance(p[1], str) and p[1][0] == '"' and p[1][-1] == '"':
            p[0] = Node('primary_expression', [Node('string_literal', leaf=p[1])])
        elif isinstance(p[1], str):
            p[0] = Node('primary_expression', [Node('id', leaf=p[1])])
        else:
            p[0] = Node('primary_expression', [p[1]])
    
    def p_argument_expression_list(self, p):
        '''
        argument_expression_list : assignment_expression
                                 | argument_expression_list COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = Node('argument_expression_list', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]
    
    def p_constant(self, p):
        '''
        constant : INT_CONST
                 | CHAR_CONST
                 | FLOAT_CONST
        '''
        p[0] = Node('constant', leaf=p[1])
    
    # Error rule for syntax errors
    def p_error(self, p):
        """Error rule for syntax errors."""
        if p:
            error = {'line': p.lineno if hasattr(p, 'lineno') else '?', 
                    'position': p.lexpos if hasattr(p, 'lexpos') else '?',
                    'type': p.type if hasattr(p, 'type') else '?', 
                    'value': p.value if hasattr(p, 'value') else '?',
                    'message': f"Syntax error at '{p.value}' (token type: {p.type})"}
        else:
            error = {'line': '?', 'position': '?', 'type': '?', 'value': '?', 
                    'message': "Syntax error at EOF"}
        
        self.errors.append(error)
    
    def parse(self):
        """
        Parse the input and build the AST.
        Returns a dictionary with the AST and error information.
        """
        # Reset errors
        self.errors = []
        
        # Use the tokens list directly from the lexer
        tokens = self.lexer.tokens_list
        
        if not tokens:
            return {
                'success': False,
                'error': "No tokens to parse. Lexical analysis may have failed.",
                'errors': []
            }
        
        # Build a string from tokens for parsing
        input_str = ' '.join([t['value'] for t in tokens])
        self.lexer.lexer.input(input_str)
        
        # Parse
        try:
            self.ast = self.parser.parse(lexer=self.lexer.lexer)
            
            success = len(self.errors) == 0
            
            return {
                'success': success,
                'ast': format_ast_for_visualization(self.ast.to_dict() if self.ast else {}),
                'errors': self.errors,
                'raw_ast': self.ast.to_dict() if self.ast else {}
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'errors': self.errors
            }
