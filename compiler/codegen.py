"""
Code generator for C compiler.
Generates target machine code from optimized intermediate code.
"""

class CodeGenerator:
    """
    Code generator for C compiler.
    Converts optimized intermediate code to target machine code.
    For simplicity, generates x86-64 assembly code.
    """
    
    def __init__(self):
        """Initialize the code generator."""
        self.ir_code = []
        self.assembly_code = []
        self.errors = []
        self.registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']
        self.register_map = {}  # Maps variables to registers
        self.stack_vars = {}    # Maps variables to stack locations
        self.stack_offset = 0
    
    def generate(self, ir_code):
        """
        Generate target machine code from intermediate code.
        
        Args:
            ir_code: List of intermediate code instructions
            
        Returns:
            Dictionary with generated code and error information
        """
        if not ir_code:
            return {
                'success': False,
                'error': "No intermediate code to generate from.",
                'errors': []
            }
        
        # Reset state
        self.ir_code = ir_code
        self.assembly_code = []
        self.errors = []
        self.register_map = {}
        self.stack_vars = {}
        self.stack_offset = 0
        
        # Generate assembly prologue
        self._generate_prologue()
        
        # Convert each IR instruction to assembly
        for instr in self.ir_code:
            self._convert_instruction(instr)
        
        # Generate assembly epilogue
        self._generate_epilogue()
        
        success = len(self.errors) == 0
        
        return {
            'success': success,
            'assembly_code': self.assembly_code,
            'errors': self.errors,
            'register_allocation': self._get_register_allocation(),
            'stack_frame': self._get_stack_frame()
        }
    
    def _generate_prologue(self):
        """Generate assembly prologue."""
        self.assembly_code.extend([
            "; Generated x86-64 Assembly Code",
            ".intel_syntax noprefix",
            ".global main",
            "",
            ".text"
        ])
    
    def _generate_epilogue(self):
        """Generate assembly epilogue."""
        self.assembly_code.extend([
            "",
            "; End of generated code"
        ])
    
    def _convert_instruction(self, instr):
        """
        Convert an IR instruction to assembly.
        
        Args:
            instr: IR instruction as a string
        """
        instr_str = str(instr)
        self.assembly_code.append(f"; {instr_str}")
        
        if "LABEL" in instr_str:
            label = instr_str.split()[1]
            self.assembly_code.append(f"{label}:")
        
        elif "GOTO" in instr_str:
            label = instr_str.split()[1]
            self.assembly_code.append(f"    jmp {label}")
        
        elif "IF_FALSE_GOTO" in instr_str:
            parts = instr_str.split()
            label = parts[1]
            cond = parts[2]
            reg = self._get_register(cond)
            
            self.assembly_code.extend([
                f"    cmp {reg}, 0",
                f"    je {label}"
            ])
        
        elif "RETURN" in instr_str:
            parts = instr_str.split()
            if len(parts) > 1:
                value = parts[1]
                reg = self._get_register(value)
                self.assembly_code.append(f"    mov eax, {reg}")
            
            self.assembly_code.append("    ret")
        
        elif "=" in instr_str:
            # Handle assignment and operations
            parts = instr_str.split("=")
            result = parts[0].strip()
            expression = parts[1].strip()
            
            result_reg = self._allocate_register(result)
            
            if "+" in expression:
                operands = expression.split("+")
                left = operands[0].strip()
                right = operands[1].strip()
                
                left_reg = self._get_register(left)
                right_reg = self._get_register(right)
                
                self.assembly_code.extend([
                    f"    mov {result_reg}, {left_reg}",
                    f"    add {result_reg}, {right_reg}"
                ])
            
            elif "-" in expression:
                operands = expression.split("-")
                left = operands[0].strip()
                right = operands[1].strip()
                
                left_reg = self._get_register(left)
                right_reg = self._get_register(right)
                
                self.assembly_code.extend([
                    f"    mov {result_reg}, {left_reg}",
                    f"    sub {result_reg}, {right_reg}"
                ])
            
            elif "*" in expression:
                operands = expression.split("*")
                left = operands[0].strip()
                right = operands[1].strip()
                
                left_reg = self._get_register(left)
                right_reg = self._get_register(right)
                
                self.assembly_code.extend([
                    f"    mov {result_reg}, {left_reg}",
                    f"    imul {result_reg}, {right_reg}"
                ])
            
            elif "/" in expression:
                operands = expression.split("/")
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Division uses fixed registers in x86
                self.assembly_code.extend([
                    f"    mov eax, {self._get_register(left)}",
                    "    cdq",                            # Sign-extend EAX into EDX:EAX
                    f"    mov ecx, {self._get_register(right)}",
                    "    idiv ecx",                       # EDX:EAX / ECX -> EAX
                    f"    mov {result_reg}, eax"
                ])
            
            elif "CALL" in expression:
                parts = expression.split()
                func = parts[1].rstrip(',')
                args = int(parts[2]) if len(parts) > 2 else 0
                
                # In x86-64, arguments go in registers (rdi, rsi, rdx, rcx, r8, r9)
                # For simplicity, we're just calling the function directly
                self.assembly_code.append(f"    call {func}")
                self.assembly_code.append(f"    mov {result_reg}, eax")  # Return value in eax
            
            else:
                # Simple assignment
                if expression.isdigit():
                    self.assembly_code.append(f"    mov {result_reg}, {expression}")
                else:
                    src_reg = self._get_register(expression)
                    self.assembly_code.append(f"    mov {result_reg}, {src_reg}")
    
    def _allocate_register(self, var):
        """
        Allocate a register for a variable.
        
        Args:
            var: Variable name
            
        Returns:
            Register name
        """
        # If the variable is already in a register, use that
        if var in self.register_map:
            return self.register_map[var]
        
        # Try to find an unused register
        for reg in self.registers:
            if reg not in self.register_map.values():
                self.register_map[var] = reg
                return reg
        
        # If all registers are in use, spill one to memory
        victim = list(self.register_map.keys())[0]
        reg = self.register_map[victim]
        
        # Allocate stack space for the victim
        self.stack_offset += 4
        self.stack_vars[victim] = self.stack_offset
        
        # Store the victim on the stack
        self.assembly_code.append(f"    mov [rbp-{self.stack_offset}], {reg}")
        
        # Remove the victim from the register map
        del self.register_map[victim]
        
        # Allocate the register to the new variable
        self.register_map[var] = reg
        return reg
    
    def _get_register(self, var):
        """
        Get the register or memory location for a variable.
        
        Args:
            var: Variable name
            
        Returns:
            Register name or memory location
        """
        # If the variable is a constant, return it directly
        if var.isdigit() or var.startswith('"'):
            return var
        
        # If the variable is in a register, use that
        if var in self.register_map:
            return self.register_map[var]
        
        # If the variable is on the stack, load it into a register
        if var in self.stack_vars:
            reg = self._allocate_register(var)
            offset = self.stack_vars[var]
            self.assembly_code.append(f"    mov {reg}, [rbp-{offset}]")
            return reg
        
        # If the variable is not found, allocate a new register
        return self._allocate_register(var)
    
    def _get_register_allocation(self):
        """
        Get the current register allocation.
        
        Returns:
            Dictionary mapping variables to registers
        """
        return self.register_map.copy()
    
    def _get_stack_frame(self):
        """
        Get the current stack frame layout.
        
        Returns:
            Dictionary mapping variables to stack locations
        """
        return self.stack_vars.copy()
