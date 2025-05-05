import pandas as pd
from .utils import format_symbol_table, format_errors

class Symbol:
    """Class representing a symbol in the symbol table."""
    def __init__(self, name, type_name, scope, line, is_function=False, params=None):
        self.name = name
        self.type = type_name
        self.scope = scope
        self.line = line
        self.is_function = is_function
        self.params = params or []
        self.used = False
    
    def to_dict(self):
        """Convert the symbol to a dictionary."""
        return {
            'name': self.name,
            'type': self.type,
            'scope': self.scope,
            'line': self.line,
            'is_function': self.is_function,
            'params': self.params,
            'used': self.used
        }

class SymbolTable:
    """Symbol table for tracking variables, functions, and types."""
    def __init__(self):
        self.symbols = []
        self.scopes = ['global']
        self.current_scope = 'global'
    
    def enter_scope(self, scope_name):
        """Enter a new scope."""
        self.scopes.append(scope_name)
        self.current_scope = scope_name
    
    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope = self.scopes[-1]
    
    def add_symbol(self, name, type_name, line, is_function=False, params=None):
        """Add a symbol to the table."""
        symbol = Symbol(name, type_name, self.current_scope, line, is_function, params)
        self.symbols.append(symbol)
        return symbol
    
    def lookup(self, name, scope=None):
        """Look up a symbol by name in the given scope or all visible scopes."""
        if scope:
            for symbol in self.symbols:
                if symbol.name == name and symbol.scope == scope:
                    return symbol
        else:
            # Search in current scope first, then global
            for symbol in self.symbols:
                if symbol.name == name and symbol.scope == self.current_scope:
                    return symbol
            
            # If not found in current scope, look in global scope
            for symbol in self.symbols:
                if symbol.name == name and symbol.scope == 'global':
                    return symbol
        
        return None
    
    def to_dataframe(self):
        """Convert the symbol table to a pandas DataFrame."""
        return pd.DataFrame([s.to_dict() for s in self.symbols])

class SemanticAnalyzer:
    """
    Semantic analyzer for C code. Checks for type errors, undeclared variables, etc.
    """
    
    def __init__(self):
        """Initialize the semantic analyzer."""
        self.symbol_table = SymbolTable()
        self.errors = []
        self.ast = None
        
        # Add built-in types
        self.types = {'int', 'char', 'float', 'double', 'void', 'short', 'long', 'unsigned', 'signed'}
        
        # Add built-in functions
        self.symbol_table.add_symbol('printf', 'function', 0, True, ['format', '...'])
        self.symbol_table.add_symbol('scanf', 'function', 0, True, ['format', '...'])
        self.symbol_table.add_symbol('malloc', 'void*', 0, True, ['size_t'])
        self.symbol_table.add_symbol('free', 'void', 0, True, ['void*'])
    
    def analyze(self, ast):
        """
        Analyze the AST for semantic errors.
        Returns a dictionary with symbol table and error information.
        """
        if not ast:
            return {
                'success': False,
                'error': "No AST to analyze. Syntax analysis may have failed.",
                'errors': []
            }
        
        self.ast = ast
        self.errors = []
        
        # Reset symbol table
        self.symbol_table = SymbolTable()
        
        # Add built-in functions
        self.symbol_table.add_symbol('printf', 'function', 0, True, ['format', '...'])
        self.symbol_table.add_symbol('scanf', 'function', 0, True, ['format', '...'])
        self.symbol_table.add_symbol('malloc', 'void*', 0, True, ['size_t'])
        self.symbol_table.add_symbol('free', 'void', 0, True, ['void*'])
        
        # Traverse the AST
        self._traverse_ast(ast)
        
        # Check for unused variables
        self._check_unused_variables()
        
        success = len(self.errors) == 0
        
        # Convert symbol table to a format suitable for visualization
        symbol_table_data = self.symbol_table.to_dataframe().to_dict('records')
        
        return {
            'success': success,
            'symbol_table': format_symbol_table(symbol_table_data),
            'errors': format_errors(self.errors),
            'raw_symbol_table': symbol_table_data
        }
    
    def _traverse_ast(self, node, parent=None):
        """Recursively traverse the AST and perform semantic analysis."""
        if not node:
            return
        
        node_type = node.get('type', '')
        
        # Handle different node types
        if node_type == 'translation_unit':
            self._process_translation_unit(node)
        elif node_type == 'function_definition':
            self._process_function_definition(node)
        elif node_type == 'declaration':
            self._process_declaration(node)
        elif node_type == 'compound_statement':
            # Enter a new scope for the compound statement
            scope_name = f"block_{id(node)}"
            self.symbol_table.enter_scope(scope_name)
            self._process_compound_statement(node)
            self.symbol_table.exit_scope()
        elif node_type == 'expression_statement':
            self._process_expression_statement(node)
        elif node_type == 'selection_statement':
            self._process_selection_statement(node)
        elif node_type == 'iteration_statement':
            self._process_iteration_statement(node)
        elif node_type == 'jump_statement':
            self._process_jump_statement(node)
        elif node_type in ('expression', 'assignment_expression', 'conditional_expression',
                         'logical_or_expression', 'logical_and_expression', 'inclusive_or_expression',
                         'exclusive_or_expression', 'and_expression', 'equality_expression',
                         'relational_expression', 'shift_expression', 'additive_expression',
                         'multiplicative_expression', 'cast_expression', 'unary_expression',
                         'postfix_expression', 'primary_expression'):
            self._process_expression(node)
        
        # Process children recursively
        children = node.get('children', [])
        for child in children:
            self._traverse_ast(child, node)
    
    def _process_translation_unit(self, node):
        """Process the translation unit (top-level node)."""
        pass  # Just traverse children
    
    def _process_function_definition(self, node):
        """Process a function definition and add it to the symbol table."""
        # Extract function name and return type
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be declaration_specifiers (return type)
        # Second child should be declarator (function name and parameters)
        
        # Extract return type
        return_type = self._extract_type(children[0])
        
        # Extract function name and parameters
        func_info = self._extract_function_info(children[1])
        if not func_info:
            return
        
        func_name, params = func_info
        
        # Check if function already exists
        existing_func = self.symbol_table.lookup(func_name)
        if existing_func and existing_func.is_function:
            self.errors.append({
                'type': 'semantic',
                'message': f"Function '{func_name}' already defined",
                'line': node.get('line', 0)
            })
            return
        
        # Add function to symbol table
        self.symbol_table.add_symbol(func_name, return_type, node.get('line', 0), True, params)
        
        # Enter function scope
        self.symbol_table.enter_scope(func_name)
        
        # Add parameters to symbol table in function scope
        for param_name, param_type in params:
            self.symbol_table.add_symbol(param_name, param_type, node.get('line', 0))
        
        # Process function body
        if len(children) > 2:
            self._traverse_ast(children[2])
        
        # Exit function scope
        self.symbol_table.exit_scope()
    
    def _extract_type(self, node):
        """Extract the type from a declaration_specifiers node."""
        if not node:
            return 'unknown'
        
        # Simple extraction for demo purposes
        # In a full compiler, this would be more complex
        type_specifiers = []
        self._collect_type_specifiers(node, type_specifiers)
        
        if not type_specifiers:
            return 'int'  # Default to int if no type specified
        
        # Join the type specifiers in order
        return ' '.join(type_specifiers)
    
    def _collect_type_specifiers(self, node, type_specifiers):
        """Collect all type specifiers from a declaration_specifiers node."""
        if not node:
            return
        
        node_type = node.get('type', '')
        
        if node_type == 'type_specifier':
            leaf = node.get('value', '')
            if leaf:
                type_specifiers.append(leaf)
        
        # Check children
        children = node.get('children', [])
        for child in children:
            self._collect_type_specifiers(child, type_specifiers)
    
    def _extract_function_info(self, node):
        """Extract function name and parameters from a declarator node."""
        if not node:
            return None
        
        # Navigate through the AST to find the function name and parameters
        # This is a simplified version; a real implementation would be more robust
        
        func_name = None
        params = []
        
        # Find direct_declarator with function call
        def find_func_info(n):
            nonlocal func_name, params
            
            if not n:
                return
            
            n_type = n.get('type', '')
            children = n.get('children', [])
            
            if n_type == 'direct_declarator':
                # Check if it's a function declarator
                if len(children) >= 2:
                    for i, child in enumerate(children):
                        if i == 0 and child.get('type') == 'id':
                            func_name = child.get('value', '')
                        elif child.get('type') == 'parameter_type_list':
                            # Extract parameters
                            self._extract_parameters(child, params)
            
            # Check children
            for child in children:
                find_func_info(child)
        
        find_func_info(node)
        
        if not func_name:
            return None
        
        return func_name, params
    
    def _extract_parameters(self, node, params):
        """Extract parameter names and types from a parameter_type_list node."""
        if not node:
            return
        
        node_type = node.get('type', '')
        children = node.get('children', [])
        
        if node_type == 'parameter_declaration':
            # First child should be declaration_specifiers (parameter type)
            # Second child should be declarator (parameter name)
            if len(children) >= 2:
                param_type = self._extract_type(children[0])
                param_name = self._extract_identifier(children[1])
                if param_name:
                    params.append((param_name, param_type))
        
        # Check children
        for child in children:
            self._extract_parameters(child, params)
    
    def _extract_identifier(self, node):
        """Extract an identifier name from a declarator node."""
        if not node:
            return None
        
        # Navigate through the AST to find the identifier
        # This is a simplified version; a real implementation would be more robust
        
        id_name = None
        
        def find_id(n):
            nonlocal id_name
            
            if not n:
                return
            
            n_type = n.get('type', '')
            
            if n_type == 'id':
                id_name = n.get('value', '')
                return
            
            # Check children
            children = n.get('children', [])
            for child in children:
                find_id(child)
        
        find_id(node)
        
        return id_name
    
    def _process_declaration(self, node):
        """Process a variable declaration and add it to the symbol table."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be declaration_specifiers (variable type)
        var_type = self._extract_type(children[0])
        
        # Second child should be init_declarator_list (variable names and initializers)
        self._process_init_declarator_list(children[1], var_type, node.get('line', 0))
    
    def _process_init_declarator_list(self, node, var_type, line):
        """Process an init_declarator_list node."""
        if not node:
            return
        
        node_type = node.get('type', '')
        children = node.get('children', [])
        
        if node_type == 'init_declarator':
            # First child should be declarator (variable name)
            var_name = self._extract_identifier(children[0])
            if var_name:
                # Check if variable already exists in current scope
                existing_var = self.symbol_table.lookup(var_name, self.symbol_table.current_scope)
                if existing_var:
                    self.errors.append({
                        'type': 'semantic',
                        'message': f"Variable '{var_name}' already declared in this scope",
                        'line': line
                    })
                else:
                    # Add variable to symbol table
                    self.symbol_table.add_symbol(var_name, var_type, line)
                
                # If there's an initializer (assignment), check it
                if len(children) > 1:
                    self._check_initializer(children[1], var_type, line)
        
        # Check all children recursively
        for child in children:
            self._process_init_declarator_list(child, var_type, line)
    
    def _check_initializer(self, node, var_type, line):
        """Check if an initializer is compatible with the variable type."""
        # In a real compiler, this would check type compatibility
        pass  # Simplified for this demo
    
    def _process_compound_statement(self, node):
        """Process a compound statement (block)."""
        # Just traverse children (declarations and statements)
        pass
    
    def _process_expression_statement(self, node):
        """Process an expression statement."""
        children = node.get('children', [])
        if not children:
            return
        
        # Process the expression
        self._process_expression(children[0])
    
    def _process_selection_statement(self, node):
        """Process an if or switch statement."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be 'if', 'if_else', or 'switch'
        stmt_type = children[0].get('value', '')
        
        if stmt_type in ('if', 'if_else', 'switch'):
            # Second child is the condition expression
            self._process_expression(children[1])
            
            # Third child is the 'then' statement
            if len(children) > 2:
                self._traverse_ast(children[2])
            
            # Fourth child is the 'else' statement (for if_else)
            if len(children) > 3 and stmt_type == 'if_else':
                self._traverse_ast(children[3])
    
    def _process_iteration_statement(self, node):
        """Process a loop statement (while, do-while, for)."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be 'while', 'do_while', or 'for'
        stmt_type = children[0].get('value', '')
        
        if stmt_type == 'while':
            # Second child is the condition expression
            self._process_expression(children[1])
            
            # Third child is the loop body
            if len(children) > 2:
                self._traverse_ast(children[2])
        
        elif stmt_type == 'do_while':
            # Second child is the loop body
            if len(children) > 1:
                self._traverse_ast(children[1])
            
            # Third child is the condition expression
            if len(children) > 2:
                self._process_expression(children[2])
        
        elif stmt_type == 'for':
            # Second child is the initialization
            if len(children) > 1:
                self._traverse_ast(children[1])
            
            # Third child is the condition
            if len(children) > 2:
                self._traverse_ast(children[2])
            
            # Fourth child is the increment
            if len(children) > 3:
                self._traverse_ast(children[3])
            
            # Fifth child is the loop body
            if len(children) > 4:
                self._traverse_ast(children[4])
    
    def _process_jump_statement(self, node):
        """Process a jump statement (return, break, continue, goto)."""
        children = node.get('children', [])
        if not children:
            return
        
        # First child should be 'return', 'break', 'continue', or 'goto'
        stmt_type = children[0].get('value', '')
        
        if stmt_type == 'return':
            # Second child is the return expression (if any)
            if len(children) > 1:
                self._process_expression(children[1])
                
                # TODO: Check if return type matches function return type
        
        elif stmt_type == 'goto':
            # Second child is the label name
            if len(children) > 1:
                label_name = children[1].get('value', '')
                # TODO: Check if label exists
    
    def _process_expression(self, node):
        """Process an expression node."""
        if not node:
            return
        
        node_type = node.get('type', '')
        children = node.get('children', [])
        
        # Handle different expression types
        if node_type == 'primary_expression':
            if children and children[0].get('type') == 'id':
                # Check if variable is declared
                var_name = children[0].get('value', '')
                symbol = self.symbol_table.lookup(var_name)
                if not symbol:
                    self.errors.append({
                        'type': 'semantic',
                        'message': f"Undeclared variable '{var_name}'",
                        'line': node.get('line', 0)
                    })
                elif symbol:
                    # Mark as used
                    symbol.used = True
        
        elif node_type == 'postfix_expression':
            leaf = node.get('value', '')
            if leaf == 'function_call':
                # First child is the function name
                if children and children[0].get('type') == 'postfix_expression':
                    func_node = children[0].get('children', [])[0]
                    if func_node and func_node.get('type') == 'primary_expression':
                        id_node = func_node.get('children', [])[0]
                        if id_node and id_node.get('type') == 'id':
                            func_name = id_node.get('value', '')
                            # Check if function is declared
                            symbol = self.symbol_table.lookup(func_name)
                            if not symbol:
                                self.errors.append({
                                    'type': 'semantic',
                                    'message': f"Undeclared function '{func_name}'",
                                    'line': node.get('line', 0)
                                })
                            elif not symbol.is_function:
                                self.errors.append({
                                    'type': 'semantic',
                                    'message': f"'{func_name}' is not a function",
                                    'line': node.get('line', 0)
                                })
                            else:
                                # Mark as used
                                symbol.used = True
                                
                                # TODO: Check parameter count and types
        
        # Process children recursively
        for child in children:
            self._process_expression(child)
    
    def _check_unused_variables(self):
        """Check for unused variables in the symbol table."""
        for symbol in self.symbol_table.symbols:
            if not symbol.is_function and not symbol.used:
                self.errors.append({
                    'type': 'warning',
                    'message': f"Unused variable '{symbol.name}'",
                    'line': symbol.line
                })
