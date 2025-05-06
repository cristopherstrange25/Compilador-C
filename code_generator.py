class CodeGenerator:
    """
    Code generator for C code.
    Converts intermediate code to target machine code.
    """
    
    def __init__(self, intermediate_code, target_architecture='x86'):
        self.intermediate_code = intermediate_code
        self.target_architecture = target_architecture
        self.generated_code = []
        self.errors = []
        
        # Map of registers for different architectures
        self.registers = {
            'x86': ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi'],
            'x86_64': ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'],
            'ARM': ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'lr']
        }
        
        # Map of instruction templates for different architectures
        self.instruction_templates = {
            'x86': {
                'ASSIGN': 'mov {dest}, {src}',
                'ADD': 'add {dest}, {src}',
                'SUB': 'sub {dest}, {src}',
                'MUL': 'imul {dest}, {src}',
                'DIV': 'mov eax, {left}\n\tidiv {right}\n\tmov {dest}, eax',
                'MOD': 'mov eax, {left}\n\tidiv {right}\n\tmov {dest}, edx',
                'AND': 'and {dest}, {src}',
                'OR': 'or {dest}, {src}',
                'XOR': 'xor {dest}, {src}',
                'NOT': 'not {dest}',
                'CMP': 'cmp {left}, {right}',
                'JMP': 'jmp {label}',
                'JE': 'je {label}',
                'JNE': 'jne {label}',
                'JG': 'jg {label}',
                'JGE': 'jge {label}',
                'JL': 'jl {label}',
                'JLE': 'jle {label}',
                'CALL': 'call {func}',
                'RET': 'ret',
                'PUSH': 'push {src}',
                'POP': 'pop {dest}'
            },
            'x86_64': {
                # Similar to x86 but with 64-bit register names
                'ASSIGN': 'mov {dest}, {src}',
                'ADD': 'add {dest}, {src}',
                'SUB': 'sub {dest}, {src}',
                'MUL': 'imul {dest}, {src}',
                'DIV': 'mov rax, {left}\n\tidiv {right}\n\tmov {dest}, rax',
                'MOD': 'mov rax, {left}\n\tidiv {right}\n\tmov {dest}, rdx',
                'AND': 'and {dest}, {src}',
                'OR': 'or {dest}, {src}',
                'XOR': 'xor {dest}, {src}',
                'NOT': 'not {dest}',
                'CMP': 'cmp {left}, {right}',
                'JMP': 'jmp {label}',
                'JE': 'je {label}',
                'JNE': 'jne {label}',
                'JG': 'jg {label}',
                'JGE': 'jge {label}',
                'JL': 'jl {label}',
                'JLE': 'jle {label}',
                'CALL': 'call {func}',
                'RET': 'ret',
                'PUSH': 'push {src}',
                'POP': 'pop {dest}'
            },
            'ARM': {
                'ASSIGN': 'mov {dest}, {src}',
                'ADD': 'add {dest}, {dest}, {src}',
                'SUB': 'sub {dest}, {dest}, {src}',
                'MUL': 'mul {dest}, {dest}, {src}',
                'DIV': 'sdiv {dest}, {left}, {right}',
                'AND': 'and {dest}, {dest}, {src}',
                'OR': 'orr {dest}, {dest}, {src}',
                'XOR': 'eor {dest}, {dest}, {src}',
                'NOT': 'mvn {dest}, {src}',
                'CMP': 'cmp {left}, {right}',
                'JMP': 'b {label}',
                'JE': 'beq {label}',
                'JNE': 'bne {label}',
                'JG': 'bgt {label}',
                'JGE': 'bge {label}',
                'JL': 'blt {label}',
                'JLE': 'ble {label}',
                'CALL': 'bl {func}',
                'RET': 'bx lr',
                'PUSH': 'push {src}',
                'POP': 'pop {dest}'
            }
        }
        
        # Initialize register allocation table
        self.register_allocation = {}
        self.available_registers = self.registers.get(target_architecture, [])
        self.stack_vars = {}
        self.stack_offset = 0
    
    def generate(self):
        """
        Generate target architecture code from intermediate code.
        
        Returns:
            tuple: (generated_code, errors) where generated_code is the assembly code
                  and errors is a list of error messages.
        """
        # Reset
        self.generated_code = []
        self.errors = []
        self.register_allocation = {}
        self.available_registers = self.registers.get(self.target_architecture, [])
        self.stack_vars = {}
        self.stack_offset = 0
        
        # Get instruction templates for target architecture
        templates = self.instruction_templates.get(self.target_architecture, {})
        if not templates:
            self.errors.append(f"Unsupported target architecture: {self.target_architecture}")
            return "", self.errors
        
        # Add code header
        self._add_code_header()
        
        # Process each line of intermediate code
        lines = self.intermediate_code.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                self.generated_code.append(f"; {line}" if line else "")
                continue
            
            # Process different intermediate code instructions
            if '=' in line and not line.startswith('IF'):
                self._process_assignment(line, templates)
            elif line.startswith('IF'):
                self._process_conditional_jump(line, templates)
            elif line.startswith('GOTO'):
                self._process_unconditional_jump(line, templates)
            elif line.startswith('LABEL'):
                self._process_label(line)
            elif line.startswith('FUNC_BEGIN'):
                self._process_function_begin(line, templates)
            elif line.startswith('FUNC_END'):
                self._process_function_end(line, templates)
            elif line.startswith('PARAM'):
                self._process_parameter(line, templates)
            elif line.startswith('CALL'):
                self._process_function_call(line, templates)
            elif line.startswith('DECL'):
                self._process_declaration(line)
            else:
                # Unrecognized instruction
                self.generated_code.append(f"; Unrecognized: {line}")
        
        # Add code footer
        self._add_code_footer()
        
        # Join all lines into a single string
        generated_code = '\n'.join(self.generated_code)
        return generated_code, self.errors
    
    def _add_code_header(self):
        """Add architecture-specific code header."""
        if self.target_architecture == 'x86':
            self.generated_code.extend([
                "; x86 Assembly Code",
                "section .text",
                "global _start",
                "",
                "_start:"
            ])
        elif self.target_architecture == 'x86_64':
            self.generated_code.extend([
                "; x86_64 Assembly Code",
                "section .text",
                "global _start",
                "",
                "_start:"
            ])
        elif self.target_architecture == 'ARM':
            self.generated_code.extend([
                "; ARM Assembly Code",
                ".text",
                ".global _start",
                "",
                "_start:"
            ])
    
    def _add_code_footer(self):
        """Add architecture-specific code footer."""
        if self.target_architecture in ['x86', 'x86_64']:
            self.generated_code.extend([
                "",
                "; Exit program",
                "mov eax, 1        ; System call number for exit",
                "xor ebx, ebx      ; Exit code 0",
                "int 0x80          ; Call kernel"
            ])
        elif self.target_architecture == 'ARM':
            self.generated_code.extend([
                "",
                "; Exit program",
                "mov r0, #0        ; Exit code 0",
                "mov r7, #1        ; System call number for exit",
                "svc 0             ; Call kernel"
            ])
    
    def _process_assignment(self, line, templates):
        """Process assignment statements."""
        parts = line.split('=', 1)
        if len(parts) != 2:
            self.errors.append(f"Invalid assignment: {line}")
            return
        
        dest = parts[0].strip()
        src = parts[1].strip()
        
        # Check for arithmetic operations
        if '+' in src:
            self._process_addition(dest, src, templates)
        elif '-' in src and not src.startswith('-'):  # Avoid unary minus
            self._process_subtraction(dest, src, templates)
        elif '*' in src:
            self._process_multiplication(dest, src, templates)
        elif '/' in src:
            self._process_division(dest, src, templates)
        elif '&&' in src:
            self._process_logical_and(dest, src, templates)
        elif '||' in src:
            self._process_logical_or(dest, src, templates)
        elif '==' in src:
            self._process_comparison(dest, src, '==', templates)
        elif '!=' in src:
            self._process_comparison(dest, src, '!=', templates)
        elif '<' in src and not '<=' in src:
            self._process_comparison(dest, src, '<', templates)
        elif '>' in src and not '>=' in src:
            self._process_comparison(dest, src, '>', templates)
        elif '<=' in src:
            self._process_comparison(dest, src, '<=', templates)
        elif '>=' in src:
            self._process_comparison(dest, src, '>=', templates)
        else:
            # Simple assignment
            dest_reg = self._get_register(dest)
            
            # Check if src is a variable or a constant
            if src.isdigit() or (src.startswith('-') and src[1:].isdigit()):
                # It's a constant
                self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=src)}")
            else:
                # It's a variable or expression
                src_reg = self._get_register(src)
                self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=src_reg)}")
    
    def _process_addition(self, dest, src, templates):
        """Process addition operation."""
        parts = src.split('+')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        
        # Handle constant right operand
        if right.isdigit():
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Add constant to destination
            self.generated_code.append(f"\t{templates['ADD'].format(dest=dest_reg, src=right)}")
        else:
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Add right operand (from register)
            right_reg = self._get_register(right)
            self.generated_code.append(f"\t{templates['ADD'].format(dest=dest_reg, src=right_reg)}")
    
    def _process_subtraction(self, dest, src, templates):
        """Process subtraction operation."""
        parts = src.split('-')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        
        # Handle constant right operand
        if right.isdigit():
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Subtract constant from destination
            self.generated_code.append(f"\t{templates['SUB'].format(dest=dest_reg, src=right)}")
        else:
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Subtract right operand (from register)
            right_reg = self._get_register(right)
            self.generated_code.append(f"\t{templates['SUB'].format(dest=dest_reg, src=right_reg)}")
    
    def _process_multiplication(self, dest, src, templates):
        """Process multiplication operation."""
        parts = src.split('*')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        
        # Handle constant right operand
        if right.isdigit():
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Multiply destination by constant
            self.generated_code.append(f"\t{templates['MUL'].format(dest=dest_reg, src=right)}")
        else:
            # Load left operand into destination register
            self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
            # Multiply by right operand (from register)
            right_reg = self._get_register(right)
            self.generated_code.append(f"\t{templates['MUL'].format(dest=dest_reg, src=right_reg)}")
    
    def _process_division(self, dest, src, templates):
        """Process division operation."""
        parts = src.split('/')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        
        # Division is special on x86/x86_64 (uses eax/edx or rax/rdx)
        if self.target_architecture in ['x86', 'x86_64']:
            if right.isdigit():
                self.generated_code.append(f"\tmov eax, {left_reg}")
                self.generated_code.append(f"\tmov edx, 0")
                self.generated_code.append(f"\tmov ecx, {right}")
                self.generated_code.append(f"\tidiv ecx")
                self.generated_code.append(f"\tmov {dest_reg}, eax")
            else:
                right_reg = self._get_register(right)
                self.generated_code.append(f"\tmov eax, {left_reg}")
                self.generated_code.append(f"\tmov edx, 0")
                self.generated_code.append(f"\tidiv {right_reg}")
                self.generated_code.append(f"\tmov {dest_reg}, eax")
        else:
            # ARM has a direct division instruction
            right_reg = self._get_register(right) if not right.isdigit() else right
            left_reg = self._get_register(left)
            self.generated_code.append(f"\t{templates['DIV'].format(dest=dest_reg, left=left_reg, right=right_reg)}")
    
    def _process_logical_and(self, dest, src, templates):
        """Process logical AND operation."""
        parts = src.split('&&')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        right_reg = self._get_register(right)
        
        # Compute logical AND
        self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
        self.generated_code.append(f"\t{templates['AND'].format(dest=dest_reg, src=right_reg)}")
    
    def _process_logical_or(self, dest, src, templates):
        """Process logical OR operation."""
        parts = src.split('||')
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        right_reg = self._get_register(right)
        
        # Compute logical OR
        self.generated_code.append(f"\t{templates['ASSIGN'].format(dest=dest_reg, src=left_reg)}")
        self.generated_code.append(f"\t{templates['OR'].format(dest=dest_reg, src=right_reg)}")
    
    def _process_comparison(self, dest, src, op, templates):
        """Process comparison operations."""
        parts = src.split(op)
        left = parts[0].strip()
        right = parts[1].strip()
        
        dest_reg = self._get_register(dest)
        left_reg = self._get_register(left)
        
        if self.target_architecture in ['x86', 'x86_64']:
            # x86 comparison and conditional move
            if right.isdigit():
                self.generated_code.append(f"\t{templates['CMP'].format(left=left_reg, right=right)}")
            else:
                right_reg = self._get_register(right)
                self.generated_code.append(f"\t{templates['CMP'].format(left=left_reg, right=right_reg)}")
            
            # Set result based on comparison
            self.generated_code.append(f"\tmov {dest_reg}, 0")
            
            # Use conditional move based on comparison operator
            if op == '==':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmove {dest_reg}, ecx")
            elif op == '!=':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmovne {dest_reg}, ecx")
            elif op == '<':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmovl {dest_reg}, ecx")
            elif op == '<=':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmovle {dest_reg}, ecx")
            elif op == '>':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmovg {dest_reg}, ecx")
            elif op == '>=':
                self.generated_code.append(f"\tmov ecx, 1")
                self.generated_code.append(f"\tcmovge {dest_reg}, ecx")
        else:
            # ARM comparison
            if right.isdigit():
                self.generated_code.append(f"\t{templates['CMP'].format(left=left_reg, right=right)}")
            else:
                right_reg = self._get_register(right)
                self.generated_code.append(f"\t{templates['CMP'].format(left=left_reg, right=right_reg)}")
            
            # Set result based on comparison
            self.generated_code.append(f"\tmov {dest_reg}, #0")
            
            # Use conditional move based on comparison operator
            if op == '==':
                self.generated_code.append(f"\tmoveq {dest_reg}, #1")
            elif op == '!=':
                self.generated_code.append(f"\tmovne {dest_reg}, #1")
            elif op == '<':
                self.generated_code.append(f"\tmovlt {dest_reg}, #1")
            elif op == '<=':
                self.generated_code.append(f"\tmovle {dest_reg}, #1")
            elif op == '>':
                self.generated_code.append(f"\tmovgt {dest_reg}, #1")
            elif op == '>=':
                self.generated_code.append(f"\tmovge {dest_reg}, #1")
    
    def _process_conditional_jump(self, line, templates):
        """Process conditional jump instructions."""
        # Example: IF !t0 GOTO L1
        parts = line.split()
        if len(parts) < 3 or parts[0] != 'IF' or 'GOTO' not in line:
            self.errors.append(f"Invalid conditional jump: {line}")
            return
        
        # Get condition and label
        condition = parts[1]
        label_index = parts.index('GOTO')
        label = parts[label_index + 1] if label_index + 1 < len(parts) else ""
        
        if not label:
            self.errors.append(f"Missing label in conditional jump: {line}")
            return
        
        # Check if it's a negated condition
        is_negated = condition.startswith('!')
        if is_negated:
            condition = condition[1:]
        
        # Generate code
        cond_reg = self._get_register(condition)
        
        if self.target_architecture in ['x86', 'x86_64']:
            # x86 style
            self.generated_code.append(f"\tcmp {cond_reg}, 0")
            if is_negated:
                self.generated_code.append(f"\tje {label}")
            else:
                self.generated_code.append(f"\tjne {label}")
        else:
            # ARM style
            self.generated_code.append(f"\tcmp {cond_reg}, #0")
            if is_negated:
                self.generated_code.append(f"\tbeq {label}")
            else:
                self.generated_code.append(f"\tbne {label}")
    
    def _process_unconditional_jump(self, line, templates):
        """Process unconditional jump instructions."""
        # Example: GOTO L1
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'GOTO':
            self.errors.append(f"Invalid unconditional jump: {line}")
            return
        
        label = parts[1]
        
        # Generate code
        if self.target_architecture in ['x86', 'x86_64']:
            self.generated_code.append(f"\tjmp {label}")
        else:
            # ARM
            self.generated_code.append(f"\tb {label}")
    
    def _process_label(self, line):
        """Process label definitions."""
        # Example: LABEL L1
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'LABEL':
            self.errors.append(f"Invalid label definition: {line}")
            return
        
        label = parts[1]
        
        # Generate code
        self.generated_code.append(f"{label}:")
    
    def _process_function_begin(self, line, templates):
        """Process function begin markers."""
        # Example: FUNC_BEGIN main
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'FUNC_BEGIN':
            self.errors.append(f"Invalid function begin: {line}")
            return
        
        func_name = parts[1]
        
        # Generate code
        self.generated_code.append(f"")
        self.generated_code.append(f"{func_name}:")
        
        # Save registers based on architecture
        if self.target_architecture in ['x86', 'x86_64']:
            self.generated_code.append(f"\tpush ebp")
            self.generated_code.append(f"\tmov ebp, esp")
            # Reserve space for local variables (placeholder)
            self.generated_code.append(f"\tsub esp, 16")
        else:
            # ARM
            self.generated_code.append(f"\tpush {{r4-r11, lr}}")
    
    def _process_function_end(self, line, templates):
        """Process function end markers."""
        # Example: FUNC_END main
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'FUNC_END':
            self.errors.append(f"Invalid function end: {line}")
            return
        
        func_name = parts[1]
        
        # Generate code - restore registers and return
        if self.target_architecture in ['x86', 'x86_64']:
            self.generated_code.append(f"\tmov esp, ebp")
            self.generated_code.append(f"\tpop ebp")
            self.generated_code.append(f"\tret")
        else:
            # ARM
            self.generated_code.append(f"\tpop {{r4-r11, pc}}")
    
    def _process_parameter(self, line, templates):
        """Process function parameters."""
        # Example: PARAM int a
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'PARAM':
            self.errors.append(f"Invalid parameter: {line}")
            return
        
        param = ' '.join(parts[1:])
        
        # In a real implementation, we would handle parameter access
        # For now, just add a comment
        self.generated_code.append(f"\t; Parameter: {param}")
    
    def _process_function_call(self, line, templates):
        """Process function calls."""
        # Example: CALL func
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'CALL':
            self.errors.append(f"Invalid function call: {line}")
            return
        
        func_name = parts[1]
        
        # Generate code
        if self.target_architecture in ['x86', 'x86_64']:
            self.generated_code.append(f"\tcall {func_name}")
        else:
            # ARM
            self.generated_code.append(f"\tbl {func_name}")
    
    def _process_declaration(self, line):
        """Process variable declarations."""
        # Example: DECL int a
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'DECL':
            self.errors.append(f"Invalid declaration: {line}")
            return
        
        var_decl = ' '.join(parts[1:])
        
        # Just add a comment for now
        self.generated_code.append(f"\t; Declaration: {var_decl}")
    
    def _get_register(self, var):
        """
        Allocate a register for a variable or return the assigned register.
        If no registers are available, simulate stack operations.
        
        Returns:
            str: The register name or memory reference
        """
        # If var is a literal value, return it as is
        if var.isdigit() or (var.startswith('-') and var[1:].isdigit()):
            return var
        
        # Check if var already has a register
        if var in self.register_allocation:
            return self.register_allocation[var]
        
        # Allocate a new register if available
        if self.available_registers:
            reg = self.available_registers.pop(0)
            self.register_allocation[var] = reg
            return reg
        
        # No registers available, use memory (stack)
        if var not in self.stack_vars:
            self.stack_offset += 4
            self.stack_vars[var] = self.stack_offset
        
        # Return memory reference based on architecture
        if self.target_architecture in ['x86', 'x86_64']:
            return f"[ebp-{self.stack_vars[var]}]"
        else:
            # ARM
            return f"[sp, #{self.stack_vars[var]}]"
