import ply.yacc as yacc
import networkx as nx

class Parser:
    """
    A parser for C code.
    Uses PLY (Python Lex-Yacc) to perform syntax analysis.
    """
    
    # Patrones comunes para sugerencias de errores
    COMMON_MISTAKES = {
        'missing_parenthesis': (
            ['if', 'for', 'while', 'switch'], 
            "Falta paréntesis después de '{keyword}'. Formato correcto: {keyword}(condición)"
        ),
        'missing_brace': (
            ['if', 'for', 'while', 'switch', 'else'], 
            "Se esperaba una llave '{' después de '{keyword}'"
        ),
        'missing_semicolon': (
            ['return', '=', '+=', '-=', '*=', '/=', 'break', 'continue'],
            "Falta punto y coma (;) después de '{keyword}'"
        ),
        'unmatched_parentheses': ("()", "Los paréntesis no están balanceados correctamente"),
        'unknown_keyword': ("", "'{keyword}' no es una palabra clave reconocida del lenguaje C")
    }
    
    # Lista de funciones estándar de C y algunas comunes de extensiones
    KNOWN_FUNCTIONS = [
        # Funciones estándar de E/S
        'printf', 'scanf', 'getchar', 'putchar', 'puts', 'gets',
        'fprintf', 'fscanf', 'sprintf', 'sscanf', 'fgets', 'fputs',
        'fopen', 'fclose', 'fread', 'fwrite', 'fseek', 'ftell', 'rewind',
        'feof', 'ferror', 'clearerr', 'remove', 'rename',
        
        # Funciones de manejo de memoria
        'malloc', 'free', 'calloc', 'realloc',
        
        # Funciones de cadenas
        'strlen', 'strcpy', 'strncpy', 'strcat', 'strncat', 'strcmp', 'strncmp',
        'strchr', 'strrchr', 'strstr', 'strtok', 'memcpy', 'memmove', 'memcmp',
        'memchr', 'memset',
        
        # Funciones matemáticas
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sinh', 'cosh', 'tanh',
        'exp', 'log', 'log10', 'pow', 'sqrt', 'ceil', 'floor', 'fabs', 'ldexp',
        'frexp', 'modf', 'fmod',
        
        # Funciones de utilidad
        'rand', 'srand', 'time', 'clock', 'exit', 'abort', 'system',
        'getenv', 'bsearch', 'qsort', 'abs', 'labs', 'div', 'ldiv',
        
        # Otras funciones comunes
        'isalpha', 'isdigit', 'isalnum', 'isspace', 'islower', 'isupper',
        'tolower', 'toupper', 'atoi', 'atof', 'atol',
        
        # Funciones simplificadas para el entorno educativo
        'print', 'main'
    ]
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = {}
        self.errors = []
        self.code_lines = []  # Para almacenar líneas de código y dar mejor contexto
        
        # Extraer líneas del código original si hay tokens
        if tokens and len(tokens) > 0:
            max_line = max([t['line'] for t in tokens]) if tokens else 0
            self.code_lines = [''] * max_line
    
    def parse_variables(self):
        """
        Parse variables and constants from tokens.
        
        Returns:
            tuple: (ast, errors) where ast is a dictionary containing the abstract syntax tree
                  and errors is a list of error messages.
        """
        # Reset errors and AST
        self.errors = []
        self.ast = {
            'graph': nx.DiGraph(),
            'elements': []
        }
        
        # Validate token list
        if not self.tokens:
            self.errors.append("Error sintáctico: No hay tokens para analizar")
            return self.ast, self.errors
            
        # Verificar paréntesis y llaves balanceados primero
        brace_errors = self._check_balanced_braces(self.tokens)
        if brace_errors:
            self.errors.extend(brace_errors)
        
        paren_errors = self._check_balanced_parentheses(self.tokens)
        if paren_errors:
            self.errors.extend(paren_errors)
        
        # Verificar operadores y operandos
        operator_errors = self._check_operators_and_operands(self.tokens)
        if operator_errors:
            self.errors.extend(operator_errors)
        
        # Verificar puntos y coma faltantes
        semicolon_errors = self._check_missing_semicolons(self.tokens)
        if semicolon_errors:
            self.errors.extend(semicolon_errors)
            
        # Verificar funciones desconocidas
        unknown_function_errors = self._check_unknown_functions(self.tokens)
        if unknown_function_errors:
            self.errors.extend(unknown_function_errors)
        
        # Track current type and variables being declared
        current_type = None
        variables = []
        
        # Read through tokens to identify variable declarations
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Check for type specifiers
            if token['type'] in ['INT', 'CHAR', 'FLOAT', 'DOUBLE', 'VOID', 'LONG', 'SHORT', 
                                'UNSIGNED', 'SIGNED', 'CONST', 'VOLATILE']:
                current_type = token['value']
                i += 1
                
                # Process variable declarations following the type
                while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                    if self.tokens[i]['type'] == 'ID':
                        var_name = self.tokens[i]['value']
                        var_value = None
                        
                        # Check if variable is initialized
                        if i + 1 < len(self.tokens) and self.tokens[i + 1]['type'] == 'EQUALS':
                            i += 2  # Skip ID and EQUALS
                            
                            # Handle different types of initializers
                            if i < len(self.tokens):
                                if self.tokens[i]['type'] in ['INTEGER', 'FLOAT_NUM', 'CHAR_CONST', 'STRING_LITERAL']:
                                    var_value = self.tokens[i]['value']
                                    i += 1
                                else:
                                    # Complex initialization (e.g., expressions) - just record the presence
                                    var_value = "complex_init"
                                    # Skip until comma or semicolon
                                    while i < len(self.tokens) and self.tokens[i]['type'] not in ['COMMA', 'SEMI']:
                                        i += 1
                        
                        # Add variable to our list
                        variables.append({
                            'name': var_name,
                            'type': current_type,
                            'value': var_value,
                            'line': self.tokens[i - 1 if var_value else i]['line']
                        })
                        
                        # Add to AST elements
                        self.ast['elements'].append({
                            'type': 'Variable Declaration',
                            'value': f"{current_type} {var_name}" + (f" = {var_value}" if var_value else "")
                        })
                        
                        # Add to graph
                        self.ast['graph'].add_node(var_name, type='variable', data_type=current_type)
                        if var_value:
                            self.ast['graph'].add_node(str(var_value), type='value')
                            self.ast['graph'].add_edge(var_name, str(var_value), label='initialized_to')
                    
                    # Skip commas
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'COMMA':
                        i += 1
                    else:
                        i += 1
                
                # Skip the semicolon
                if i < len(self.tokens) and self.tokens[i]['type'] == 'SEMI':
                    i += 1
                else:
                    # Detectar la falta de punto y coma
                    last_var = variables[-1] if variables else None
                    if last_var:
                        line_num = last_var['line']
                        self.errors.append(f"Error sintáctico: Falta punto y coma (;) después de la declaración de variable '{last_var['name']}' en la línea {line_num}")
            else:
                i += 1
        
        return self.ast, self.errors
    
    def parse_expressions(self):
        """
        Parse arithmetic and logical expressions from tokens.
        
        Returns:
            tuple: (ast, errors) where ast is a dictionary containing the abstract syntax tree
                  and errors is a list of error messages.
        """
        # Reset errors and AST
        self.errors = []
        self.ast = {
            'graph': nx.DiGraph(),
            'elements': []
        }
        
        # Validate token list
        if not self.tokens:
            self.errors.append("Error sintáctico: No hay tokens para analizar expresiones")
            return self.ast, self.errors
        
        # Verificar paréntesis y llaves balanceados primero
        brace_errors = self._check_balanced_braces(self.tokens)
        if brace_errors:
            self.errors.extend(brace_errors)
        
        paren_errors = self._check_balanced_parentheses(self.tokens)
        if paren_errors:
            self.errors.extend(paren_errors)
        
        # Verificar expresiones incompletas y operadores sin operandos
        operator_errors = self._check_operators_and_operands(self.tokens)
        if operator_errors:
            self.errors.extend(operator_errors)
            
        # Verificar puntos y coma faltantes
        semicolon_errors = self._check_missing_semicolons(self.tokens)
        if semicolon_errors:
            self.errors.extend(semicolon_errors)
            
        # Verificar funciones desconocidas
        unknown_function_errors = self._check_unknown_functions(self.tokens)
        if unknown_function_errors:
            self.errors.extend(unknown_function_errors)
        
        # Process expressions
        i = 0
        while i < len(self.tokens):
            # Look for assignment or expressions
            if i + 2 < len(self.tokens) and self.tokens[i]['type'] == 'ID' and self.tokens[i+1]['type'] in [
                'EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL'
            ]:
                # Assignment expression found
                var_name = self.tokens[i]['value']
                operator = self.tokens[i+1]['value']
                
                # Find the end of the expression (semicolon)
                expr_tokens = []
                j = i + 2
                semicolon_found = False
                while j < len(self.tokens) and self.tokens[j]['type'] != 'SEMI':
                    expr_tokens.append(self.tokens[j])
                    j += 1
                
                # Verificar si se encontró el punto y coma
                if j < len(self.tokens) and self.tokens[j]['type'] == 'SEMI':
                    semicolon_found = True
                else:
                    line_num = self.tokens[i]['line']
                    line_content = self._get_line_content(line_num)
                    error_msg = f"Error sintáctico: Falta punto y coma (;) al final de la expresión en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n"
                    error_msg += f"Sugerencia: Agregue un punto y coma al final de la expresión"
                    self.errors.append(error_msg)
                
                # Add to AST elements
                expr_text = ' '.join([t['value'] for t in expr_tokens])
                self.ast['elements'].append({
                    'type': 'Assignment Expression',
                    'value': f"{var_name} {operator} {expr_text}"
                })
                
                # Add to graph
                self.ast['graph'].add_node(var_name, type='variable')
                expr_node = f"expr_{i}"
                self.ast['graph'].add_node(expr_node, type='expression', expr=expr_text)
                self.ast['graph'].add_edge(var_name, expr_node, label=operator)
                
                # Skip to after the semicolon or report error
                i = j + 1 if j < len(self.tokens) else j
                
                # Reportar error si no se encontró punto y coma
                if not semicolon_found:
                    line_num = self.tokens[j-1]['line'] if j > 0 and j-1 < len(self.tokens) else "desconocida"
                    self.errors.append(f"Error sintáctico: Falta punto y coma (;) después de la expresión '{var_name} {operator} {expr_text}' en la línea {line_num}")
            
            # Look for binary operations
            elif i + 2 < len(self.tokens) and self.tokens[i+1]['type'] in [
                'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
                'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
                'AND', 'OR', 'XOR', 'LAND', 'LOR'
            ]:
                left = self.tokens[i]['value']
                operator = self.tokens[i+1]['value']
                right = self.tokens[i+2]['value']
                
                # Add to AST elements
                self.ast['elements'].append({
                    'type': 'Binary Expression',
                    'value': f"{left} {operator} {right}"
                })
                
                # Add to graph
                expr_node = f"binexpr_{i}"
                self.ast['graph'].add_node(expr_node, type='binary_expr', operator=operator)
                self.ast['graph'].add_node(left, type='operand')
                self.ast['graph'].add_node(right, type='operand')
                self.ast['graph'].add_edge(expr_node, left, label='left')
                self.ast['graph'].add_edge(expr_node, right, label='right')
                
                i += 3
            
            # Look for unary operations
            elif i + 1 < len(self.tokens) and self.tokens[i]['type'] in ['PLUSPLUS', 'MINUSMINUS', 'NOT', 'LNOT']:
                operator = self.tokens[i]['value']
                operand = self.tokens[i+1]['value']
                
                # Add to AST elements
                self.ast['elements'].append({
                    'type': 'Unary Expression',
                    'value': f"{operator}{operand}"
                })
                
                # Add to graph
                expr_node = f"unexpr_{i}"
                self.ast['graph'].add_node(expr_node, type='unary_expr', operator=operator)
                self.ast['graph'].add_node(operand, type='operand')
                self.ast['graph'].add_edge(expr_node, operand, label='operand')
                
                i += 2
            else:
                i += 1
        
        return self.ast, self.errors
    
    def parse_control_structures(self):
        """
        Parse control structures (if, for, while, etc.) from tokens.
        
        Returns:
            tuple: (ast, errors) where ast is a dictionary containing the abstract syntax tree
                  and errors is a list of error messages.
        """
        # Reset errors and AST
        self.errors = []
        self.ast = {
            'graph': nx.DiGraph(),
            'elements': []
        }
        
        # Validate token list
        if not self.tokens:
            self.errors.append("Error sintáctico: No hay tokens para analizar estructuras de control")
            return self.ast, self.errors
        
        # Primero, verificamos la estructura global
        # Esto incluye verificar paréntesis y llaves balanceados
        brace_errors = self._check_balanced_braces(self.tokens)
        self.errors.extend(brace_errors)
        
        paren_errors = self._check_balanced_parentheses(self.tokens)
        self.errors.extend(paren_errors)
        
        # Verificar operadores y operandos
        operator_errors = self._check_operators_and_operands(self.tokens)
        self.errors.extend(operator_errors)
        
        # Verificar puntos y coma faltantes
        semicolon_errors = self._check_missing_semicolons(self.tokens)
        if semicolon_errors:
            self.errors.extend(semicolon_errors)
            
        # Verificar funciones desconocidas
        unknown_function_errors = self._check_unknown_functions(self.tokens)
        if unknown_function_errors:
            self.errors.extend(unknown_function_errors)
        
        # Definir la gramática para las estructuras de control
        # según el formato en los requisitos
        # estructura_control -> sentencia_if | sentencia_while | sentencia_for
        # sentencia_if -> 'if' '(' expresion ')' '{' bloque '}' ( 'else' '{' bloque '}' )?
        # sentencia_while -> 'while' '(' expresion ')' '{' bloque '}'
        # sentencia_for -> 'for' '(' inicializacion ';' expresion ';' actualizacion ')' '{' bloque '}'
        
        # Process control structures
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Check for if statements
            if token['type'] == 'IF':
                i += 1
                
                # Parse the condition (everything between parentheses)
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LPAREN':
                    i += 1
                    condition_tokens = []
                    paren_count = 1
                    
                    while i < len(self.tokens) and paren_count > 0:
                        if self.tokens[i]['type'] == 'LPAREN':
                            paren_count += 1
                        elif self.tokens[i]['type'] == 'RPAREN':
                            paren_count -= 1
                            if paren_count == 0:
                                break
                        
                        condition_tokens.append(self.tokens[i])
                        i += 1
                    
                    # Skip the closing parenthesis
                    i += 1
                    
                    condition_text = ' '.join([t['value'] for t in condition_tokens])
                    
                    # Add to AST elements
                    self.ast['elements'].append({
                        'type': 'If Statement',
                        'value': f"if ({condition_text})"
                    })
                    
                    # Add to graph
                    if_node = f"if_{i}"
                    self.ast['graph'].add_node(if_node, type='if_statement')
                    cond_node = f"cond_{i}"
                    self.ast['graph'].add_node(cond_node, type='condition', condition=condition_text)
                    self.ast['graph'].add_edge(if_node, cond_node, label='condition')
                    
                    # Parse the body
                    # Just track opening and closing braces for now
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                        i += 1
                        brace_count = 1
                        
                        body_node = f"body_{i}"
                        self.ast['graph'].add_node(body_node, type='if_body')
                        self.ast['graph'].add_edge(if_node, body_node, label='then')
                        
                        while i < len(self.tokens) and brace_count > 0:
                            if self.tokens[i]['type'] == 'LBRACE':
                                brace_count += 1
                            elif self.tokens[i]['type'] == 'RBRACE':
                                brace_count -= 1
                            
                            i += 1
                    else:
                        # Handle single statement (no braces)
                        while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                            i += 1
                        i += 1  # Skip semicolon
                    
                    # Check for else
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'ELSE':
                        i += 1
                        
                        # Add to AST elements
                        self.ast['elements'].append({
                            'type': 'Else Statement',
                            'value': "else"
                        })
                        
                        else_node = f"else_{i}"
                        self.ast['graph'].add_node(else_node, type='else_body')
                        self.ast['graph'].add_edge(if_node, else_node, label='else')
                        
                        # Parse the else body
                        if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                            i += 1
                            brace_count = 1
                            
                            while i < len(self.tokens) and brace_count > 0:
                                if self.tokens[i]['type'] == 'LBRACE':
                                    brace_count += 1
                                elif self.tokens[i]['type'] == 'RBRACE':
                                    brace_count -= 1
                                
                                i += 1
                        else:
                            # Handle single statement (no braces)
                            while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                                i += 1
                            i += 1  # Skip semicolon
                else:
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Condición inválida en la estructura 'if' en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: El formato correcto es 'if (condición) {{ ... }}'. Se esperaba un paréntesis '(' después de 'if'"
                    
                    self.errors.append(error_msg)
                    i += 1
            
            # Check for for loops
            elif token['type'] == 'FOR':
                i += 1
                
                # Parse the for loop components
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LPAREN':
                    i += 1
                    
                    # Parse initialization
                    init_tokens = []
                    while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                        init_tokens.append(self.tokens[i])
                        i += 1
                    i += 1  # Skip semicolon
                    
                    # Parse condition
                    cond_tokens = []
                    while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                        cond_tokens.append(self.tokens[i])
                        i += 1
                    i += 1  # Skip semicolon
                    
                    # Parse increment
                    incr_tokens = []
                    while i < len(self.tokens) and self.tokens[i]['type'] != 'RPAREN':
                        incr_tokens.append(self.tokens[i])
                        i += 1
                    i += 1  # Skip closing parenthesis
                    
                    init_text = ' '.join([t['value'] for t in init_tokens])
                    cond_text = ' '.join([t['value'] for t in cond_tokens])
                    incr_text = ' '.join([t['value'] for t in incr_tokens])
                    
                    # Add to AST elements
                    self.ast['elements'].append({
                        'type': 'For Loop',
                        'value': f"for ({init_text}; {cond_text}; {incr_text})"
                    })
                    
                    # Add to graph
                    for_node = f"for_{i}"
                    self.ast['graph'].add_node(for_node, type='for_loop')
                    
                    init_node = f"init_{i}"
                    self.ast['graph'].add_node(init_node, type='initialization', init=init_text)
                    self.ast['graph'].add_edge(for_node, init_node, label='init')
                    
                    cond_node = f"cond_{i}"
                    self.ast['graph'].add_node(cond_node, type='condition', condition=cond_text)
                    self.ast['graph'].add_edge(for_node, cond_node, label='condition')
                    
                    incr_node = f"incr_{i}"
                    self.ast['graph'].add_node(incr_node, type='increment', increment=incr_text)
                    self.ast['graph'].add_edge(for_node, incr_node, label='increment')
                    
                    # Parse the body
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                        i += 1
                        brace_count = 1
                        
                        body_node = f"body_{i}"
                        self.ast['graph'].add_node(body_node, type='for_body')
                        self.ast['graph'].add_edge(for_node, body_node, label='body')
                        
                        while i < len(self.tokens) and brace_count > 0:
                            if self.tokens[i]['type'] == 'LBRACE':
                                brace_count += 1
                            elif self.tokens[i]['type'] == 'RBRACE':
                                brace_count -= 1
                            
                            i += 1
                    else:
                        # Handle single statement (no braces)
                        while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                            i += 1
                        i += 1  # Skip semicolon
                else:
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Componente inválido en la estructura 'for' en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: El formato correcto es 'for (inicialización; condición; actualización) {{ ... }}'. Se esperaba un paréntesis '(' después de 'for'"
                    
                    self.errors.append(error_msg)
                    i += 1
            
            # Check for while loops
            elif token['type'] == 'WHILE':
                i += 1
                
                # Parse the condition
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LPAREN':
                    i += 1
                    condition_tokens = []
                    paren_count = 1
                    
                    while i < len(self.tokens) and paren_count > 0:
                        if self.tokens[i]['type'] == 'LPAREN':
                            paren_count += 1
                        elif self.tokens[i]['type'] == 'RPAREN':
                            paren_count -= 1
                            if paren_count == 0:
                                break
                        
                        condition_tokens.append(self.tokens[i])
                        i += 1
                    
                    # Skip the closing parenthesis
                    i += 1
                    
                    condition_text = ' '.join([t['value'] for t in condition_tokens])
                    
                    # Add to AST elements
                    self.ast['elements'].append({
                        'type': 'While Loop',
                        'value': f"while ({condition_text})"
                    })
                    
                    # Add to graph
                    while_node = f"while_{i}"
                    self.ast['graph'].add_node(while_node, type='while_loop')
                    
                    cond_node = f"cond_{i}"
                    self.ast['graph'].add_node(cond_node, type='condition', condition=condition_text)
                    self.ast['graph'].add_edge(while_node, cond_node, label='condition')
                    
                    # Parse the body
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                        i += 1
                        brace_count = 1
                        
                        body_node = f"body_{i}"
                        self.ast['graph'].add_node(body_node, type='while_body')
                        self.ast['graph'].add_edge(while_node, body_node, label='body')
                        
                        while i < len(self.tokens) and brace_count > 0:
                            if self.tokens[i]['type'] == 'LBRACE':
                                brace_count += 1
                            elif self.tokens[i]['type'] == 'RBRACE':
                                brace_count -= 1
                            
                            i += 1
                    else:
                        # Handle single statement (no braces)
                        while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                            i += 1
                        i += 1  # Skip semicolon
                else:
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Condición inválida en la estructura 'while' en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: El formato correcto es 'while (condición) {{ ... }}'. Se esperaba un paréntesis '(' después de 'while'"
                    
                    self.errors.append(error_msg)
                    i += 1
            
            # Check for do-while loops
            elif token['type'] == 'DO':
                i += 1
                
                # Add to AST elements
                self.ast['elements'].append({
                    'type': 'Do-While Loop',
                    'value': "do"
                })
                
                do_node = f"do_{i}"
                self.ast['graph'].add_node(do_node, type='do_while_loop')
                
                # Parse the body
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                    i += 1
                    brace_count = 1
                    
                    body_node = f"body_{i}"
                    self.ast['graph'].add_node(body_node, type='do_body')
                    self.ast['graph'].add_edge(do_node, body_node, label='body')
                    
                    while i < len(self.tokens) and brace_count > 0:
                        if self.tokens[i]['type'] == 'LBRACE':
                            brace_count += 1
                        elif self.tokens[i]['type'] == 'RBRACE':
                            brace_count -= 1
                        
                        i += 1
                else:
                    # Handle single statement (no braces)
                    while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                        i += 1
                    i += 1  # Skip semicolon
                
                # Check for while condition
                if i < len(self.tokens) and self.tokens[i]['type'] == 'WHILE':
                    i += 1
                    
                    # Parse the condition
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LPAREN':
                        i += 1
                        condition_tokens = []
                        paren_count = 1
                        
                        while i < len(self.tokens) and paren_count > 0:
                            if self.tokens[i]['type'] == 'LPAREN':
                                paren_count += 1
                            elif self.tokens[i]['type'] == 'RPAREN':
                                paren_count -= 1
                                if paren_count == 0:
                                    break
                            
                            condition_tokens.append(self.tokens[i])
                            i += 1
                        
                        # Skip the closing parenthesis
                        i += 1
                        
                        condition_text = ' '.join([t['value'] for t in condition_tokens])
                        
                        # Add to AST elements (update the do-while entry)
                        self.ast['elements'][-1]['value'] = f"do ... while ({condition_text})"
                        
                        # Add to graph
                        cond_node = f"cond_{i}"
                        self.ast['graph'].add_node(cond_node, type='condition', condition=condition_text)
                        self.ast['graph'].add_edge(do_node, cond_node, label='condition')
                        
                        # Skip the following semicolon
                        if i < len(self.tokens) and self.tokens[i]['type'] == 'SEMI':
                            i += 1
                    else:
                        line_num = token['line']
                        line_content = self._get_line_content(line_num)
                        position = self._get_token_position_in_line(token)
                        position_marker = ' ' * position + '^'
                        
                        error_msg = f"Error sintáctico: Se esperaba '(' después de 'while' en un bucle do-while en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El formato correcto es 'do {{ ... }} while (condición);'"
                        
                        self.errors.append(error_msg)
                        i += 1
                else:
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Se esperaba 'while' después del cuerpo de 'do' en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: El formato correcto es 'do {{ ... }} while (condición);'"
                    
                    self.errors.append(error_msg)
                    i += 1
            
            # Check for switch statements
            elif token['type'] == 'SWITCH':
                i += 1
                
                # Parse the switch expression
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LPAREN':
                    i += 1
                    expr_tokens = []
                    paren_count = 1
                    
                    while i < len(self.tokens) and paren_count > 0:
                        if self.tokens[i]['type'] == 'LPAREN':
                            paren_count += 1
                        elif self.tokens[i]['type'] == 'RPAREN':
                            paren_count -= 1
                            if paren_count == 0:
                                break
                        
                        expr_tokens.append(self.tokens[i])
                        i += 1
                    
                    # Skip the closing parenthesis
                    i += 1
                    
                    expr_text = ' '.join([t['value'] for t in expr_tokens])
                    
                    # Add to AST elements
                    self.ast['elements'].append({
                        'type': 'Switch Statement',
                        'value': f"switch ({expr_text})"
                    })
                    
                    # Add to graph
                    switch_node = f"switch_{i}"
                    self.ast['graph'].add_node(switch_node, type='switch_statement')
                    
                    expr_node = f"expr_{i}"
                    self.ast['graph'].add_node(expr_node, type='expression', expr=expr_text)
                    self.ast['graph'].add_edge(switch_node, expr_node, label='expression')
                    
                    # Parse the body with cases
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                        i += 1
                        
                        # Process cases
                        case_count = 0
                        while i < len(self.tokens) and self.tokens[i]['type'] != 'RBRACE':
                            if self.tokens[i]['type'] == 'CASE':
                                i += 1
                                
                                # Parse case value
                                case_value = self.tokens[i]['value'] if i < len(self.tokens) else "unknown"
                                i += 1
                                
                                # Skip colon
                                if i < len(self.tokens) and self.tokens[i]['type'] == 'COLON':
                                    i += 1
                                
                                # Add to AST elements
                                self.ast['elements'].append({
                                    'type': 'Case',
                                    'value': f"case {case_value}:"
                                })
                                
                                # Add to graph
                                case_node = f"case_{case_count}"
                                self.ast['graph'].add_node(case_node, type='case', value=case_value)
                                self.ast['graph'].add_edge(switch_node, case_node, label='case')
                                
                                case_count += 1
                            elif self.tokens[i]['type'] == 'DEFAULT':
                                i += 1
                                
                                # Skip colon
                                if i < len(self.tokens) and self.tokens[i]['type'] == 'COLON':
                                    i += 1
                                
                                # Add to AST elements
                                self.ast['elements'].append({
                                    'type': 'Default Case',
                                    'value': "default:"
                                })
                                
                                # Add to graph
                                default_node = f"default_{i}"
                                self.ast['graph'].add_node(default_node, type='default_case')
                                self.ast['graph'].add_edge(switch_node, default_node, label='default')
                            else:
                                i += 1
                        
                        # Skip closing brace
                        i += 1
                    else:
                        line_num = token['line']
                        line_content = self._get_line_content(line_num)
                        position = self._get_token_position_in_line(token)
                        position_marker = ' ' * position + '^'
                        
                        error_msg = f"Error sintáctico: Se esperaba '{{' después de la declaración switch en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El formato correcto es 'switch (expresión) {{ case valor: ... }}'"
                        
                        self.errors.append(error_msg)
                        i += 1
                else:
                        line_num = token['line']
                        line_content = self._get_line_content(line_num)
                        position = self._get_token_position_in_line(token)
                        position_marker = ' ' * position + '^'
                        
                        error_msg = f"Error sintáctico: Se esperaba '(' después de 'switch' en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El formato correcto es 'switch (expresión) {{ case valor: ... }}'"
                        
                        self.errors.append(error_msg)
                        i += 1
            
            # Continue with next token if not a control structure
            else:
                i += 1
        
        return self.ast, self.errors
    
    def _get_line_content(self, line_num):
        """Obtiene el contenido de una línea específica."""
        for token in self.tokens:
            if token['line'] == line_num:
                # Encuentra todos los tokens de esta línea
                line_tokens = [t for t in self.tokens if t['line'] == line_num]
                # Encuentra el token con la posición más temprana
                if line_tokens:
                    first_token = min(line_tokens, key=lambda t: t['position'])
                    last_token = max(line_tokens, key=lambda t: t['position'] + len(str(t['value'])))
                    
                    # Calcula la longitud total
                    start_pos = first_token['position']
                    end_pos = last_token['position'] + len(str(last_token['value']))
                    
                    # Intenta reconstruir la línea
                    reconstructed = ""
                    for t in sorted(line_tokens, key=lambda t: t['position']):
                        pos = t['position'] - start_pos
                        # Añade espacios si hay huecos
                        while len(reconstructed) < pos:
                            reconstructed += " "
                        reconstructed += str(t['value'])
                    
                    return reconstructed
        return ""
    
    def _get_token_position_in_line(self, token):
        """Calcula la posición exacta de un token dentro de su línea."""
        line_num = token['line']
        position = 0
        
        # Encuentra todos los tokens anteriores en la misma línea
        for t in self.tokens:
            if t['line'] == line_num and t['position'] < token['position']:
                position = max(position, t['position'])
        
        # La posición relativa dentro de la línea
        return token['position'] - position
    
    def _check_balanced_braces(self, tokens):
        """Verifica que las llaves estén balanceadas correctamente y proporciona mensajes detallados."""
        stack = []
        errors = []
        
        for token in tokens:
            if token['type'] == 'LBRACE':
                # Verificar el contexto previo para mejor diagnóstico
                prev_token_idx = tokens.index(token) - 1
                context = ""
                if prev_token_idx >= 0:
                    prev_token = tokens[prev_token_idx]
                    if prev_token['type'] in ['IF', 'ELSE', 'FOR', 'WHILE', 'SWITCH', 'FUNCTION']:
                        context = f" después de '{prev_token['value']}'"
                
                stack.append((token, '{', context))
            elif token['type'] == 'RBRACE':
                if not stack or stack[-1][1] != '{':
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Llave de cierre '}}' sin su correspondiente llave de apertura en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: Verifique que cada llave de cierre tenga su correspondiente llave de apertura"
                    
                    errors.append(error_msg)
                else:
                    # Verificar si hay código entre las llaves
                    opening_token, _, context = stack.pop()
                    if tokens.index(token) - tokens.index(opening_token) <= 1:
                        line_num = opening_token['line']
                        line_content = self._get_line_content(line_num)
                        position = self._get_token_position_in_line(opening_token)
                        position_marker = ' ' * position + '^'
                        
                        error_msg = f"Advertencia: Bloque vacío{context} en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: Este bloque no contiene código, lo que podría ser un error"
                        
                        # Añadimos como advertencia, no como error crítico
                        if context:  # Solo reportar si es un bloque de una estructura de control
                            errors.append(error_msg)
        
        # Comprueba si quedan llaves sin cerrar
        for token, brace, context in stack:
            line_num = token['line']
            line_content = self._get_line_content(line_num)
            position = self._get_token_position_in_line(token)
            position_marker = ' ' * position + '^'
            
            error_msg = f"Error sintáctico: Llave de apertura '{{' sin cerrar{context} en línea {line_num}\n"
            error_msg += f"Contexto: {line_content}\n{position_marker}\n"
            error_msg += f"Sugerencia: Cada llave de apertura debe tener su correspondiente llave de cierre"
            
            errors.append(error_msg)
        
        return errors
    
    def _check_missing_semicolons(self, tokens):
        """Verifica que todas las sentencias terminen con punto y coma."""
        errors = []
        
        # Lista de tokens que requieren punto y coma cuando aparecen en una sentencia
        requires_semicolon_tokens = [
            'EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL',  # Asignaciones
            'PRINTF', 'SCANF', 'PRINT', 'SCAN',  # Funciones de I/O
            'PLUSPLUS', 'MINUSMINUS',  # Incremento/decremento
            'RETURN',  # Sentencia return
        ]
        
        # Tokens que marcan inicio de estructuras que no necesitan punto y coma
        control_structure_tokens = [
            'IF', 'ELSE', 'FOR', 'WHILE', 'DO', 'SWITCH', 'CASE'
        ]
        
        # Tokens que indican tipos o modificadores
        type_tokens = [
            'INT', 'FLOAT', 'CHAR', 'DOUBLE', 'VOID', 'LONG', 'SHORT',
            'UNSIGNED', 'SIGNED', 'STATIC', 'CONST', 'EXTERN'
        ]
        
        # Primero, identifiquemos los tokens que encontramos en cada línea
        lines_tokens = {}
        
        for token in tokens:
            line = token['line']
            if line not in lines_tokens:
                lines_tokens[line] = []
            
            lines_tokens[line].append(token)
        
        # Ahora analizamos cada línea por separado
        for line_num, line_tokens in lines_tokens.items():
            # No verificamos líneas vacías o con un solo token
            if len(line_tokens) <= 1:
                continue
                
            # Verificar el último token de la línea
            last_token = line_tokens[-1]
            
            # Variables para determinar el tipo de línea
            has_function_call = False
            has_variable_decl = False
            has_assignment = False
            has_control_structure = False
            is_function_definition = False
            
            # Primero, detectar si parece ser una definición de función
            has_type_token = False
            has_id_paren = False
            idx_type = -1
            
            for i, token in enumerate(line_tokens):
                # Verificar si hay un tipo de dato (int, float, etc.)
                if token['type'] in type_tokens:
                    has_type_token = True
                    idx_type = i
                
                # Verificar si hay un ID seguido de paréntesis (función)
                if token['type'] == 'ID' and i < len(line_tokens) - 1 and line_tokens[i+1]['type'] == 'LPAREN':
                    has_id_paren = True
                    
                    # Si hay un tipo antes del ID y paréntesis, podría ser definición de función
                    if has_type_token and i > idx_type:
                        # Buscar una llave de apertura en las siguientes líneas
                        for next_line in range(line_num + 1, line_num + 4):  # Buscar hasta 3 líneas adelante
                            if next_line in lines_tokens:
                                for next_token in lines_tokens[next_line]:
                                    if next_token['type'] == 'LBRACE':
                                        is_function_definition = True
                                        break
                                        
                                if is_function_definition:
                                    break
            
            # Si es una definición de función, no necesita punto y coma
            if is_function_definition:
                continue
            
            # Verificar tokens específicos que indican necesidad de punto y coma
            for i, token in enumerate(line_tokens):
                # Estructura de control (no necesita punto y coma)
                if token['type'] in control_structure_tokens:
                    has_control_structure = True
                    break
                
                # Llamada a función como printf, scanf, etc.
                if token['type'] in ['PRINTF', 'SCANF', 'PRINT', 'SCAN', 'FPRINTF', 'FSCANF', 'PUTS', 'GETS']:
                    has_function_call = True
                
                # Cualquier identificador seguido de paréntesis puede ser una llamada a función
                if token['type'] == 'ID' and i < len(line_tokens) - 1 and line_tokens[i+1]['type'] == 'LPAREN':
                    # Distinguir entre declaración de función y llamada a función
                    # Si no hay tipo antes del ID, es una llamada a función
                    if not any(lt['type'] in type_tokens for lt in line_tokens[:i]):
                        has_function_call = True
                
                # Asignaciones
                if token['type'] in ['EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL']:
                    has_assignment = True
                
                # Declaración de variable (tiene tipo pero no es función)
                if token['type'] in type_tokens:
                    # Verificar si la declaración NO es de función
                    is_variable_decl = True
                    
                    # Buscar paréntesis que indicarían que es una función
                    for j in range(i+1, len(line_tokens)):
                        if line_tokens[j]['type'] == 'LPAREN':
                            is_variable_decl = False
                            break
                    
                    if is_variable_decl:
                        has_variable_decl = True
            
            # Verificar si necesita punto y coma pero no lo tiene
            needs_semicolon = (has_function_call or has_assignment or has_variable_decl or 
                              (last_token['type'] == 'RETURN'))
            
            if needs_semicolon and not has_control_structure and last_token['type'] != 'SEMI':
                # Y no hay continuación de expresión en la línea siguiente
                next_line_continues = False
                if line_num + 1 in lines_tokens:
                    next_tokens = lines_tokens[line_num + 1]
                    if next_tokens and next_tokens[0]['type'] in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO']:
                        next_line_continues = True
                
                if not next_line_continues:
                    position = self._get_token_position_in_line(last_token) + len(last_token['value'])
                    line_content = self._get_line_content(line_num)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Falta punto y coma (;) al final de la línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: Agregue un punto y coma al final de la sentencia"
                    
                    errors.append(error_msg)
        
        return errors
    
    def _check_operators_and_operands(self, tokens):
        """Verifica que los operadores tengan sus operandos correspondientes."""
        errors = []
        
        # Listas de tipos de token para clasificación
        arithmetic_operators = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO']
        comparison_operators = ['LT', 'LE', 'GT', 'GE', 'EQ', 'NE']
        logical_operators = ['LAND', 'LOR', 'AND', 'OR', 'XOR']
        assignment_operators = ['EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL']
        all_operators = arithmetic_operators + comparison_operators + logical_operators + assignment_operators
        
        # Tipos de token que pueden ser operandos válidos
        valid_operands = ['ID', 'INTEGER', 'FLOAT_NUM', 'CHAR_CONST', 'STRING_LITERAL']
        
        for i, token in enumerate(tokens):
            # Verificar operadores
            if token['type'] in all_operators:
                # Verificar que hay un operando a la izquierda
                has_left_operand = False
                if i > 0 and (tokens[i-1]['type'] in valid_operands or tokens[i-1]['type'] == 'RPAREN'):
                    has_left_operand = True
                
                # Verificar que hay un operando a la derecha
                has_right_operand = False
                if i < len(tokens) - 1 and (tokens[i+1]['type'] in valid_operands or tokens[i+1]['type'] == 'LPAREN'):
                    has_right_operand = True
                
                # Reportar error si falta un operando
                if not has_left_operand or not has_right_operand:
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_type = ""
                    if token['type'] in arithmetic_operators:
                        error_type = "aritmético"
                    elif token['type'] in comparison_operators:
                        error_type = "de comparación"
                    elif token['type'] in logical_operators:
                        error_type = "lógico"
                    else:
                        error_type = "de asignación"
                    
                    error_msg = f"Error sintáctico: Operador {error_type} '{token['value']}' "
                    
                    if not has_left_operand and not has_right_operand:
                        error_msg += f"sin operandos en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El operador '{token['value']}' requiere operandos a la izquierda y derecha"
                    elif not has_left_operand:
                        error_msg += f"sin operando izquierdo en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El operador '{token['value']}' requiere un operando a la izquierda"
                    else:  # not has_right_operand
                        error_msg += f"sin operando derecho en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: El operador '{token['value']}' requiere un operando a la derecha"
                    
                    errors.append(error_msg)
                
                # Verificar operadores secuenciales (como x + * y)
                if i > 0 and i < len(tokens) - 1:
                    if tokens[i-1]['type'] in all_operators or tokens[i+1]['type'] in all_operators:
                        line_num = token['line']
                        line_content = self._get_line_content(line_num)
                        position = self._get_token_position_in_line(token)
                        position_marker = ' ' * position + '^'
                        
                        error_msg = f"Error sintáctico: Operadores secuenciales sin operandos intermedios en línea {line_num}\n"
                        error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                        error_msg += f"Sugerencia: No se pueden usar operadores secuencialmente sin operandos intermedios"
                        
                        errors.append(error_msg)
        
        return errors
        
    def _check_balanced_parentheses(self, tokens):
        """Verifica que los paréntesis estén balanceados correctamente y proporciona mensajes detallados."""
        stack = []
        errors = []
        
        for token in tokens:
            if token['type'] == 'LPAREN':
                # Verificar el contexto previo para mejor diagnóstico
                prev_token_idx = tokens.index(token) - 1
                context = ""
                if prev_token_idx >= 0:
                    prev_token = tokens[prev_token_idx]
                    if prev_token['type'] in ['IF', 'FOR', 'WHILE', 'SWITCH']:
                        context = f" en la estructura '{prev_token['value']}'"
                
                stack.append((token, '(', context))
            elif token['type'] == 'RPAREN':
                if not stack or stack[-1][1] != '(':
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^'
                    
                    error_msg = f"Error sintáctico: Paréntesis de cierre ')' sin su correspondiente paréntesis de apertura en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    error_msg += f"Sugerencia: Los paréntesis están desbalanceados. Verifique que cada paréntesis de cierre tenga su correspondiente paréntesis de apertura"
                    
                    errors.append(error_msg)
                else:
                    # Verificar si hay contenido entre los paréntesis
                    opening_token, _, context = stack.pop()
                    if tokens.index(token) - tokens.index(opening_token) <= 1:
                        # Paréntesis vacíos - solo advertir si están en una estructura de control
                        if context:
                            line_num = opening_token['line']
                            line_content = self._get_line_content(line_num)
                            position = self._get_token_position_in_line(opening_token)
                            position_marker = ' ' * position + '^'
                            
                            error_msg = f"Advertencia: Condición vacía{context} en línea {line_num}\n"
                            error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                            error_msg += f"Sugerencia: Esta estructura de control tiene una condición vacía, lo que podría ser un error"
                            
                            errors.append(error_msg)
                    else:
                        # Verificar contenido desbalanceado dentro de paréntesis
                        # (5 + )
                        opening_idx = tokens.index(opening_token)
                        closing_idx = tokens.index(token)
                        content_tokens = tokens[opening_idx+1:closing_idx]
                        
                        if content_tokens:
                            last_token = content_tokens[-1]
                            if last_token['type'] in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE']:
                                line_num = last_token['line']
                                line_content = self._get_line_content(line_num)
                                position = self._get_token_position_in_line(last_token)
                                position_marker = ' ' * position + '^'
                                
                                error_msg = f"Error sintáctico: Operador '{last_token['value']}' sin operando derecho dentro de paréntesis en línea {line_num}\n"
                                error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                                error_msg += f"Sugerencia: El operador '{last_token['value']}' requiere un operando a la derecha"
                                
                                errors.append(error_msg)
        
        # Comprueba si quedan paréntesis sin cerrar
        for token, parenthesis, context in stack:
            line_num = token['line']
            line_content = self._get_line_content(line_num)
            position = self._get_token_position_in_line(token)
            position_marker = ' ' * position + '^'
            
            error_msg = f"Error sintáctico: Paréntesis de apertura '(' sin cerrar{context} en línea {line_num}\n"
            error_msg += f"Contexto: {line_content}\n{position_marker}\n"
            error_msg += f"Sugerencia: Los paréntesis están desbalanceados. Agregue un paréntesis de cierre ')'"
            
            errors.append(error_msg)
        
        return errors
        
    def _check_unknown_functions(self, tokens):
        """Verifica si se están usando funciones que no están definidas en C."""
        errors = []
        
        # Buscar patrones de llamada a función: ID seguido de paréntesis
        for i, token in enumerate(tokens):
            if token['type'] == 'ID' and i + 1 < len(tokens) and tokens[i+1]['type'] == 'LPAREN':
                function_name = token['value']
                
                # Verificar si la función es conocida
                if function_name.lower() not in [f.lower() for f in self.KNOWN_FUNCTIONS]:
                    # No está en la lista de funciones estándar
                    line_num = token['line']
                    line_content = self._get_line_content(line_num)
                    position = self._get_token_position_in_line(token)
                    position_marker = ' ' * position + '^' * len(function_name)
                    
                    # Buscar funciones similares para sugerir
                    suggestions = []
                    for known_func in self.KNOWN_FUNCTIONS:
                        # Funciones similares (considerando diferencia de máximo 2 caracteres)
                        if abs(len(known_func) - len(function_name)) <= 2:
                            # Algoritmo simple de distancia de edición
                            distance = 0
                            for j in range(min(len(known_func), len(function_name))):
                                if j < len(known_func) and j < len(function_name) and known_func[j].lower() != function_name[j].lower():
                                    distance += 1
                            
                            distance += abs(len(known_func) - len(function_name))
                            if distance <= 2:
                                suggestions.append(known_func)
                    
                    error_msg = f"Error semántico: La función '{function_name}' no está definida en C estándar en línea {line_num}\n"
                    error_msg += f"Contexto: {line_content}\n{position_marker}\n"
                    
                    if suggestions:
                        error_msg += f"Sugerencia: ¿Quizás quiso decir {', '.join(suggestions[:2])}?"
                    else:
                        error_msg += "Sugerencia: Verifique que la función esté declarada o incluya la biblioteca correspondiente"
                    
                    errors.append(error_msg)
        
        return errors
        
    def parse_methods_classes(self):
        """
        Parse methods and classes from tokens.
        
        Returns:
            tuple: (ast, errors) where ast is a dictionary containing the abstract syntax tree
                  and errors is a list of error messages.
        """
        # Reset errors and AST
        self.errors = []
        self.ast = {
            'graph': nx.DiGraph(),
            'elements': []
        }
        
        # Process methods and classes
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Check for method declarations
            if i + 2 < len(self.tokens) and token['type'] in ['INT', 'CHAR', 'FLOAT', 'DOUBLE', 'VOID', 'LONG', 'SHORT'] and \
               self.tokens[i+1]['type'] == 'ID' and self.tokens[i+2]['type'] == 'LPAREN':
                
                return_type = token['value']
                method_name = self.tokens[i+1]['value']
                i += 3  # Skip return type, name, and opening parenthesis
                
                # Parse parameters
                params = []
                param_tokens = []
                
                # Handle empty parameter list
                if i < len(self.tokens) and self.tokens[i]['type'] == 'RPAREN':
                    i += 1
                else:
                    # Parse parameters
                    param_type = None
                    param_name = None
                    
                    while i < len(self.tokens) and self.tokens[i]['type'] != 'RPAREN':
                        if self.tokens[i]['type'] in ['INT', 'CHAR', 'FLOAT', 'DOUBLE', 'VOID', 'LONG', 'SHORT']:
                            param_type = self.tokens[i]['value']
                            i += 1
                        elif self.tokens[i]['type'] == 'ID':
                            param_name = self.tokens[i]['value']
                            params.append({'type': param_type, 'name': param_name})
                            param_tokens.append(f"{param_type} {param_name}")
                            i += 1
                        elif self.tokens[i]['type'] == 'COMMA':
                            i += 1
                        else:
                            i += 1
                    
                    # Skip closing parenthesis
                    i += 1
                
                # Add to AST elements
                param_list = ', '.join(param_tokens)
                self.ast['elements'].append({
                    'type': 'Method Declaration',
                    'value': f"{return_type} {method_name}({param_list})"
                })
                
                # Add to graph
                method_node = method_name
                self.ast['graph'].add_node(method_node, type='method', return_type=return_type)
                
                for j, param in enumerate(params):
                    param_node = f"{method_name}_param_{j}"
                    self.ast['graph'].add_node(param_node, type='parameter', param_type=param['type'], param_name=param['name'])
                    self.ast['graph'].add_edge(method_node, param_node, label='parameter')
                
                # Parse method body
                if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                    body_node = f"{method_name}_body"
                    self.ast['graph'].add_node(body_node, type='method_body')
                    self.ast['graph'].add_edge(method_node, body_node, label='body')
                    
                    i += 1
                    brace_count = 1
                    
                    while i < len(self.tokens) and brace_count > 0:
                        if self.tokens[i]['type'] == 'LBRACE':
                            brace_count += 1
                        elif self.tokens[i]['type'] == 'RBRACE':
                            brace_count -= 1
                        
                        i += 1
            
            # Check for class declarations
            elif token['type'] == 'CLASS':
                i += 1
                
                # Get class name
                if i < len(self.tokens) and self.tokens[i]['type'] == 'ID':
                    class_name = self.tokens[i]['value']
                    i += 1
                    
                    # Add to AST elements
                    self.ast['elements'].append({
                        'type': 'Class Declaration',
                        'value': f"class {class_name}"
                    })
                    
                    # Add to graph
                    class_node = class_name
                    self.ast['graph'].add_node(class_node, type='class')
                    
                    # Handle inheritance
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'COLON':
                        i += 1
                        
                        # Parse parent classes
                        while i < len(self.tokens) and self.tokens[i]['type'] != 'LBRACE':
                            if self.tokens[i]['type'] == 'ID':
                                parent_class = self.tokens[i]['value']
                                self.ast['graph'].add_node(parent_class, type='class')
                                self.ast['graph'].add_edge(class_node, parent_class, label='inherits')
                            
                            i += 1
                    
                    # Parse class body
                    if i < len(self.tokens) and self.tokens[i]['type'] == 'LBRACE':
                        i += 1
                        brace_count = 1
                        
                        # We'll parse methods and attributes inside the class
                        while i < len(self.tokens) and brace_count > 0:
                            # Check for class attributes
                            if i + 1 < len(self.tokens) and \
                               self.tokens[i]['type'] in ['INT', 'CHAR', 'FLOAT', 'DOUBLE', 'VOID', 'LONG', 'SHORT'] and \
                               self.tokens[i+1]['type'] == 'ID':
                                
                                attr_type = self.tokens[i]['value']
                                attr_name = self.tokens[i+1]['value']
                                
                                # Add to AST elements
                                self.ast['elements'].append({
                                    'type': 'Class Attribute',
                                    'value': f"{attr_type} {attr_name}"
                                })
                                
                                # Add to graph
                                attr_node = f"{class_name}_{attr_name}"
                                self.ast['graph'].add_node(attr_node, type='attribute', attr_type=attr_type, attr_name=attr_name)
                                self.ast['graph'].add_edge(class_node, attr_node, label='attribute')
                                
                                # Skip to semicolon
                                while i < len(self.tokens) and self.tokens[i]['type'] != 'SEMI':
                                    i += 1
                                i += 1  # Skip semicolon
                            
                            # Track braces for nested scopes
                            if i < len(self.tokens):
                                if self.tokens[i]['type'] == 'LBRACE':
                                    brace_count += 1
                                elif self.tokens[i]['type'] == 'RBRACE':
                                    brace_count -= 1
                                
                                i += 1
                    else:
                        self.errors.append(f"Expected '{{' after class name at line {token['line']}")
                        i += 1
                else:
                    self.errors.append(f"Expected class name after 'class' keyword at line {token['line']}")
                    i += 1
            else:
                i += 1
        
        return self.ast, self.errors
