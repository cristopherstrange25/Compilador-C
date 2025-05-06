import pandas as pd

class SemanticAnalyzer:
    """
    A semantic analyzer for C code.
    Performs various semantic checks including type checking and symbol table management.
    """
    
    # Tablas de compatibilidad de tipos para operaciones comunes
    TYPE_COMPATIBILITY = {
        'arithmetic': {
            'int': ['int', 'float', 'double', 'char'],
            'float': ['int', 'float', 'double'],
            'double': ['int', 'float', 'double'],
            'char': ['int', 'char']
        },
        'logical': {
            'int': ['int', 'char'],
            'char': ['int', 'char'],
            'bool': ['int', 'char', 'bool']
        },
        'assignment': {
            'int': ['int', 'char'],
            'float': ['int', 'float'],
            'double': ['int', 'float', 'double'],
            'char': ['char'],
            'bool': ['int', 'char', 'bool']
        }
    }
    
    # Errores comunes con mensajes específicos
    COMMON_ERRORS = {
        'undeclared_variable': "Error semántico: Variable '{var}' usada pero no declarada",
        'redeclared_variable': "Error semántico: Variable '{var}' ya declarada en este ámbito en línea {line}",
        'type_mismatch': "Error semántico: Incompatibilidad de tipos en {context}. '{expected}' no puede operar con '{actual}'",
        'uninitialized_variable': "Error semántico: Variable '{var}' usada antes de ser inicializada",
        'function_call_mismatch': "Error semántico: Llamada a función '{func}' con {actual} argumentos, pero se esperaban {expected}"
    }
    
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = []
        self.errors = []
        self.error_context = {}  # Para almacenar información de contexto de errores
    
    def analyze_symbols(self):
        """
        Analyzes the AST to build a symbol table.
        
        Returns:
            tuple: (result, symbol_table, errors) where result is a dictionary of analysis results,
                  symbol_table is a list of symbol dictionaries, and errors is a list of error messages.
        """
        # Reset symbol table and errors
        self.symbol_table = []
        self.errors = []
        
        # Extract from the AST graph
        graph = self.ast.get('graph', None)
        elements = self.ast.get('elements', [])
        
        if not graph:
            self.errors.append("No AST graph available for symbol table analysis")
            return {}, [], self.errors
        
        # Process graph nodes to build symbol table
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'variable':
                # Process variables
                self.symbol_table.append({
                    'name': node,
                    'kind': 'variable',
                    'data_type': data.get('data_type', 'unknown'),
                    'scope': 'global',  # Default scope, will be refined later
                    'initialized': self._is_initialized(graph, node)
                })
            elif data.get('type') == 'method':
                # Process methods
                self.symbol_table.append({
                    'name': node,
                    'kind': 'function',
                    'data_type': data.get('return_type', 'unknown'),
                    'scope': 'global',
                    'parameters': self._get_parameters(graph, node)
                })
            elif data.get('type') == 'parameter':
                # Process parameters
                self.symbol_table.append({
                    'name': data.get('param_name', 'unknown'),
                    'kind': 'parameter',
                    'data_type': data.get('param_type', 'unknown'),
                    'scope': 'parameter'
                })
            elif data.get('type') == 'class':
                # Process classes
                self.symbol_table.append({
                    'name': node,
                    'kind': 'class',
                    'data_type': 'class',
                    'scope': 'global',
                    'attributes': self._get_class_attributes(graph, node)
                })
            elif data.get('type') == 'attribute':
                # Process class attributes
                self.symbol_table.append({
                    'name': data.get('attr_name', 'unknown'),
                    'kind': 'attribute',
                    'data_type': data.get('attr_type', 'unknown'),
                    'scope': 'class:' + node.split('_')[0]  # Extract class name from attribute node
                })
        
        # Check for duplicate symbols
        self._check_duplicate_symbols()
        
        # Perform scope analysis (simplified version)
        self._analyze_scopes()
        
        return {'symbol_count': len(self.symbol_table)}, self.symbol_table, self.errors
    
    def _is_initialized(self, graph, node):
        """Check if a variable is initialized by looking at its edges."""
        for _, target, data in graph.out_edges(node, data=True):
            if data.get('label') == 'initialized_to':
                return True
        return False
    
    def _get_parameters(self, graph, method_node):
        """Get list of parameters for a method."""
        params = []
        for _, target, data in graph.out_edges(method_node, data=True):
            if data.get('label') == 'parameter':
                param_data = graph.nodes[target]
                params.append({
                    'name': param_data.get('param_name', 'unknown'),
                    'type': param_data.get('param_type', 'unknown')
                })
        return params
    
    def _get_class_attributes(self, graph, class_node):
        """Get list of attributes for a class."""
        attributes = []
        for _, target, data in graph.out_edges(class_node, data=True):
            if data.get('label') == 'attribute':
                attr_data = graph.nodes[target]
                attributes.append({
                    'name': attr_data.get('attr_name', 'unknown'),
                    'type': attr_data.get('attr_type', 'unknown')
                })
        return attributes
    
    def _check_duplicate_symbols(self):
        """Check for duplicate symbols in the same scope."""
        seen_symbols = {}
        
        for symbol in self.symbol_table:
            key = (symbol['name'], symbol['scope'])
            if key in seen_symbols:
                error_msg = f"Error semántico: Símbolo duplicado '{symbol['name']}' en el ámbito '{symbol['scope']}'. "
                error_msg += f"Los símbolos deben tener nombres únicos dentro de un mismo ámbito."
                self.errors.append(error_msg)
            else:
                seen_symbols[key] = True
    
    def _analyze_scopes(self):
        """Perform simplified scope analysis."""
        # This is a simplified approximation based on the information available
        # A real implementation would need to track block scopes, etc.
        
        # Update function parameters to be in function scope
        for symbol in self.symbol_table:
            if symbol['kind'] == 'function':
                func_name = symbol['name']
                for param_symbol in [s for s in self.symbol_table if s['kind'] == 'parameter']:
                    param_symbol['scope'] = f"function:{func_name}"
    
    def type_check(self):
        """
        Perform type checking on the AST.
        
        Returns:
            tuple: (result, errors) where result is a dictionary of analysis results
                  and errors is a list of error messages.
        """
        # Reset errors
        self.errors = []
        
        # Extract from the AST graph
        graph = self.ast.get('graph', None)
        elements = self.ast.get('elements', [])
        
        if not graph:
            self.errors.append("No AST graph available for type checking")
            return {}, self.errors
        
        # Results to store type checking information
        type_results = {
            'type_mismatches': [],
            'incompatible_assignments': [],
            'undefined_variables': []
        }
        
        # Check variable assignments and expressions
        for node, data in graph.nodes(data=True):
            # Check binary expressions
            if data.get('type') == 'binary_expr':
                operator = data.get('operator', '')
                left_operand = None
                right_operand = None
                
                # Get the operands
                for _, target, edge_data in graph.out_edges(node, data=True):
                    if edge_data.get('label') == 'left':
                        left_operand = target
                    elif edge_data.get('label') == 'right':
                        right_operand = target
                
                if left_operand and right_operand:
                    left_type = self._get_type(left_operand)
                    right_type = self._get_type(right_operand)
                    
                    if left_type and right_type:
                        compatible = self._are_types_compatible(left_type, right_type, operator)
                        if not compatible:
                            self.errors.append(f"Incompatible types in binary expression: {left_type} {operator} {right_type}")
                            type_results['type_mismatches'].append({
                                'expression': f"{left_operand} {operator} {right_operand}",
                                'left_type': left_type,
                                'right_type': right_type
                            })
            
            # Check assignments
            elif data.get('type') == 'variable':
                var_name = node
                var_type = data.get('data_type', 'unknown')
                
                for _, target, edge_data in graph.out_edges(node, data=True):
                    if edge_data.get('label') in ['=', '+=', '-=', '*=', '/=', '%=']:
                        assignment_operator = edge_data.get('label')
                        expr_type = self._get_expression_type(graph, target)
                        
                        if expr_type:
                            compatible = self._are_types_compatible(var_type, expr_type, assignment_operator)
                            if not compatible:
                                self.errors.append(f"Incompatible assignment: {var_type} {var_name} {assignment_operator} {expr_type}")
                                type_results['incompatible_assignments'].append({
                                    'variable': var_name,
                                    'var_type': var_type,
                                    'expr_type': expr_type,
                                    'operator': assignment_operator
                                })
        
        # Check for undefined variables
        defined_vars = set(symbol['name'] for symbol in self.symbol_table)
        for element in elements:
            if element['type'] in ['Binary Expression', 'Assignment Expression']:
                expr = element['value']
                # This is a simplified check - a real implementation would parse the expression
                for token in expr.split():
                    if token.isalnum() and token not in defined_vars and not token[0].isdigit():
                        # Ignore operators and literals
                        if token not in ['+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=']:
                            self.errors.append(f"Undefined variable '{token}'")
                            type_results['undefined_variables'].append(token)
        
        return type_results, self.errors
    
    def _get_type(self, var_name):
        """Get the type of a variable from the symbol table."""
        for symbol in self.symbol_table:
            if symbol['name'] == var_name:
                return symbol['data_type']
        return None
    
    def _get_expression_type(self, graph, expr_node):
        """Determine the type of an expression node with improved type inference."""
        try:
            node_data = graph.nodes[expr_node]
            
            if 'expr' in node_data:
                # Análisis detallado para determinar el tipo de expresiones complejas
                expr = node_data['expr']
                
                # Comprobaciones para tipos literales
                if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                    return 'int'
                elif expr.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in expr[2:]):
                    return 'int'  # Hexadecimal
                elif '.' in expr and (
                    (expr.split('.')[0].isdigit() or not expr.split('.')[0]) and 
                    (expr.split('.')[1].isdigit() or not expr.split('.')[1])
                ):
                    return 'float'
                elif expr.startswith('"') and expr.endswith('"'):
                    return 'string'
                elif expr.startswith("'") and expr.endswith("'") and len(expr) == 3:
                    return 'char'
                elif expr.lower() in ['true', 'false']:
                    return 'bool'
                elif expr in ['NULL', 'nullptr']:
                    return 'pointer'
                    
                # Análisis de operadores para inferir tipos
                if '+' in expr or '-' in expr or '*' in expr or '/' in expr:
                    # Operaciones aritméticas
                    has_float = any('.' in token for token in expr.split())
                    if has_float:
                        return 'float'
                    return 'int'
                elif '==' in expr or '!=' in expr or '<' in expr or '>' in expr or '<=' in expr or '>=' in expr:
                    # Comparaciones
                    return 'bool'
                elif '&&' in expr or '||' in expr or '!' in expr:
                    # Operaciones lógicas
                    return 'bool'
                    
                # Buscar si algún token es un identificador conocido
                for token in expr.split():
                    # Eliminar posibles operadores o caracteres especiales
                    clean_token = token.strip('+-*/(){}[];,.')
                    if clean_token and clean_token.isalnum() and not clean_token[0].isdigit():
                        for symbol in self.symbol_table:
                            if symbol['name'] == clean_token:
                                return symbol['data_type']
                
                # Si llegamos aquí y no hemos determinado el tipo, es desconocido
                self.error_context[f"expr_type_unknown_{expr_node}"] = {
                    'expr': expr,
                    'tokens': expr.split()
                }
                return 'unknown'
            else:
                # Para nodos que son literales o identificadores directos
                node_type = node_data.get('type', '')
                
                # Mapear tipos de token a tipos de datos de C
                type_map = {
                    'INTEGER': 'int',
                    'FLOAT_NUM': 'float',
                    'CHAR_CONST': 'char',
                    'STRING_LITERAL': 'string',
                    'ID': None  # Para identificadores, necesitamos buscar en la tabla de símbolos
                }
                
                if node_type in type_map:
                    if type_map[node_type] is not None:
                        return type_map[node_type]
                    else:
                        # Es un identificador, buscamos en la tabla de símbolos
                        for symbol in self.symbol_table:
                            if symbol['name'] == expr_node:
                                return symbol['data_type']
                
                # Si no podemos determinar el tipo por otros medios, verificamos
                # si el nodo mismo tiene un 'data_type' especificado
                if 'data_type' in node_data:
                    return node_data['data_type']
                
                # Último recurso, buscar en la tabla de símbolos por nombre de nodo
                if isinstance(expr_node, str):
                    for symbol in self.symbol_table:
                        if symbol['name'] == expr_node:
                            return symbol['data_type']
            
            # Si todo falla, registramos información para depuración
            self.error_context[f"type_inference_fail_{expr_node}"] = {
                'node': expr_node,
                'node_data': {k: v for k, v in node_data.items()}
            }
            
            return 'unknown'
        except Exception as e:
            # Capturar cualquier error y dar información útil
            self.errors.append(f"Error al determinar el tipo de expresión: {str(e)}")
            return 'unknown'
    
    def _are_types_compatible(self, type1, type2, operator):
        """Check if two types are compatible for the given operator."""
        # Simplified type compatibility rules
        numeric_types = ['int', 'float', 'double', 'long', 'short']
        
        # Arithmetic operators
        if operator in ['+', '-', '*', '/', '%', '+=', '-=', '*=', '/=', '%=']:
            if type1 in numeric_types and type2 in numeric_types:
                return True
            if type1 == 'char*' and type2 == 'char*' and operator == '+':
                # Allow string concatenation
                return True
            return False
        
        # Comparison operators
        elif operator in ['<', '>', '<=', '>=', '==', '!=']:
            if type1 in numeric_types and type2 in numeric_types:
                return True
            if type1 == type2:  # Same types can always be compared
                return True
            return False
        
        # Assignment
        elif operator == '=':
            # Allow numeric type conversion with potential loss warning
            if type1 in numeric_types and type2 in numeric_types:
                if (type1 == 'int' and type2 in ['float', 'double']) or \
                   (type1 == 'float' and type2 == 'double'):
                    self.errors.append(f"Warning: Possible loss of precision in assignment from {type2} to {type1}")
                return True
            
            if type1 == type2:  # Same types can always be assigned
                return True
            
            # Pointer assignment compatibility would go here
            
            return False
        
        # Logical operators
        elif operator in ['&&', '||', '!']:
            # Most types can be used in logical expressions
            return True
        
        # Default: assume incompatible
        return False
    
    def verify_expressions(self):
        """
        Verify arithmetic and logical expressions in the AST.
        
        Returns:
            tuple: (result, errors) where result is a dictionary of analysis results
                  and errors is a list of error messages.
        """
        # Reset errors
        self.errors = []
        
        # Extract from the AST
        graph = self.ast.get('graph', None)
        elements = self.ast.get('elements', [])
        
        if not graph:
            self.errors.append("No AST graph available for expression verification")
            return {}, self.errors
        
        # Results to store verification information
        expr_results = {
            'verified_expressions': [],
            'potential_issues': []
        }
        
        # Check expressions in the AST
        for element in elements:
            if element['type'] == 'Binary Expression':
                expr = element['value']
                expr_parts = expr.split()
                
                if len(expr_parts) >= 3:
                    left = expr_parts[0]
                    operator = expr_parts[1]
                    right = expr_parts[2]
                    
                    # Check division by zero
                    if operator == '/' and right.isdigit() and int(right) == 0:
                        self.errors.append(f"Error: Division by zero in expression: {expr}")
                        expr_results['potential_issues'].append({
                            'expression': expr,
                            'issue': 'Division by zero'
                        })
                    
                    # Check for potential overflow
                    if operator in ['+', '*'] and all(p.isdigit() for p in [left, right]):
                        if operator == '+' and int(left) > 1000000 and int(right) > 1000000:
                            self.errors.append(f"Warning: Potential integer overflow in addition: {expr}")
                            expr_results['potential_issues'].append({
                                'expression': expr,
                                'issue': 'Potential overflow'
                            })
                        elif operator == '*' and int(left) > 1000 and int(right) > 1000:
                            self.errors.append(f"Warning: Potential integer overflow in multiplication: {expr}")
                            expr_results['potential_issues'].append({
                                'expression': expr,
                                'issue': 'Potential overflow'
                            })
                    
                    # If verification passes, add to verified list
                    if not any(issue['expression'] == expr for issue in expr_results['potential_issues']):
                        expr_results['verified_expressions'].append(expr)
            
            elif element['type'] == 'Assignment Expression':
                expr = element['value']
                expr_parts = expr.split('=')
                
                if len(expr_parts) >= 2:
                    left = expr_parts[0].strip()
                    right = expr_parts[1].strip()
                    
                    # Check self-assignment
                    if left == right:
                        self.errors.append(f"Warning: Self-assignment detected: {expr}")
                        expr_results['potential_issues'].append({
                            'expression': expr,
                            'issue': 'Self-assignment'
                        })
                    
                    # If verification passes, add to verified list
                    if not any(issue['expression'] == expr for issue in expr_results['potential_issues']):
                        expr_results['verified_expressions'].append(expr)
        
        return expr_results, self.errors
    
    def verify_control_flow(self):
        """
        Verify control flow structures in the AST.
        
        Returns:
            tuple: (result, errors) where result is a dictionary of analysis results
                  and errors is a list of error messages.
        """
        # Reset errors
        self.errors = []
        
        # Extract from the AST
        graph = self.ast.get('graph', None)
        elements = self.ast.get('elements', [])
        
        if not graph:
            self.errors.append("Error semántico: No hay grafo AST disponible para la verificación de flujo de control.")
            return {}, self.errors
        
        # Results to store verification information
        flow_results = {
            'verified_structures': [],
            'potential_issues': []
        }
        
        # Check control structures in the AST
        for node, data in graph.nodes(data=True):
            # Check conditions of if statements
            if data.get('type') == 'if_statement':
                # Get condition node
                condition_node = None
                for _, target, edge_data in graph.out_edges(node, data=True):
                    if edge_data.get('label') == 'condition':
                        condition_node = target
                        break
                
                if condition_node:
                    condition_data = graph.nodes[condition_node]
                    condition = condition_data.get('condition', '')
                    
                    # Check for constant conditions
                    if condition in ['true', 'false', '0', '1']:
                        self.errors.append(f"Warning: Constant condition in if statement: {condition}")
                        flow_results['potential_issues'].append({
                            'structure': f"if ({condition})",
                            'issue': 'Constant condition'
                        })
                    
                    # Check for assignment in condition (common mistake)
                    if '=' in condition and '==' not in condition and '!=' not in condition:
                        self.errors.append(f"Warning: Assignment in if condition: {condition}")
                        flow_results['potential_issues'].append({
                            'structure': f"if ({condition})",
                            'issue': 'Assignment in condition'
                        })
                    
                    # If verification passes, add to verified list
                    structure_type = f"if ({condition})"
                    if not any(issue['structure'] == structure_type for issue in flow_results['potential_issues']):
                        flow_results['verified_structures'].append(structure_type)
            
            # Check conditions of while loops
            elif data.get('type') == 'while_loop':
                # Get condition node
                condition_node = None
                for _, target, edge_data in graph.out_edges(node, data=True):
                    if edge_data.get('label') == 'condition':
                        condition_node = target
                        break
                
                if condition_node:
                    condition_data = graph.nodes[condition_node]
                    condition = condition_data.get('condition', '')
                    
                    # Check for constant true condition (infinite loop)
                    if condition in ['true', '1']:
                        self.errors.append(f"Warning: Infinite loop detected: while ({condition})")
                        flow_results['potential_issues'].append({
                            'structure': f"while ({condition})",
                            'issue': 'Infinite loop'
                        })
                    
                    # Check for constant false condition (unreachable code)
                    elif condition in ['false', '0']:
                        self.errors.append(f"Warning: Loop never executes: while ({condition})")
                        flow_results['potential_issues'].append({
                            'structure': f"while ({condition})",
                            'issue': 'Unreachable code'
                        })
                    
                    # If verification passes, add to verified list
                    structure_type = f"while ({condition})"
                    if not any(issue['structure'] == structure_type for issue in flow_results['potential_issues']):
                        flow_results['verified_structures'].append(structure_type)
            
            # Check for loops
            elif data.get('type') == 'for_loop':
                # Get initialization, condition, and increment nodes
                init_node = None
                cond_node = None
                incr_node = None
                
                for _, target, edge_data in graph.out_edges(node, data=True):
                    if edge_data.get('label') == 'init':
                        init_node = target
                    elif edge_data.get('label') == 'condition':
                        cond_node = target
                    elif edge_data.get('label') == 'increment':
                        incr_node = target
                
                if cond_node:
                    condition_data = graph.nodes[cond_node]
                    condition = condition_data.get('condition', '')
                    
                    # Check for constant condition
                    if condition in ['true', 'false', '0', '1']:
                        structure_type = "for loop with constant condition"
                        issue_type = 'Infinite loop' if condition in ['true', '1'] else 'Unreachable code'
                        
                        self.errors.append(f"Warning: {issue_type} in for loop: for (...; {condition}; ...)")
                        flow_results['potential_issues'].append({
                            'structure': structure_type,
                            'issue': issue_type
                        })
                    else:
                        flow_results['verified_structures'].append("for loop")
        
        return flow_results, self.errors
