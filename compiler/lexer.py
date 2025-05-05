import re
import ply.lex as lex
from .utils import format_tokens_for_visualization

class Lexer:
    """
    Lexical analyzer for C code. Converts C source code into tokens.
    """
    
    # List of token names
    tokens = (
        # Keywords
        'AUTO', 'BREAK', 'CASE', 'CHAR', 'CONST', 'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE',
        'ELSE', 'ENUM', 'EXTERN', 'FLOAT', 'FOR', 'GOTO', 'IF', 'INT', 'LONG',
        'REGISTER', 'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'STATIC', 'STRUCT',
        'SWITCH', 'TYPEDEF', 'UNION', 'UNSIGNED', 'VOID', 'VOLATILE', 'WHILE',
        
        # Identifiers
        'ID',
        
        # Constants
        'INT_CONST', 'FLOAT_CONST', 'CHAR_CONST', 'STRING_LITERAL',
        
        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        
        # Assignment operators
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL', 'RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',
        
        # Increment/decrement
        'PLUSPLUS', 'MINUSMINUS',
        
        # Structure dereference
        'ARROW',
        
        # Ternary operator
        'CONDOP',
        
        # Delimiters
        'LPAREN', 'RPAREN',         # ( )
        'LBRACKET', 'RBRACKET',     # [ ]
        'LBRACE', 'RBRACE',         # { }
        'COMMA', 'PERIOD',          # , .
        'SEMI', 'COLON',            # ; :
        
        # Ellipsis (for variadic functions)
        'ELLIPSIS',
    )
    
    # Keywords
    keywords = {
        'auto': 'AUTO',
        'break': 'BREAK',
        'case': 'CASE',
        'char': 'CHAR',
        'const': 'CONST',
        'continue': 'CONTINUE',
        'default': 'DEFAULT',
        'do': 'DO',
        'double': 'DOUBLE',
        'else': 'ELSE',
        'enum': 'ENUM',
        'extern': 'EXTERN',
        'float': 'FLOAT',
        'for': 'FOR',
        'goto': 'GOTO',
        'if': 'IF',
        'int': 'INT',
        'long': 'LONG',
        'register': 'REGISTER',
        'return': 'RETURN',
        'short': 'SHORT',
        'signed': 'SIGNED',
        'sizeof': 'SIZEOF',
        'static': 'STATIC',
        'struct': 'STRUCT',
        'switch': 'SWITCH',
        'typedef': 'TYPEDEF',
        'union': 'UNION',
        'unsigned': 'UNSIGNED',
        'void': 'VOID',
        'volatile': 'VOLATILE',
        'while': 'WHILE',
    }
    
    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_OR = r'\|'
    t_AND = r'&'
    t_NOT = r'~'
    t_XOR = r'\^'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'
    t_LOR = r'\|\|'
    t_LAND = r'&&'
    t_LNOT = r'!'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='
    
    # Assignment operators
    t_EQUALS = r'='
    t_TIMESEQUAL = r'\*='
    t_DIVEQUAL = r'/='
    t_MODEQUAL = r'%='
    t_PLUSEQUAL = r'\+='
    t_MINUSEQUAL = r'-='
    t_LSHIFTEQUAL = r'<<='
    t_RSHIFTEQUAL = r'>>='
    t_ANDEQUAL = r'&='
    t_XOREQUAL = r'\^='
    t_OREQUAL = r'\|='
    
    # Increment/decrement
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'
    
    # Structure dereference
    t_ARROW = r'->'
    
    # Ternary operator
    t_CONDOP = r'\?'
    
    # Delimiters
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_SEMI = r';'
    t_COLON = r':'
    t_ELLIPSIS = r'\.\.\.'
    
    # Ignore spaces and tabs
    t_ignore = ' \t'
    
    def __init__(self, data=None):
        """Initialize the lexer with input data."""
        self.lexer = None
        self.data = data or ""
        self.tokens_list = []
        self.error_list = []
        
        # Build the lexer
        self.lexer = lex.lex(module=self)
        if data:
            self.lexer.input(data)
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_COMMENT(self, t):
        r'/\*(.|\n)*?\*/|//.*'
        # Ignore comments
        t.lexer.lineno += t.value.count('\n')
    
    def t_FLOAT_CONST(self, t):
        r'(\d+\.\d*|\.\d+)([eE][-+]?\d+)?[fFlL]?|\d+[eE][-+]?\d+[fFlL]?'
        return t
    
    def t_INT_CONST(self, t):
        r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        return t
    
    def t_CHAR_CONST(self, t):
        r"'(\\.|[^\\'])'"
        return t
    
    def t_STRING_LITERAL(self, t):
        r'"(\\.|[^\\"])*"'
        return t
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Check if ID is a keyword
        t.type = self.keywords.get(t.value, 'ID')
        return t
    
    def t_error(self, t):
        """Error handling rule."""
        error_msg = f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}"
        self.error_list.append({
            'line': t.lexer.lineno,
            'pos': t.lexpos,
            'value': t.value[0],
            'message': error_msg
        })
        t.lexer.skip(1)
    
    def tokenize(self):
        """
        Tokenize the input data and return the results.
        Returns a dictionary with tokens and error information.
        """
        # Reset lists
        self.tokens_list = []
        self.error_list = []
        
        # Tokenize
        self.lexer.input(self.data)
        for tok in self.lexer:
            self.tokens_list.append({
                'type': tok.type,
                'value': tok.value,
                'line': tok.lineno,
                'position': tok.lexpos
            })
        
        success = len(self.error_list) == 0
        
        return {
            'success': success,
            'tokens': format_tokens_for_visualization(self.tokens_list),
            'errors': self.error_list,
            'raw_tokens': self.tokens_list
        }
