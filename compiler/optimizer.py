"""
Code optimizer for C compiler.
Performs various optimization techniques on the intermediate code.
"""

class Optimizer:
    """
    Code optimizer for C compiler.
    Performs various optimization techniques on the intermediate code:
    - Constant folding and propagation
    - Dead code elimination
    - Common subexpression elimination
    - Loop optimization
    - Strength reduction
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self.ir_code = []
        self.optimized_code = []
        self.constant_map = {}  # Maps variables to their constant values
        self.expression_map = {}  # Maps expressions to their computed values
        self.used_variables = set()  # Set of variables that are used
        self.errors = []
    
    def optimize(self, ir_code):
        """
        Optimize the intermediate code.
        
        Args:
            ir_code: List of IR instructions
            
        Returns:
            Dictionary with optimization results
        """
        if not ir_code:
            return {
                'success': False,
                'error': "No intermediate code to optimize.",
                'errors': []
            }
        
        # Reset state
        self.ir_code = ir_code
        self.optimized_code = []
        self.constant_map = {}
        self.expression_map = {}
        self.used_variables = set()
        self.errors = []
        
        # Perform multiple optimization passes
        self._find_used_variables()
        self._constant_folding()
        self._constant_propagation()
        self._dead_code_elimination()
        self._common_subexpression_elimination()
        self._strength_reduction()
        
        success = len(self.errors) == 0
        
        # Prepare optimization details for visualization
        optimization_details = self._generate_optimization_details()
        
        return {
            'success': success,
            'optimized_code': self.optimized_code,
            'errors': self.errors,
            'original_code': self.ir_code,
            'optimization_details': optimization_details
        }
    
    def _find_used_variables(self):
        """Find all variables that are used in the code."""
        self.used_variables = set()
        
        for instr in self.ir_code:
            # Convert instruction to string if it's not already
            instr_str = str(instr)
            
            # Parse the instruction
            parts = instr_str.split()
            
            # Check for variable usage in right-hand side
            for i, part in enumerate(parts):
                if i > 0 and part not in ['=', '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 
                                          '&&', '||', '!', '&', '|', '^', '<<', '>>', 'GOTO', 'IF_FALSE_GOTO', 
                                          'LABEL', 'RETURN', 'PARAM', 'CALL'] and not part.isdigit() and not (part.startswith('"') and part.endswith('"')):
                    self.used_variables.add(part)
    
    def _constant_folding(self):
        """Perform constant folding optimization."""
        new_code = []
        
        for instr in self.ir_code:
            # Convert instruction to string if it's not already
            instr_str = str(instr)
            
            # Try to fold constants in the instruction
            folded_instr = self._fold_constants(instr_str)
            new_code.append(folded_instr)
        
        self.optimized_code = new_code
    
    def _fold_constants(self, instr):
        """
        Fold constants in an instruction.
        
        Args:
            instr: Instruction as a string
            
        Returns:
            Folded instruction as a string
        """
        # Simple constant folding implementation for demonstration
        # In a real compiler, this would be more sophisticated
        
        if ' + ' in instr and '=' in instr:
            parts = instr.split('=')
            if len(parts) == 2:
                lhs = parts[0].strip()
                expression = parts[1].strip()
                
                # Try to evaluate constant expressions
                try:
                    if '+' in expression:
                        operands = expression.split('+')
                        
                        # Check if both operands are numeric
                        if all(op.strip().isdigit() for op in operands):
                            result = sum(int(op.strip()) for op in operands)
                            return f"{lhs} = {result}"
                except:
                    pass
        
        return instr
    
    def _constant_propagation(self):
        """Perform constant propagation optimization."""
        # Find constant assignments
        for instr in self.optimized_code:
            instr_str = str(instr)
            
            # Check for constant assignments: var = constant
            if ' = ' in instr_str and not any(op in instr_str for op in ['+', '-', '*', '/', '%']):
                parts = instr_str.split(' = ')
                if len(parts) == 2:
                    var = parts[0].strip()
                    value = parts[1].strip()
                    
                    # If the value is a constant (numeric)
                    if value.isdigit():
                        self.constant_map[var] = value
        
        # Propagate constants
        new_code = []
        for instr in self.optimized_code:
            instr_str = str(instr)
            
            # Replace variables with their constant values
            for var, value in self.constant_map.items():
                # Don't replace in assignment to the same variable
                if instr_str.startswith(f"{var} ="):
                    continue
                
                # Replace occurrences of the variable with its constant value
                instr_str = instr_str.replace(f" {var} ", f" {value} ")
                instr_str = instr_str.replace(f" {var},", f" {value},")
                
                # Handle end of line
                if instr_str.endswith(f" {var}"):
                    instr_str = instr_str[:-len(var)] + value
            
            new_code.append(instr_str)
        
        self.optimized_code = new_code
    
    def _dead_code_elimination(self):
        """Perform dead code elimination optimization."""
        # Simple implementation for demonstration
        # Remove assignments to variables that are never used
        new_code = []
        
        for instr in self.optimized_code:
            instr_str = str(instr)
            
            # Check if this is an assignment
            if ' = ' in instr_str:
                parts = instr_str.split(' = ')
                var = parts[0].strip()
                
                # If the variable is never used, skip this instruction
                if var not in self.used_variables and not var.startswith('t'):
                    continue
            
            new_code.append(instr_str)
        
        self.optimized_code = new_code
    
    def _common_subexpression_elimination(self):
        """Perform common subexpression elimination optimization."""
        new_code = []
        self.expression_map = {}
        
        for instr in self.optimized_code:
            instr_str = str(instr)
            
            # Check if this is an assignment with an expression
            if ' = ' in instr_str and any(op in instr_str for op in ['+', '-', '*', '/', '%']):
                parts = instr_str.split(' = ')
                if len(parts) == 2:
                    var = parts[0].strip()
                    expression = parts[1].strip()
                    
                    # If we've seen this expression before, reuse the result
                    if expression in self.expression_map:
                        new_code.append(f"{var} = {self.expression_map[expression]}")
                        continue
                    
                    # Otherwise, record this expression
                    self.expression_map[expression] = var
            
            new_code.append(instr_str)
        
        self.optimized_code = new_code
    
    def _strength_reduction(self):
        """Perform strength reduction optimization."""
        new_code = []
        
        for instr in self.optimized_code:
            instr_str = str(instr)
            
            # Replace multiplication by 2 with addition
            if ' * ' in instr_str:
                parts = instr_str.split(' = ')
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    expression = parts[1].strip()
                    
                    if expression.endswith(' * 2'):
                        var = expression[:-4].strip()
                        new_code.append(f"{lhs} = {var} + {var}")
                        continue
            
            new_code.append(instr_str)
        
        self.optimized_code = new_code
    
    def _generate_optimization_details(self):
        """
        Generate details about the optimizations performed.
        
        Returns:
            Dictionary with optimization details
        """
        details = {
            'constant_folding': [],
            'constant_propagation': [],
            'dead_code_elimination': [],
            'common_subexpression_elimination': [],
            'strength_reduction': []
        }
        
        # Compare original and optimized code to identify optimizations
        original_set = set(self.ir_code)
        optimized_set = set(self.optimized_code)
        
        # Find removed and added instructions
        removed = original_set - optimized_set
        added = optimized_set - original_set
        
        # Classify optimizations (simplified for demonstration)
        for instr in removed:
            instr_str = str(instr)
            
            if ' * ' in instr_str and any(f"{var} + {var}" in str(new_instr) for new_instr in added for var in self.used_variables):
                details['strength_reduction'].append({
                    'original': instr_str,
                    'optimized': f"Replaced multiplication by 2 with addition"
                })
            elif ' = ' in instr_str and not any(var in instr_str for var in self.used_variables):
                details['dead_code_elimination'].append({
                    'original': instr_str,
                    'optimized': "Eliminated unused assignment"
                })
            elif any(op in instr_str for op in ['+', '-', '*', '/', '%']) and any(var in instr_str for var in self.constant_map):
                details['constant_propagation'].append({
                    'original': instr_str,
                    'optimized': "Propagated constant value"
                })
            elif any(op in instr_str for op in ['+', '-', '*', '/', '%']) and all(op.strip().isdigit() for op in instr_str.split('=')[1].split('+') if op.strip()):
                details['constant_folding'].append({
                    'original': instr_str,
                    'optimized': "Folded constant expression"
                })
            elif instr_str in self.expression_map:
                details['common_subexpression_elimination'].append({
                    'original': instr_str,
                    'optimized': f"Eliminated common subexpression: {self.expression_map[instr_str]}"
                })
        
        return details
