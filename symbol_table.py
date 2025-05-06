class SymbolTable:
    """
    Symbol table implementation for the C compiler.
    
    The symbol table stores information about identifiers (variables, functions, classes, etc.)
    including their names, types, scopes, and other attributes.
    """
    
    def __init__(self):
        """Initialize an empty symbol table."""
        self.symbols = []
        self.current_scope = "global"
        self.scope_stack = ["global"]
    
    def add_symbol(self, name, kind, data_type, scope=None, attributes=None):
        """
        Add a symbol to the symbol table.
        
        Args:
            name (str): The name of the symbol
            kind (str): The kind of symbol (variable, function, class, etc.)
            data_type (str): The data type of the symbol
            scope (str, optional): The scope of the symbol. Defaults to current scope.
            attributes (dict, optional): Additional attributes for the symbol. Defaults to None.
        
        Returns:
            bool: True if the symbol was added successfully, False if it already exists in the current scope
        """
        # Use current scope if none provided
        if scope is None:
            scope = self.current_scope
        
        # Check if symbol already exists in the specified scope
        if self.lookup(name, scope_only=scope):
            return False
        
        # Create the symbol entry
        symbol = {
            'name': name,
            'kind': kind,
            'data_type': data_type,
            'scope': scope,
        }
        
        # Add any additional attributes
        if attributes:
            symbol.update(attributes)
        
        # Add to the symbol table
        self.symbols.append(symbol)
        return True
    
    def lookup(self, name, scope_only=None):
        """
        Look up a symbol in the symbol table.
        
        Args:
            name (str): The name of the symbol to look up
            scope_only (str, optional): If provided, only look in this specific scope.
                                      Otherwise, follow scope chain.
        
        Returns:
            dict or None: The symbol entry if found, None otherwise
        """
        if scope_only:
            # Look only in the specified scope
            for symbol in self.symbols:
                if symbol['name'] == name and symbol['scope'] == scope_only:
                    return symbol
            return None
        else:
            # Start with current scope and follow scope chain
            for scope in reversed(self.scope_stack):
                for symbol in self.symbols:
                    if symbol['name'] == name and symbol['scope'] == scope:
                        return symbol
            return None
    
    def enter_scope(self, scope_name):
        """
        Enter a new scope.
        
        Args:
            scope_name (str): The name of the new scope
        """
        # Create a hierarchical scope name
        parent_scope = self.current_scope
        if parent_scope == "global":
            new_scope = scope_name
        else:
            new_scope = f"{parent_scope}.{scope_name}"
        
        # Update scope tracking
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
    
    def exit_scope(self):
        """
        Exit the current scope and return to the parent scope.
        
        Returns:
            str: The name of the scope that was exited
        """
        if len(self.scope_stack) > 1:
            exited_scope = self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
            return exited_scope
        else:
            # Can't exit global scope
            return None
    
    def get_symbols_in_scope(self, scope=None):
        """
        Get all symbols in a specific scope.
        
        Args:
            scope (str, optional): The scope to get symbols from. Defaults to current scope.
        
        Returns:
            list: A list of symbol entries in the specified scope
        """
        if scope is None:
            scope = self.current_scope
        
        return [symbol for symbol in self.symbols if symbol['scope'] == scope]
    
    def get_all_symbols(self):
        """
        Get all symbols in the symbol table.
        
        Returns:
            list: A list of all symbol entries
        """
        return self.symbols
    
    def update_symbol(self, name, scope=None, **attributes):
        """
        Update attributes of an existing symbol.
        
        Args:
            name (str): The name of the symbol to update
            scope (str, optional): The scope in which to find the symbol. Defaults to current scope.
            **attributes: Keyword arguments of attributes to update
        
        Returns:
            bool: True if the symbol was updated, False if it wasn't found
        """
        # Find the symbol
        symbol = self.lookup(name, scope_only=scope if scope else None)
        
        if symbol:
            # Update the attributes
            for key, value in attributes.items():
                symbol[key] = value
            return True
        
        return False
    
    def remove_symbol(self, name, scope=None):
        """
        Remove a symbol from the symbol table.
        
        Args:
            name (str): The name of the symbol to remove
            scope (str, optional): The scope in which to find the symbol. Defaults to current scope.
        
        Returns:
            bool: True if the symbol was removed, False if it wasn't found
        """
        if scope is None:
            scope = self.current_scope
        
        for i, symbol in enumerate(self.symbols):
            if symbol['name'] == name and symbol['scope'] == scope:
                self.symbols.pop(i)
                return True
        
        return False
    
    def clear(self):
        """Clear all symbols and reset to global scope."""
        self.symbols = []
        self.current_scope = "global"
        self.scope_stack = ["global"]
    
    def check_variable_initialization(self, name, scope=None):
        """
        Check if a variable has been initialized.
        
        Args:
            name (str): The name of the variable
            scope (str, optional): The scope in which to find the variable. Defaults to current scope.
        
        Returns:
            bool: True if the variable is initialized, False otherwise
        """
        symbol = self.lookup(name, scope_only=scope if scope else None)
        
        if symbol and symbol['kind'] == 'variable':
            return symbol.get('initialized', False)
        
        return False
    
    def mark_initialized(self, name, scope=None):
        """
        Mark a variable as initialized.
        
        Args:
            name (str): The name of the variable
            scope (str, optional): The scope in which to find the variable. Defaults to current scope.
        
        Returns:
            bool: True if the variable was marked as initialized, False if it wasn't found
        """
        return self.update_symbol(name, scope=scope, initialized=True)
    
    def get_function_parameters(self, func_name):
        """
        Get the parameters of a function.
        
        Args:
            func_name (str): The name of the function
        
        Returns:
            list or None: A list of parameter descriptions or None if the function wasn't found
        """
        symbol = self.lookup(func_name)
        
        if symbol and symbol['kind'] == 'function':
            return symbol.get('parameters', [])
        
        return None
    
    def add_function(self, name, return_type, parameters=None):
        """
        Add a function to the symbol table.
        
        Args:
            name (str): The name of the function
            return_type (str): The return type of the function
            parameters (list, optional): A list of parameter descriptions. Defaults to None.
        
        Returns:
            bool: True if the function was added successfully, False if it already exists
        """
        return self.add_symbol(
            name, 
            'function', 
            return_type, 
            attributes={'parameters': parameters or []}
        )
    
    def add_class(self, name, attributes=None, parent_classes=None):
        """
        Add a class to the symbol table.
        
        Args:
            name (str): The name of the class
            attributes (list, optional): A list of class attributes. Defaults to None.
            parent_classes (list, optional): A list of parent class names. Defaults to None.
        
        Returns:
            bool: True if the class was added successfully, False if it already exists
        """
        return self.add_symbol(
            name, 
            'class', 
            'class', 
            attributes={
                'attributes': attributes or [],
                'parent_classes': parent_classes or []
            }
        )
