import networkx as nx

class IntermediateCodeGenerator:
    """
    Intermediate code generator for C code.
    Generates three-address code from the AST.
    """
    
    def __init__(self, ast, symbol_table=None):
        self.ast = ast
        self.symbol_table = symbol_table or []
        self.intermediate_code = []
        self.temp_var_count = 0
        self.label_count = 0
        self.errors = []
        
        # Set up a control flow graph
        self.cfg = nx.DiGraph()
    
    def generate(self):
        """
        Generate intermediate code from the AST.
        
        Returns:
            tuple: (code_str, errors) where code_str is the generated intermediate code
                  and errors is a list of error messages.
        """
        # Reset
        self.intermediate_code = []
        self.temp_var_count = 0
        self.label_count = 0
        self.errors = []
        self.cfg = nx.DiGraph()
        
        # Get AST components
        graph = self.ast.get('graph', None)
        elements = self.ast.get('elements', [])
        
        if not graph:
            self.errors.append("No AST graph available for code generation")
            return "", self.errors
        
        # Start with program entry
        self.intermediate_code.append("# Intermediate Code")
        self.intermediate_code.append("# --------------")
        
        # Process different types of nodes in the AST
        # Map AST node processing to specific generation methods
        for element in elements:
            element_type = element.get('type', '')
            
            if element_type == 'Variable Declaration':
                self._generate_var_declaration(element)
            elif element_type == 'Assignment Expression':
                self._generate_assignment(element)
            elif element_type == 'Binary Expression':
                self._generate_binary_expr(element)
            elif element_type == 'If Statement':
                self._generate_if_statement(element)
            elif element_type == 'While Loop':
                self._generate_while_loop(element)
            elif element_type == 'For Loop':
                self._generate_for_loop(element)
            elif element_type == 'Method Declaration':
                self._generate_method_declaration(element)
        
        # Also process nodes from the graph
        for node, data in graph.nodes(data=True):
            node_type = data.get('type', '')
            
            if node_type == 'switch_statement':
                self._generate_switch_statement(node, data, graph)
        
        # Combine all code into a single string
        code_str = '\n'.join(self.intermediate_code)
        return code_str, self.errors
    
    def _generate_var_declaration(self, element):
        """Generate code for variable declaration."""
        value = element.get('value', '')
        parts = value.split('=')
        
        var_decl = parts[0].strip()
        
        # Add to intermediate code
        self.intermediate_code.append(f"# Variable declaration")
        self.intermediate_code.append(f"DECL {var_decl}")
        
        # If it has an initialization
        if len(parts) > 1:
            var_name = var_decl.split()[-1]  # Get variable name
            init_value = parts[1].strip()
            self.intermediate_code.append(f"ASSIGN {var_name}, {init_value}")
        
        self.intermediate_code.append("")  # Empty line for readability
    
    def _generate_assignment(self, element):
        """Generate code for assignment expression."""
        value = element.get('value', '')
        parts = value.split('=', 1)  # Split only on first equals sign
        
        if len(parts) < 2:
            self.errors.append(f"Invalid assignment expression: {value}")
            return
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        # Check for compound assignments (+=, -=, etc.)
        compound_ops = {'+=': '+', '-=': '-', '*=': '*', '/=': '/', '%=': '%'}
        for op_symbol, basic_op in compound_ops.items():
            if op_symbol in lhs:
                var_parts = lhs.split(op_symbol)
                var_name = var_parts[0].strip()
                
                # Generate a temporary for the operation
                temp = self._new_temp()
                self.intermediate_code.append(f"{temp} = {var_name} {basic_op} {rhs}")
                self.intermediate_code.append(f"{var_name} = {temp}")
                return
        
        # Handle simple assignment with the new format
        self.intermediate_code.append(f"# Assignment")
        
        # Check if RHS is a complex expression
        if any(op in rhs for op in ['+', '-', '*', '/', '%', '<', '>', '==', '!=', '&&', '||']):
            # Parse and generate code for the expression
            temp = self._new_temp()
            
            # Is it a constant?
            if rhs.isdigit() or (rhs.startswith('-') and rhs[1:].isdigit()):
                self.intermediate_code.append(f"{temp} = {rhs}       # {temp} es una etiqueta temporal que representa la constante {rhs}")
                self.intermediate_code.append(f"{lhs} = {temp}       # Asigna el valor de {temp} a {lhs}")
            else:
                # It's a more complex expression
                expression_temp = self._generate_expression(rhs)
                self.intermediate_code.append(f"{lhs} = {expression_temp}")
        else:
            # Direct assignment of a constant or variable
            temp = self._new_temp()
            
            # Is it a constant?
            if rhs.isdigit() or (rhs.startswith('-') and rhs[1:].isdigit()):
                self.intermediate_code.append(f"{temp} = {rhs}       # {temp} es una etiqueta temporal que representa la constante {rhs}")
                self.intermediate_code.append(f"{lhs} = {temp}       # Asigna el valor de {temp} a {lhs}")
            else:
                # It's a variable
                self.intermediate_code.append(f"{lhs} = {rhs}")
        
        self.intermediate_code.append("")  # Empty line for readability
    
    def _generate_expression(self, expr):
        """
        Generate code for a complex expression.
        Returns the temporary variable holding the result.
        """
        # This is a simplified expression parser
        # A real implementation would use a proper parser
        
        # Check for logical operators first (lowest precedence)
        if '&&' in expr:
            parts = expr.split('&&')
            left_temp = self._generate_expression(parts[0].strip())
            right_temp = self._generate_expression(parts[1].strip())
            result_temp = self._new_temp()
            self.intermediate_code.append(f"{result_temp} = {left_temp} && {right_temp}  # {result_temp} es una etiqueta temporal para la operación lógica AND")
            return result_temp
        
        if '||' in expr:
            parts = expr.split('||')
            left_temp = self._generate_expression(parts[0].strip())
            right_temp = self._generate_expression(parts[1].strip())
            result_temp = self._new_temp()
            self.intermediate_code.append(f"{result_temp} = {left_temp} || {right_temp}  # {result_temp} es una etiqueta temporal para la operación lógica OR")
            return result_temp
        
        # Check for comparison operators
        for op in ['==', '!=', '<=', '>=', '<', '>']:
            if op in expr:
                parts = expr.split(op)
                left_temp = self._generate_expression(parts[0].strip())
                right_temp = self._generate_expression(parts[1].strip())
                result_temp = self._new_temp()
                self.intermediate_code.append(f"{result_temp} = {left_temp} {op} {right_temp}  # {result_temp} es una etiqueta temporal para la comparación")
                return result_temp
        
        # Check for arithmetic operators
        for op in ['+', '-']:
            if op in expr and not expr.startswith(op):  # Avoid unary operators
                parts = expr.split(op)
                left_temp = self._generate_expression(parts[0].strip())
                right_temp = self._generate_expression(parts[1].strip())
                result_temp = self._new_temp()
                
                op_name = "suma" if op == "+" else "resta"
                self.intermediate_code.append(f"{result_temp} = {left_temp} {op} {right_temp}  # {result_temp} es una etiqueta temporal para la {op_name}")
                return result_temp
        
        for op in ['*', '/', '%']:
            if op in expr:
                parts = expr.split(op)
                left_temp = self._generate_expression(parts[0].strip())
                right_temp = self._generate_expression(parts[1].strip())
                result_temp = self._new_temp()
                
                if op == '*':
                    op_name = "multiplicación"
                elif op == '/':
                    # Agregar validación para división por cero
                    if right_temp.isdigit() and int(right_temp) == 0:
                        self.intermediate_code.append(f"if {right_temp} == 0 then error \"Division by zero\" # Valida que no se realice división por cero")
                    op_name = "división"
                else:
                    op_name = "módulo"
                
                self.intermediate_code.append(f"{result_temp} = {left_temp} {op} {right_temp}  # {result_temp} es una etiqueta temporal para la {op_name}")
                return result_temp
        
        # If it's a simple value, just return it
        if expr.strip().startswith('t'):
            # It's already a temp variable
            return expr.strip()
        else:
            # Create a new temp for the value
            temp = self._new_temp()
            
            # Is it a constant?
            if expr.strip().isdigit() or (expr.strip().startswith('-') and expr.strip()[1:].isdigit()):
                self.intermediate_code.append(f"{temp} = {expr.strip()}  # {temp} es una etiqueta temporal que representa la constante {expr.strip()}")
            else:
                # It's a variable or other value
                self.intermediate_code.append(f"{temp} = {expr.strip()}")
            
            return temp
    
    def _generate_binary_expr(self, element):
        """Generate code for binary expression."""
        value = element.get('value', '')
        
        # Split the expression into parts
        parts = value.split(' ', 2)
        if len(parts) < 3:
            self.errors.append(f"Invalid binary expression: {value}")
            return
        
        left = parts[0]
        operator = parts[1]
        right = parts[2]
        
        # Generate intermediates for operands if needed
        if left.isdigit() or (left.startswith('-') and left[1:].isdigit()):
            left_temp = self._new_temp()
            self.intermediate_code.append(f"{left_temp} = {left}    # {left_temp} es una etiqueta temporal que representa la constante {left}")
            left = left_temp
        
        if right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
            right_temp = self._new_temp()
            self.intermediate_code.append(f"{right_temp} = {right}    # {right_temp} es una etiqueta temporal que representa la constante {right}")
            right = right_temp
        
        # Generate a temporary for the result
        result_temp = self._new_temp()
        
        # Determine operation type for comment
        if operator in ['+', '-', '*', '/']:
            op_names = {'+': 'suma', '-': 'resta', '*': 'multiplicación', '/': 'división'}
            op_name = op_names.get(operator, 'operación')
            
            # Add validation for division by zero
            if operator == '/' and right.isdigit() and int(right) == 0:
                self.intermediate_code.append(f"if {right} == 0 then error \"Division by zero\" # Valida que no se realice división por cero")
                
            self.intermediate_code.append(f"# Expresión binaria: {op_name}")
            self.intermediate_code.append(f"{result_temp} = {left} {operator} {right}    # {result_temp} es una etiqueta temporal para la {op_name}")
        elif operator in ['<', '>', '<=', '>=', '==', '!=']:
            self.intermediate_code.append(f"# Expresión de comparación")
            self.intermediate_code.append(f"{result_temp} = {left} {operator} {right}    # {result_temp} es una etiqueta temporal para la comparación")
        elif operator in ['&&', '||']:
            op_names = {'&&': 'AND', '||': 'OR'}
            op_name = op_names.get(operator, 'lógica')
            self.intermediate_code.append(f"# Expresión lógica")
            self.intermediate_code.append(f"{result_temp} = {left} {operator} {right}    # {result_temp} es una etiqueta temporal para la operación lógica {op_name}")
        else:
            self.intermediate_code.append(f"# Expresión binaria")
            self.intermediate_code.append(f"{result_temp} = {left} {operator} {right}")
        
        self.intermediate_code.append("")  # Empty line for readability
    
    def _generate_if_statement(self, element):
        """Generate code for if statement."""
        value = element.get('value', '')
        
        # Extract condition from "if (condition)"
        if '(' in value and ')' in value:
            condition = value[value.find('(')+1:value.find(')')]
        else:
            self.errors.append(f"Invalid if statement format: {value}")
            return
        
        # Generate labels for the branches
        else_label = self._new_label()
        end_label = self._new_label()
        
        # Generate condition code
        self.intermediate_code.append(f"# If Statement")
        self.intermediate_code.append(f"# Condition: {condition}")
        
        # Check if condition is complex
        if any(op in condition for op in ['+', '-', '*', '/', '%', '<', '>', '==', '!=', '&&', '||']):
            condition_temp = self._generate_expression(condition)
            self.intermediate_code.append(f"IF !{condition_temp} GOTO {else_label}")
        else:
            self.intermediate_code.append(f"IF !{condition} GOTO {else_label}")
        
        # Placeholder for the 'then' block code
        self.intermediate_code.append("# Then block code would be here")
        self.intermediate_code.append(f"GOTO {end_label}")
        
        # Else block
        self.intermediate_code.append(f"LABEL {else_label}")
        self.intermediate_code.append("# Else block code would be here")
        
        # End of if
        self.intermediate_code.append(f"LABEL {end_label}")
        self.intermediate_code.append("")  # Empty line for readability
        
        # Add to control flow graph
        self.cfg.add_node(f"cond_{condition}", type="condition")
        self.cfg.add_node(f"then_block", type="block")
        self.cfg.add_node(f"else_block", type="block")
        self.cfg.add_node(f"end_if", type="block")
        
        self.cfg.add_edge(f"cond_{condition}", f"then_block", label="true")
        self.cfg.add_edge(f"cond_{condition}", f"else_block", label="false")
        self.cfg.add_edge(f"then_block", f"end_if")
        self.cfg.add_edge(f"else_block", f"end_if")
    
    def _generate_while_loop(self, element):
        """Generate code for while loop."""
        value = element.get('value', '')
        
        # Extract condition from "while (condition)"
        if '(' in value and ')' in value:
            condition = value[value.find('(')+1:value.find(')')]
        else:
            self.errors.append(f"Invalid while statement format: {value}")
            return
        
        # Generate labels for the loop
        start_label = self._new_label()
        end_label = self._new_label()
        
        # Generate code
        self.intermediate_code.append(f"# While Loop")
        self.intermediate_code.append(f"LABEL {start_label}")
        self.intermediate_code.append(f"# Condition: {condition}")
        
        # Check if condition is complex
        if any(op in condition for op in ['+', '-', '*', '/', '%', '<', '>', '==', '!=', '&&', '||']):
            condition_temp = self._generate_expression(condition)
            self.intermediate_code.append(f"IF !{condition_temp} GOTO {end_label}")
        else:
            self.intermediate_code.append(f"IF !{condition} GOTO {end_label}")
        
        # Placeholder for the loop body
        self.intermediate_code.append("# Loop body code would be here")
        self.intermediate_code.append(f"GOTO {start_label}")
        
        # End of loop
        self.intermediate_code.append(f"LABEL {end_label}")
        self.intermediate_code.append("")  # Empty line for readability
        
        # Add to control flow graph
        self.cfg.add_node(f"while_cond_{condition}", type="condition")
        self.cfg.add_node(f"while_body", type="block")
        self.cfg.add_node(f"end_while", type="block")
        
        self.cfg.add_edge(f"while_cond_{condition}", f"while_body", label="true")
        self.cfg.add_edge(f"while_cond_{condition}", f"end_while", label="false")
        self.cfg.add_edge(f"while_body", f"while_cond_{condition}")
    
    def _generate_for_loop(self, element):
        """Generate code for for loop."""
        value = element.get('value', '')
        
        # Extract components from "for (init; condition; increment)"
        if '(' in value and ')' in value:
            for_parts = value[value.find('(')+1:value.find(')')].split(';')
            if len(for_parts) == 3:
                init = for_parts[0].strip()
                condition = for_parts[1].strip()
                increment = for_parts[2].strip()
            else:
                self.errors.append(f"Invalid for loop format: {value}")
                return
        else:
            self.errors.append(f"Invalid for loop format: {value}")
            return
        
        # Generate labels for the loop
        start_label = self._new_label()
        end_label = self._new_label()
        
        # Generate code
        self.intermediate_code.append(f"# For Loop")
        
        # Initialization
        if init:
            self.intermediate_code.append(f"# Initialization: {init}")
            if '=' in init:
                var, expr = init.split('=', 1)
                self.intermediate_code.append(f"ASSIGN {var.strip()}, {expr.strip()}")
        
        # Loop start
        self.intermediate_code.append(f"LABEL {start_label}")
        
        # Condition check
        if condition:
            self.intermediate_code.append(f"# Condition: {condition}")
            if any(op in condition for op in ['+', '-', '*', '/', '%', '<', '>', '==', '!=', '&&', '||']):
                condition_temp = self._generate_expression(condition)
                self.intermediate_code.append(f"IF !{condition_temp} GOTO {end_label}")
            else:
                self.intermediate_code.append(f"IF !{condition} GOTO {end_label}")
        
        # Placeholder for the loop body
        self.intermediate_code.append("# Loop body code would be here")
        
        # Increment
        if increment:
            self.intermediate_code.append(f"# Increment: {increment}")
            if '=' in increment:
                var, expr = increment.split('=', 1)
                self.intermediate_code.append(f"ASSIGN {var.strip()}, {expr.strip()}")
            elif '+=' in increment:
                var, expr = increment.split('+=', 1)
                self.intermediate_code.append(f"ASSIGN {var.strip()}, {var.strip()} + {expr.strip()}")
            elif '-=' in increment:
                var, expr = increment.split('-=', 1)
                self.intermediate_code.append(f"ASSIGN {var.strip()}, {var.strip()} - {expr.strip()}")
            elif '++' in increment:
                var = increment.replace('++', '').strip()
                self.intermediate_code.append(f"ASSIGN {var}, {var} + 1")
            elif '--' in increment:
                var = increment.replace('--', '').strip()
                self.intermediate_code.append(f"ASSIGN {var}, {var} - 1")
        
        # Loop back
        self.intermediate_code.append(f"GOTO {start_label}")
        
        # End of loop
        self.intermediate_code.append(f"LABEL {end_label}")
        self.intermediate_code.append("")  # Empty line for readability
        
        # Add to control flow graph
        self.cfg.add_node(f"for_init", type="block")
        self.cfg.add_node(f"for_cond_{condition}", type="condition")
        self.cfg.add_node(f"for_body", type="block")
        self.cfg.add_node(f"for_incr", type="block")
        self.cfg.add_node(f"end_for", type="block")
        
        self.cfg.add_edge(f"for_init", f"for_cond_{condition}")
        self.cfg.add_edge(f"for_cond_{condition}", f"for_body", label="true")
        self.cfg.add_edge(f"for_cond_{condition}", f"end_for", label="false")
        self.cfg.add_edge(f"for_body", f"for_incr")
        self.cfg.add_edge(f"for_incr", f"for_cond_{condition}")
    
    def _generate_switch_statement(self, node, data, graph):
        """Generate code for switch statement."""
        # Find the expression node
        expr_node = None
        for _, target, edge_data in graph.out_edges(node, data=True):
            if edge_data.get('label') == 'expression':
                expr_node = target
                break
        
        if not expr_node:
            self.errors.append(f"Switch statement missing expression")
            return
        
        expr_data = graph.nodes[expr_node]
        expr = expr_data.get('expr', '')
        
        # Find case nodes
        case_nodes = []
        default_node = None
        for _, target, edge_data in graph.out_edges(node, data=True):
            if edge_data.get('label') == 'case':
                case_nodes.append(target)
            elif edge_data.get('label') == 'default':
                default_node = target
        
        # Generate labels
        case_labels = {}
        for case_node in case_nodes:
            case_data = graph.nodes[case_node]
            case_value = case_data.get('value', '')
            case_labels[case_value] = self._new_label()
        
        default_label = self._new_label() if default_node else None
        end_label = self._new_label()
        
        # Generate code
        self.intermediate_code.append(f"# Switch Statement")
        self.intermediate_code.append(f"# Expression: {expr}")
        
        # Generate comparison for each case
        expr_temp = self._generate_expression(expr)
        for case_value, label in case_labels.items():
            self.intermediate_code.append(f"IF {expr_temp} == {case_value} GOTO {label}")
        
        # Jump to default if no case matches
        if default_label:
            self.intermediate_code.append(f"GOTO {default_label}")
        else:
            self.intermediate_code.append(f"GOTO {end_label}")
        
        # Generate case blocks
        for case_node in case_nodes:
            case_data = graph.nodes[case_node]
            case_value = case_data.get('value', '')
            label = case_labels[case_value]
            
            self.intermediate_code.append(f"LABEL {label}")
            self.intermediate_code.append(f"# Case {case_value} code would be here")
            self.intermediate_code.append(f"GOTO {end_label}")
        
        # Generate default block if it exists
        if default_label:
            self.intermediate_code.append(f"LABEL {default_label}")
            self.intermediate_code.append("# Default case code would be here")
        
        # End of switch
        self.intermediate_code.append(f"LABEL {end_label}")
        self.intermediate_code.append("")  # Empty line for readability
        
        # Add to control flow graph
        self.cfg.add_node(f"switch_{expr}", type="switch")
        for case_value in case_labels:
            self.cfg.add_node(f"case_{case_value}", type="case")
            self.cfg.add_edge(f"switch_{expr}", f"case_{case_value}", label=case_value)
        
        if default_node:
            self.cfg.add_node("default_case", type="default")
            self.cfg.add_edge(f"switch_{expr}", "default_case", label="default")
        
        self.cfg.add_node("end_switch", type="block")
        for case_value in case_labels:
            self.cfg.add_edge(f"case_{case_value}", "end_switch")
        
        if default_node:
            self.cfg.add_edge("default_case", "end_switch")
    
    def _generate_method_declaration(self, element):
        """Generate code for method declaration."""
        value = element.get('value', '')
        
        # Parse method signature: "return_type method_name(param_list)"
        if '(' in value and ')' in value:
            signature = value[:value.find('(')]
            params = value[value.find('(')+1:value.find(')')]
            
            parts = signature.split()
            if len(parts) >= 2:
                return_type = ' '.join(parts[:-1])
                method_name = parts[-1]
            else:
                self.errors.append(f"Invalid method declaration: {value}")
                return
        else:
            self.errors.append(f"Invalid method declaration: {value}")
            return
        
        # Generate code for method entry
        self.intermediate_code.append(f"# Method Declaration")
        self.intermediate_code.append(f"FUNC_BEGIN {method_name}")
        
        # Process parameters
        if params:
            param_list = params.split(',')
            for i, param in enumerate(param_list):
                param = param.strip()
                self.intermediate_code.append(f"PARAM {param}")
        
        # Placeholder for method body
        self.intermediate_code.append("# Method body code would be here")
        
        # Return statement (placeholder)
        if return_type != 'void':
            self.intermediate_code.append("# Return statement would be here")
        
        # Method exit
        self.intermediate_code.append(f"FUNC_END {method_name}")
        self.intermediate_code.append("")  # Empty line for readability
        
        # Add to control flow graph
        self.cfg.add_node(f"method_{method_name}", type="method", return_type=return_type)
        self.cfg.add_node(f"method_{method_name}_entry", type="block")
        self.cfg.add_node(f"method_{method_name}_exit", type="block")
        
        self.cfg.add_edge(f"method_{method_name}", f"method_{method_name}_entry", label="entry")
        self.cfg.add_edge(f"method_{method_name}_entry", f"method_{method_name}_exit", label="return")
    
    def _new_temp(self):
        """Generate a new temporary variable name."""
        temp = f"t{self.temp_var_count}"
        self.temp_var_count += 1
        return temp
    
    def _new_label(self):
        """Generate a new label for code blocks."""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def generate_control_flow_graph(self):
        """
        Generate a control flow graph for the intermediate code.
        
        Returns:
            networkx.DiGraph: The control flow graph
        """
        if not self.cfg.nodes():
            # If CFG hasn't been built yet, generate the intermediate code first
            if not self.intermediate_code:
                self.generate()
        
        return self.cfg
