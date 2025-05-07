import re
import ply.lex as lex

class Lexer:
    """
    A lexical analyzer for C code.
    Uses PLY (Python Lex-Yacc) to perform lexical analysis.
    """
    
    # C reserved words
    reserved = {
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
        # C standard library functions
        'printf': 'PRINTF',
        'scanf': 'SCANF',
        'malloc': 'MALLOC',
        'free': 'FREE',
        'calloc': 'CALLOC',
        'realloc': 'REALLOC',
        'fopen': 'FOPEN',
        'fclose': 'FCLOSE',
        'fprintf': 'FPRINTF',
        'fscanf': 'FSCANF',
        'fread': 'FREAD',
        'fwrite': 'FWRITE',
        'gets': 'GETS',
        'puts': 'PUTS',
        'getchar': 'GETCHAR',
        'putchar': 'PUTCHAR',
        'strlen': 'STRLEN',
        'strcpy': 'STRCPY',
        'strcat': 'STRCAT',
        'strcmp': 'STRCMP',
        'memcpy': 'MEMCPY',
        'memset': 'MEMSET',
        'exit': 'EXIT',
        'print': 'PRINT',  # No es de C estándar, pero es común
        # C++ specific
        'class': 'CLASS',
        'new': 'NEW',
        'delete': 'DELETE',
        'this': 'THIS',
        'namespace': 'NAMESPACE',
        'using': 'USING',
        'try': 'TRY',
        'catch': 'CATCH',
        'throw': 'THROW',
        'public': 'PUBLIC',
        'private': 'PRIVATE',
        'protected': 'PROTECTED',
        'template': 'TEMPLATE',
        'virtual': 'VIRTUAL',
        'cout': 'COUT',
        'cin': 'CIN',
        'endl': 'ENDL',
    }
    
    # Token list
    tokens = [
        # Identifiers and reserved words
        'ID',
        
        # Constants
        'INTEGER', 'FLOAT_NUM', 'CHAR_CONST', 'STRING_LITERAL',
        
        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        
        # Assignment operators
        'EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL',
        'ANDEQUAL', 'OREQUAL', 'XOREQUAL', 'LSHIFTEQUAL', 'RSHIFTEQUAL',
        
        # Increment/decrement
        'PLUSPLUS', 'MINUSMINUS',
        
        # Delimiters
        'LPAREN', 'RPAREN',      # ( )
        'LBRACKET', 'RBRACKET',  # [ ]
        'LBRACE', 'RBRACE',      # { }
        'COMMA', 'PERIOD',       # , .
        'SEMI', 'COLON',         # ; :
        'ELLIPSIS',              # ...
        
        # Preprocessor
        'HASH',                  # #
        'PREPROCESSOR',          # #include etc.
    ] + list(reserved.values())
    
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
    
    t_EQUALS = r'='
    t_PLUSEQUAL = r'\+='
    t_MINUSEQUAL = r'-='
    t_TIMESEQUAL = r'\*='
    t_DIVEQUAL = r'/='
    t_MODEQUAL = r'%='
    t_ANDEQUAL = r'&='
    t_OREQUAL = r'\|='
    t_XOREQUAL = r'\^='
    t_LSHIFTEQUAL = r'<<='
    t_RSHIFTEQUAL = r'>>='
    
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'
    
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
    
    t_HASH = r'\#'
    
    # Ignored characters
    t_ignore = ' \t\f\v'
    
    def __init__(self, code):
        self.code = code
        self.lexer = None
        self.tokens_list = []
        self.errors = []
        
        # Build the lexer
        self.lexer = lex.lex(module=self)
    
    # Define a rule for preprocessor directives
    def t_PREPROCESSOR(self, t):
        r'\#\s*[a-zA-Z_][a-zA-Z0-9_]*(\s+<[^>]+>|\s+"[^"]+")?'
        return t
    
    # Define a rule for identifiers
    # Regla para identificar posibles identificadores mal formados que comienzan con números
    def t_INVALID_ID(self, t):
        r'[0-9]+[a-zA-Z_][a-zA-Z0-9_]*'
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Identificador mal formado): '{t.value}' en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^' * len(t.value)
        error_message += "\nSugerencia: Los identificadores deben comenzar con una letra o guion bajo, no con números"
        
        self.errors.append(error_message)
        # No retornamos el token, lo que hace que sea ignorado en el análisis posterior
        t.lexer.skip(len(t.value))
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Verificar si es una palabra reservada
        t.type = self.reserved.get(t.value, 'ID')
        
        # Si no es una palabra reservada, verificar si es similar a alguna palabra reservada
        if t.type == 'ID':
            # Comprobación para detectar palabras clave mal escritas (como "el" en lugar de "else")
            similar_keywords = self._check_similar_keywords(t.value)
            if similar_keywords:
                line_number = t.lineno
                position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
                line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
                
                error_message = f"Advertencia léxica: '{t.value}' podría ser una palabra clave mal escrita en línea {line_number}, posición {position_in_line}\n"
                error_message += f"Contexto: {line_content}\n"
                error_message += ' ' * position_in_line + '^' * len(t.value)
                error_message += f"\nSugerencia: ¿Quizás quiso decir {similar_keywords}?"
                
                self.errors.append(error_message)
        
        return t
        
    def _check_similar_keywords(self, word):
        """Verificar si una palabra es similar a alguna palabra clave de C."""
        # Lista de palabras clave comunes que podrían ser mal escritas
        common_keywords = {
            'el': 'else',
            'Els': 'else',
            'elese': 'else',
            'esle': 'else',
            'fi': 'if',
            'fro': 'for',
            'fore': 'for',
            'whiel': 'while',
            'wile': 'while',
            'whyle': 'while',
            'witch': 'switch',
            'swtich': 'switch',
            'swicth': 'switch',
            'casse': 'case',
            'brake': 'break',
            'brk': 'break',
            'retrn': 'return',
            'reutrn': 'return',
            'retur': 'return',
            'defualt': 'default',
            'defalt': 'default',
            'printF': 'printf',
            'pintf': 'printf',
            'scan': 'scanf',
            'scanF': 'scanf',
            'scnaf': 'scanf',
            'pnt': 'print',
            'prnit': 'print',
            'pinrt': 'print'
        }
        
        # Revisar si la palabra está en el diccionario de errores comunes
        if word in common_keywords:
            return f"'{common_keywords[word]}'"
        
        # Si no se encuentra en errores comunes, buscar similitud con otras palabras clave
        # Solo para palabras cortas (menos de 8 caracteres) para evitar falsos positivos
        if len(word) < 8:
            close_matches = []
            for keyword in self.reserved.keys():
                # Detectar palabras que difieren en máximo 2 caracteres
                if len(keyword) > 2 and abs(len(keyword) - len(word)) <= 2:
                    # Algoritmo simple de distancia de edición
                    similar = self._is_similar(word, keyword)
                    if similar:
                        close_matches.append(f"'{keyword}'")
            
            if close_matches:
                return " o ".join(close_matches[:2])  # Mostrar hasta 2 sugerencias
        
        return None
    
    def _is_similar(self, word1, word2):
        """
        Verificar si dos palabras son similares basándose en la distancia de Levenshtein.
        Retorna True si las palabras difieren en máximo 2 caracteres.
        """
        # Para palabras muy cortas, ser más estricto
        if len(word1) <= 3 or len(word2) <= 3:
            return word1 == word2
            
        if abs(len(word1) - len(word2)) > 2:
            return False
            
        # Implementación simple de distancia de edición
        distance = 0
        for i in range(min(len(word1), len(word2))):
            if word1[i] != word2[i]:
                distance += 1
                if distance > 2:  # Más de 2 diferencias
                    return False
        
        # Agregar diferencia de longitud
        distance += abs(len(word1) - len(word2))
        return distance <= 2
    
    # Regla para identificar literales numéricos incompletos (hexadecimales malformados)
    def t_INVALID_HEX(self, t):
        r'0[xX][^0-9a-fA-F]+'
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Literal numérico incorrecto): '{t.value}' en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^' * len(t.value)
        error_message += "\nSugerencia: Los números hexadecimales deben contener solo dígitos (0-9) y letras (A-F)"
        
        self.errors.append(error_message)
        t.lexer.skip(len(t.value))
    
    # Define a rule for integer constants
    def t_INTEGER(self, t):
        r'(0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*)[uUlL]*'
        return t
    
    # Regla para detectar literales de punto flotante malformados
    def t_INVALID_FLOAT(self, t):
        r'[0-9]+\.[a-zA-Z_]+|[0-9]+[eE][^0-9\-\+]+'
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Literal numérico incorrecto): '{t.value}' en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^' * len(t.value)
        error_message += "\nSugerencia: Formato incorrecto de número flotante. El exponente debe tener un valor numérico"
        
        self.errors.append(error_message)
        t.lexer.skip(len(t.value))
    
    # Define a rule for float constants
    def t_FLOAT_NUM(self, t):
        r'([0-9]*\.[0-9]+|[0-9]+\.)([eE][-+]?[0-9]+)?[fFlL]?|[0-9]+[eE][-+]?[0-9]+[fFlL]?'
        return t
    
    # Regla para detectar cadenas sin cerrar - debe ir ANTES de t_STRING_LITERAL
    def t_UNTERMINATED_STRING(self, t):
        r'"(\\.|[^\\"\n])*\n'
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Cadena mal formada): Cadena sin cerrar en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^'
        error_message += "\nSugerencia: Cierre la cadena con comillas dobles (\") antes del final de línea"
        
        self.errors.append(error_message)
        t.lexer.skip(len(t.value))
    
    # Define a rule for character constants
    def t_CHAR_CONST(self, t):
        r'\'(\\.|[^\\\'])\''
        return t
    
    # Regla para detectar caracteres sin cerrar
    def t_UNTERMINATED_CHAR(self, t):
        r"'(\\.|[^\\'])*\n"
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Carácter mal formado): Carácter sin cerrar en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^'
        error_message += "\nSugerencia: Cierre el carácter con comilla simple (') antes del final de línea"
        
        self.errors.append(error_message)
        t.lexer.skip(len(t.value))
    
    # Define a rule for string literals
    def t_STRING_LITERAL(self, t):
        r'"(\\.|[^\\"])*"'
        return t
    
    # Define a rule for line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    # Define a rule for comments
    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'
        t.lexer.lineno += t.value.count('\n')
        pass  # No return value. Token discarded
    
    # Define a rule for error handling
    def t_error(self, t):
        error_char = t.value[0]
        line_number = t.lineno
        
        # Obtener la línea completa para dar contexto
        try:
            lines = self.code.split('\n')
            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
            
            # Calcular la posición exacta del error en la línea
            position_in_line = t.lexpos - sum(len(l) + 1 for l in lines[:line_number - 1])
            position_marker = ' ' * position_in_line + '^'
            
            # Determinar sugerencias basadas en el carácter erróneo
            suggestion = ""
            # Identificar el tipo de error léxico
            error_type = "Carácter no reconocido"
            
            if error_char in "áéíóúÁÉÍÓÚ":
                suggestion = "Los caracteres acentuados no son válidos en identificadores en C"
                error_type = "Identificador mal formado"
            elif error_char in "!@#$%^&*()+-={}[]|\\:;\"'<>,.?/":
                suggestion = self._get_special_char_suggestion(error_char)
                # Verificar si podría ser parte de un literal numérico incorrecto
                prev_char = line_content[position_in_line-1] if position_in_line > 0 else ""
                if prev_char.isdigit() and error_char in "abcdefABCDEF":
                    error_type = "Literal numérico incorrecto"
                    suggestion = "Los números hexadecimales deben comenzar con '0x' o '0X'"
                elif prev_char.isdigit() and error_char in ".,":
                    error_type = "Literal numérico incorrecto"
                    suggestion = "Posible número decimal mal formado. Verifique la sintaxis de punto flotante"
            elif error_char in "¿¡ñÑ":
                suggestion = "Los caracteres especiales como '¿', '¡', 'ñ' no son válidos en C"
                error_type = "Identificador mal formado"
            elif ord(error_char) > 127:
                suggestion = "Los caracteres Unicode fuera del ASCII estándar no son válidos en C"
                error_type = "Identificador mal formado"
            elif error_char == '"' or error_char == "'":
                # Buscar si hay una comilla sin cerrar
                rest_of_line = line_content[position_in_line:]
                if error_char not in rest_of_line:
                    error_type = "Cadena mal formada"
                    suggestion = f"Falta cerrar la cadena con {error_char}"
            
            # Construir mensaje de error detallado
            error_message = f"Error léxico ({error_type}): '{error_char}' en línea {line_number}, posición {position_in_line}\n"
            error_message += f"Contexto: {line_content}\n{position_marker}"
            
            if suggestion:
                error_message += f"\nSugerencia: {suggestion}"
            
            self.errors.append(error_message)
        except Exception as e:
            # Fallback para casos excepcionales
            self.errors.append(f"Error léxico: Carácter ilegal '{error_char}' en línea {line_number}")
        
        t.lexer.skip(1)
        
    # Regla específica para detectar cadenas mal formadas (sin comilla de cierre)
    def t_error_string(self, t):
        r'"([^"\n])*$'
        line_number = t.lineno
        position_in_line = t.lexpos - sum(len(l) + 1 for l in self.code.split('\n')[:line_number - 1])
        
        error_message = f"Error léxico (Cadena mal formada): Falta comilla de cierre en línea {line_number}, posición {position_in_line}\n"
        line_content = self.code.split('\n')[line_number - 1] if line_number <= len(self.code.split('\n')) else ""
        error_message += f"Contexto: {line_content}\n"
        error_message += ' ' * position_in_line + '^'
        error_message += "\nSugerencia: Cierre la cadena con comillas (\")"
        
        self.errors.append(error_message)
        t.lexer.skip(len(t.value))
    
    def _get_special_char_suggestion(self, char):
        """Proporciona sugerencias específicas basadas en caracteres especiales problemáticos."""
        suggestions = {
            "@": "El carácter '@' no es válido en C. Si estás intentando multiplicar, usa '*'",
            "#": "El carácter '#' solo es válido en directivas de preprocesador al inicio de línea",
            "$": "El carácter '$' no es válido en C. Los identificadores deben comenzar con letra o '_'",
            "&": "Verifica si querías usar '&&' (AND lógico) o '&' (operador de dirección)",
            "\\": "El carácter '\\' solo es válido dentro de cadenas o caracteres como escape",
            "\"": "Comillas sin cerrar o mal escape de comillas en una cadena",
            "'": "Comilla simple sin cerrar o mal formateada",
            "?": "El operador ternario requiere formato: condicion ? expr1 : expr2",
        }
        return suggestions.get(char, "Verifica la sintaxis alrededor de este carácter")
    
    def tokenize(self):
        """
        Tokenize the input code.
        
        Returns:
            tuple: (tokens, errors) where tokens is a list of token dictionaries
                  and errors is a list of error messages.
        """
        self.lexer.input(self.code)
        tokens = []
        
        # Collect all tokens
        for tok in self.lexer:
            tokens.append({
                'type': tok.type,
                'value': tok.value,
                'line': tok.lineno,
                'position': tok.lexpos
            })
        
        return tokens, self.errors
    
    def get_token_at_position(self, position):
        """Get the token at a specific position in the code."""
        for token in self.tokens_list:
            if token['position'] <= position < token['position'] + len(str(token['value'])):
                return token
        return None
