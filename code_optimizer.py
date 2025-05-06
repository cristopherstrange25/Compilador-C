class CodeOptimizer:
    """
    Code optimizer for intermediate code.
    Performs various optimization techniques to improve code efficiency.
    """
    
    def __init__(self, intermediate_code, optimization_level=1):
        self.intermediate_code = intermediate_code
        self.optimization_level = optimization_level
        self.optimized_code = []
        self.optimizations_applied = []
    
    def optimize(self):
        """
        Optimize the intermediate code.
        
        Returns:
            tuple: (optimized_code, optimizations_applied) where optimized_code is the optimized intermediate code
                  and optimizations_applied is a list of optimization techniques applied.
        """
        # Start with the original code
        self.optimized_code = self.intermediate_code.split('\n')
        self.optimizations_applied = []
        
        # Apply optimizations based on the optimization level
        if self.optimization_level >= 1:
            self._constant_folding()
            self._remove_unreachable_code()
            self._eliminate_dead_code()
        
        if self.optimization_level >= 2:
            self._common_subexpression_elimination()
            self._constant_propagation()
            self._strength_reduction()
        
        if self.optimization_level >= 3:
            self._loop_optimization()
            self._tail_recursion_elimination()
        
        # Return the optimized code
        return '\n'.join(self.optimized_code), self.optimizations_applied
    
    def _constant_folding(self):
        """Perform constant folding optimization."""
        # Look for expressions with constant operands
        for i in range(len(self.optimized_code)):
            line = self.optimized_code[i]
            
            # Skip lines that don't contain assignments
            if '=' not in line or line.strip().startswith('#'):
                continue
            
            # Check for arithmetic operations with constant operands
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Check for constant arithmetic expressions
            try:
                # Look for simple arithmetic operations
                if any(op in rhs for op in ['+', '-', '*', '/', '%']) and \
                   not any(var.isalpha() for var in rhs.split() if var not in ['+', '-', '*', '/', '%', '(', ')']):
                    # Evaluate the expression
                    # Replace operators for eval
                    expr = rhs.replace('&&', ' and ').replace('||', ' or ')
                    result = eval(expr)
                    
                    # Replace the line with the folded constant
                    self.optimized_code[i] = f"{lhs} = {result}"
                    self.optimizations_applied.append(f"Constant folding: {rhs} -> {result}")
            except:
                # If evaluation fails, skip this line
                pass
    
    def _common_subexpression_elimination(self):
        """Eliminate common subexpressions."""
        expressions = {}
        
        # First pass: identify expressions
        for i in range(len(self.optimized_code)):
            line = self.optimized_code[i]
            
            # Skip lines that don't contain assignments
            if '=' not in line or line.strip().startswith('#') or line.strip().startswith('IF') or line.strip().startswith('GOTO'):
                continue
            
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Store the expression
            if rhs in expressions:
                # This is a common subexpression
                temp_var = expressions[rhs]
                # Replace the expression with the temporary variable
                self.optimized_code[i] = f"{lhs} = {temp_var}"
                self.optimizations_applied.append(f"Common subexpression elimination: {rhs} -> {temp_var}")
            else:
                expressions[rhs] = lhs
    
    def _remove_unreachable_code(self):
        """Remove unreachable code after unconditional jumps."""
        i = 0
        while i < len(self.optimized_code):
            line = self.optimized_code[i]
            
            # Check for unconditional jumps
            if line.strip().startswith('GOTO') and not line.strip().startswith('IF'):
                # Find the next label
                j = i + 1
                while j < len(self.optimized_code):
                    next_line = self.optimized_code[j]
                    if next_line.strip().startswith('LABEL'):
                        break
                    # Remove unreachable code
                    self.optimized_code[j] = f"# REMOVED (UNREACHABLE): {next_line}"
                    self.optimizations_applied.append(f"Removed unreachable code after GOTO")
                    j += 1
                i = j
            else:
                i += 1
    
    def _eliminate_dead_code(self):
        """Eliminate code that has no effect on the program output."""
        # Find assignments to variables that are never used
        used_vars = set()
        assigned_vars = {}
        
        # First pass: find all variable uses
        for i, line in enumerate(self.optimized_code):
            if '=' in line and not line.strip().startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    
                    # Record this assignment
                    if lhs not in assigned_vars:
                        assigned_vars[lhs] = []
                    assigned_vars[lhs].append(i)
                    
                    # Check for variables in rhs
                    for token in rhs.split():
                        if token.isalnum() and token.strip() and token[0].isalpha():
                            used_vars.add(token)
            
            # Check other lines for variable uses
            elif 'IF' in line:
                # Extract condition
                parts = line.split('IF', 1)
                if len(parts) > 1:
                    condition = parts[1].split('GOTO', 1)[0].strip()
                    # Check for variables in condition
                    for token in condition.split():
                        if token.isalnum() and token.strip() and token[0].isalpha():
                            used_vars.add(token)
        
        # Second pass: mark unused assignments
        for var, assignments in assigned_vars.items():
            if var not in used_vars:
                for i in assignments:
                    # This assignment is never used
                    self.optimized_code[i] = f"# REMOVED (DEAD CODE): {self.optimized_code[i]}"
                    self.optimizations_applied.append(f"Eliminated dead code: {var} is never used")
    
    def _constant_propagation(self):
        """Propagate constants through the code."""
        constants = {}
        
        for i in range(len(self.optimized_code)):
            line = self.optimized_code[i]
            
            # Skip lines that don't contain assignments
            if '=' not in line or line.strip().startswith('#'):
                continue
            
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Check if rhs is a simple constant
            if rhs.isdigit() or rhs.startswith('"') and rhs.endswith('"'):
                constants[lhs] = rhs
            
            # Apply constant propagation to this line
            for var, value in constants.items():
                # Replace variables with constants
                tokens = rhs.split()
                for j, token in enumerate(tokens):
                    if token == var:
                        tokens[j] = value
                
                new_rhs = ' '.join(tokens)
                if new_rhs != rhs:
                    self.optimized_code[i] = f"{lhs} = {new_rhs}"
                    self.optimizations_applied.append(f"Constant propagation: {var} -> {value}")
                    rhs = new_rhs
            
            # Check if the variable is no longer a constant after this line
            if lhs in constants and ('ASSIGN' in line or any(op in line for op in ['+', '-', '*', '/', '%'])):
                del constants[lhs]
    
    def _strength_reduction(self):
        """Reduce the strength of operations."""
        for i in range(len(self.optimized_code)):
            line = self.optimized_code[i]
            
            # Skip lines that don't contain assignments
            if '=' not in line or line.strip().startswith('#'):
                continue
            
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Replace multiplication by 2 with addition
            if ' * 2' in rhs:
                var = rhs.split(' * 2')[0].strip()
                self.optimized_code[i] = f"{lhs} = {var} + {var}"
                self.optimizations_applied.append(f"Strength reduction: {var} * 2 -> {var} + {var}")
            
            # Replace multiplication by power of 2 with shifts
            for power in range(1, 10):
                power_of_2 = 2 ** power
                if f" * {power_of_2}" in rhs:
                    var = rhs.split(f" * {power_of_2}")[0].strip()
                    self.optimized_code[i] = f"{lhs} = {var} << {power}"
                    self.optimizations_applied.append(f"Strength reduction: {var} * {power_of_2} -> {var} << {power}")
            
            # Replace division by power of 2 with shifts
            for power in range(1, 10):
                power_of_2 = 2 ** power
                if f" / {power_of_2}" in rhs:
                    var = rhs.split(f" / {power_of_2}")[0].strip()
                    self.optimized_code[i] = f"{lhs} = {var} >> {power}"
                    self.optimizations_applied.append(f"Strength reduction: {var} / {power_of_2} -> {var} >> {power}")
    
    def _loop_optimization(self):
        """Optimize loops in the code."""
        # Look for loop patterns
        i = 0
        while i < len(self.optimized_code):
            line = self.optimized_code[i]
            
            # Check for loop labels
            if line.strip().startswith('LABEL'):
                label = line.strip().split()[1]
                
                # Find the end of the loop (GOTO back to this label)
                loop_end = -1
                for j in range(i + 1, len(self.optimized_code)):
                    if self.optimized_code[j].strip() == f"GOTO {label}":
                        loop_end = j
                        break
                
                if loop_end != -1:
                    # We found a loop, look for invariant code
                    self._hoist_loop_invariants(i, loop_end, label)
                    self._loop_unrolling(i, loop_end, label)
            
            i += 1
    
    def _hoist_loop_invariants(self, loop_start, loop_end, label):
        """Hoist loop invariants out of the loop."""
        invariants = []
        
        # Identify loop invariants (code that doesn't change in the loop)
        for i in range(loop_start + 1, loop_end):
            line = self.optimized_code[i]
            
            # Skip lines that don't contain assignments
            if '=' not in line or line.strip().startswith('#'):
                continue
            
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Check if this expression is invariant
            invariant = True
            for j in range(loop_start + 1, loop_end):
                if j == i:
                    continue
                    
                other_line = self.optimized_code[j]
                # If this variable is modified elsewhere in the loop, it's not invariant
                if other_line.strip().startswith(lhs) and '=' in other_line:
                    invariant = False
                    break
                    
                # If any variable in the rhs is modified, this expression is not invariant
                for var in rhs.split():
                    if var.isalnum() and var.strip() and var[0].isalpha():
                        if other_line.strip().startswith(var) and '=' in other_line:
                            invariant = False
                            break
            
            if invariant:
                invariants.append(i)
        
        # Move invariants before the loop
        for i in sorted(invariants, reverse=True):
            invariant_line = self.optimized_code[i]
            self.optimized_code.insert(loop_start, invariant_line)
            self.optimized_code[i + 1] = f"# HOISTED: {invariant_line}"
            self.optimizations_applied.append(f"Loop invariant hoisting: {invariant_line.strip()}")
    
    def _loop_unrolling(self, loop_start, loop_end, label):
        """Unroll small loops with known iteration counts."""
        # This is a simplified unrolling that only works for very specific cases
        # In a real optimizer, this would be much more complex
        
        # Check if this is a simple counted loop
        for i in range(loop_start + 1, loop_end):
            line = self.optimized_code[i]
            
            # Look for loop counter increments
            if '+=' in line or '++' in line or '= i + 1' in line:
                # Check if this is a small loop (e.g., iterating < 3 times)
                # This is a very simplified check
                if any(cond for cond in self.optimized_code if f"i < 3" in cond or f"i <= 2" in cond):
                    # Unroll the loop
                    unrolled_code = []
                    
                    # Extract the loop body
                    loop_body = self.optimized_code[loop_start + 1:loop_end]
                    
                    # Unroll for 3 iterations (simplified example)
                    for iter_count in range(3):
                        for body_line in loop_body:
                            # Skip the increment and condition check in unrolled instances
                            if "GOTO" in body_line or "i +=" in body_line or "i = i + 1" in body_line:
                                continue
                            
                            # Replace 'i' with the actual value
                            unrolled_line = body_line.replace(" i ", f" {iter_count} ")
                            unrolled_line = unrolled_line.replace(" i,", f" {iter_count},")
                            unrolled_line = unrolled_line.replace(",i ", f",{iter_count} ")
                            unrolled_line = unrolled_line.replace("(i)", f"({iter_count})")
                            
                            unrolled_code.append(unrolled_line)
                    
                    # Replace the loop with unrolled code
                    self.optimized_code[loop_start:loop_end + 1] = unrolled_code
                    self.optimizations_applied.append("Loop unrolling applied")
                    
                    return  # Only handle one unrolling per call
    
    def _tail_recursion_elimination(self):
        """Eliminate tail recursion in functions."""
        # This is a complex optimization that would require more detailed analysis
        # For this implementation, we'll look for a very specific pattern
        
        # Find function beginnings
        for i in range(len(self.optimized_code)):
            line = self.optimized_code[i]
            
            if line.strip().startswith('FUNC_BEGIN'):
                func_name = line.strip().split()[1]
                
                # Find function end
                func_end = -1
                for j in range(i + 1, len(self.optimized_code)):
                    if self.optimized_code[j].strip() == f"FUNC_END {func_name}":
                        func_end = j
                        break
                
                if func_end != -1:
                    # Look for recursive calls just before return
                    for j in range(func_end - 1, i, -1):
                        line = self.optimized_code[j]
                        
                        if f"CALL {func_name}" in line:
                            # This is a potential tail-recursive call
                            # In a real implementation, we would convert this to a loop
                            self.optimized_code[j] = f"# TAIL-RECURSIVE CALL: {line}"
                            self.optimizations_applied.append(f"Identified tail recursion in {func_name}")
                            break
