class IRInstruction:
    """Class representing an IR instruction."""
    def __init__(self, opcode, result=None, arg1=None, arg2=None):
        self.opcode = opcode
        self.result = result
        self.arg1 = arg1
        self.arg2 = arg2
    
    def __str__(self):
        if self.opcode in ['LABEL', 'GOTO', 'IF_FALSE_GOTO', 'RETURN']:
            if self.arg1 is not None:
                return f"{self.opcode} {self.arg1}"
            return f"{self.opcode}"
        elif self.opcode in ['PARAM', 'CALL', 'ASSIGN']:
            if self.arg2 is not None:
                return f"{self.result} = {self.opcode} {self.arg1}, {self.arg2}"
            return f"{self.result} = {self.opcode} {self.arg1}"
        else:
            return f"{self.result} = {self.arg1} {self.opcode} {self.arg2}"
    
    def to_dict(self):
        """Convert the instruction to a dictionary."""
        return {
            'opcode': self.opcode,
            'result': self.result,
            'arg1': self.arg1,
            'arg2': self.arg2
        }

class BasicBlock:
    """Class representing a basic block of IR instructions."""
    def __init__(self, label=None):
        self.label = label
        self.instructions = []
        self.predecessors = []
        self.successors = []
    
    def add_instruction(self, instruction):
        """Add an instruction to the block."""
        self.instructions.append(instruction)
    
    def to_dict(self):
        """Convert the basic block to a dictionary."""
        return {
            'label': self.label,
            'instructions': [instr.to_dict() for instr in self.instructions],
            'predecessors': [pred.label for pred in self.predecessors],
            'successors': [succ.label for succ in self.successors]
        }

class ControlFlowGraph:
    """Class representing a control flow graph of basic blocks."""
    def __init__(self):
        self.blocks = []
        self.entry = None
        self.exit = None
    
    def add_block(self, block):
        """Add a block to the graph."""
        self.blocks.append(block)
        if not self.entry:
            self.entry = block
    
    def link_blocks(self, pred, succ):
        """Link two blocks as predecessor and successor."""
        if pred not in succ.predecessors:
            succ.predecessors.append(pred)
        if succ not in pred.successors:
            pred.successors.append(succ)
    
    def to_dict(self):
        """Convert the CFG to a dictionary."""
        return {
            'blocks': [block.to_dict() for block in self.blocks],
            'entry': self.entry.label if self.entry else None,
            'exit': self.exit.label if self.exit else None
        }

class IntermediateCodeGenerator:
    """
    Generate three-address code (TAC) intermediate representation from an AST.
    """
    
    def __init__(self):
        """Initialize the intermediate code generator."""
        self.instructions = []
        self.current_function = None
        self.temp_counter = 0
        self.label_counter = 0
        self.cfg = None
        self.current_block = None
        self.errors = []
    
    def generate(self, ast, symbol_table):
        """
        Generate intermediate code from the AST.
        Returns a dictionary with the IR code and CFG information.
        """
        if not ast:
            return {
                'success': False,
                'error': "No AST to generate code from. Semantic analysis may have failed.",
                'errors': []
            }
        
        # Reset state
        self.instructions = []
        self.current_function = None
        self.temp_counter = 0
        self.label_counter = 0
        self.errors = []
        self.cfg = ControlFlowGraph()
        self.current_block = BasicBlock("entry")
        self.cfg.add_block(self.current_block)
        
        # Traverse the AST to generate code
        self._traverse_ast(ast)
        
        # Build control flow graph
        self._build_cfg()
        
        success = len(self.errors) == 0
        
        return {
            'success': success,
            'ir_code': [str(instr) for instr in self.instructions],
            'errors': self.errors,
            'cfg': self.cfg.to_dict()
        }
    
    def _traverse_ast(self, node):
        """Recursively traverse the AST and generate intermediate code."""
        if not node:
            return None
        
        node_type = node.get('type', '')
        
        # Handle different node types
        if node_type == 'translation_unit':
            return self._gen_translation_unit(node)
        elif node_type == 'function_definition':
            return self._gen_function_definition(node)
        elif node_type == 'compound_statement':
            return self._gen_compound_statement(node)
        elif node_type == 'declaration':
            return self._gen_declaration(node)
        elif node_type == 'expression_statement':
            return self._gen_expression_statement(node)
        elif node_type == 'selection_statement':
            return self._gen_selection_statement(node)
        elif node_type == 'iteration_statement':
            return self._gen_iteration_statement(node)
        elif node_type == 'jump_statement':
            return self._gen_jump_statement(node)
        elif node_type == 'expression':
            return self._gen_expression(node)
        elif node_type == 'assignment_expression':
            return self._gen_assignment_expression(node)
        elif node_type == 'conditional_expression':
            return self._gen_conditional_expression(node)
        elif node_type == 'logical_or_expression':
            return self._gen_logical_or_expression(node)
        elif node_type == 'logical_and_expression':
            return self._gen_logical_and_expression(node)
        elif node_type == 'inclusive_or_expression':
            return self._gen_bitwise_or_expression(node)
        elif node_type == 'exclusive_or_expression':
            return self._gen_bitwise_xor_expression(node)
        elif node_type == 'and_expression':
            return self._gen_bitwise_and_expression(node)
        elif node_type == 'equality_expression':
            return self._gen_equality_expression(node)
        elif node_type == 'relational_expression':
            return self._gen_relational_expression(node)
        elif node_type == 'shift_expression':
            return self._gen_shift_expression(node)
        elif node_type == 'additive_expression':
            return self._gen_additive_expression(node)
        elif node_type == 'multiplicative_expression':
            return self._gen_multiplicative_expression(node)
        elif node_type == 'cast_expression':
            return self._gen_cast_expression(node)
        elif node_type == 'unary_expression':
            return self._gen_unary_expression(node)
        elif node_type == 'postfix_expression':
            return self._gen_postfix_expression(node)
        elif node_type == 'primary_expression':
            return self._gen_primary_expression(node)
        
        # Process children recursively
        children = node.get('children', [])
        for child in children:
            self._traverse_ast(child)
        
        return None
    
    def _gen_temp(self):
        """Generate a unique temporary variable name."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def _gen_label(self):
        """Generate a unique label."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def _add_instruction(self, instruction):
        """Add an instruction to the current basic block and instruction list."""
        self.instructions.append(instruction)
        self.current_block.add_instruction(instruction)
        
        # If the instruction is a jump or label, it affects the control flow
        if instruction.opcode in ['GOTO', 'IF_FALSE_GOTO', 'RETURN']:
            # Create a new basic block
            new_block = BasicBlock()
            self.cfg.add_block(new_block)
            
            # Link the current block to the new block
            if instruction.opcode != 'RETURN':
                target_label = instruction.arg1
                # Find or create the target block
                target_block = None
                for block in self.cfg.blocks:
                    if block.label == target_label:
                        target_block = block
                        break
                
                if not target_block:
                    target_block = BasicBlock(target_label)
                    self.cfg.add_block(target_block)
                
                self.cfg.link_blocks(self.current_block, target_block)
            
            # For non-unconditional jumps, link to the next block too
            if instruction.opcode == 'IF_FALSE_GOTO':
                self.cfg.link_blocks(self.current_block, new_block)
            
            self.current_block = new_block
    
    def _build_cfg(self):
        """Build the control flow graph from the instruction list."""
        # Identify basic blocks
        leaders = set([0])  # First instruction is a leader
        
        for i, instr in enumerate(self.instructions):
            if instr.opcode in ['LABEL']:
                leaders.add(i)
            elif instr.opcode in ['GOTO', 'IF_FALSE_GOTO', 'RETURN']:
                leaders.add(i + 1)  # Instruction after jump is a leader
        
        # Create basic blocks
        blocks = []
        leaders = sorted(list(leaders))
        
        for i in range(len(leaders)):
            start = leaders[i]
            end = leaders[i + 1] if i + 1 < len(leaders) else len(self.instructions)
            
            block = BasicBlock()
            for j in range(start, end):
                block.add_instruction(self.instructions[j])
            
            blocks.append(block)
        
        # Connect blocks (build edges)
        for i in range(len(blocks)):
            if i + 1 < len(blocks):
                last_instr = blocks[i].instructions[-1] if blocks[i].instructions else None
                
                # If last instruction is unconditional jump or return, don't connect to next block
                if not last_instr or last_instr.opcode not in ['GOTO', 'RETURN']:
                    blocks[i].successors.append(blocks[i + 1])
                    blocks[i + 1].predecessors.append(blocks[i])
                
                # For jumps, connect to target block
                if last_instr and last_instr.opcode in ['GOTO', 'IF_FALSE_GOTO']:
                    target_label = last_instr.arg1
                    for block in blocks:
                        if block.instructions and block.instructions[0].opcode == 'LABEL' and block.instructions[0].arg1 == target_label:
                            blocks[i].successors.append(block)
                            block.predecessors.append(blocks[i])
                            break
        
        self.cfg.blocks = blocks
        self.cfg.entry = blocks[0] if blocks else None
        # The exit is typically the block with no successors
        for block in blocks:
            if not block.successors:
                self.cfg.exit = block
                break
    
    def _gen_translation_unit(self, node):
        """Generate code for the translation unit (top-level node)."""
        children = node.get('children', [])
        for child in children:
            self._traverse_ast(child)
    
    def _gen_function_definition(self, node):
        """Generate code for a function definition."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # Extract function name
        func_name = self._extract_function_name(children[1])
        if not func_name:
            return
        
        # Set current function
        self.current_function = func_name
        
        # Generate function label
        func_label = f"func_{func_name}"
        self._add_instruction(IRInstruction('LABEL', None, func_label))
        
        # Process function body
        if len(children) > 2:
            self._traverse_ast(children[2])
        
        # Add a return if not already present
        if not self.instructions or self.instructions[-1].opcode != 'RETURN':
            self._add_instruction(IRInstruction('RETURN'))
        
        # Reset current function
        self.current_function = None
    
    def _extract_function_name(self, node):
        """Extract function name from declarator node."""
        if not node:
            return None
        
        # Navigate through the AST to find the function name
        # This is a simplified version; a real implementation would be more robust
        
        func_name = None
        
        def find_func_name(n):
            nonlocal func_name
            
            if not n:
                return
            
            n_type = n.get('type', '')
            children = n.get('children', [])
            
            if n_type == 'direct_declarator':
                if children and children[0].get('type') == 'id':
                    func_name = children[0].get('value', '')
                    return
            
            # Check children
            for child in children:
                find_func_name(child)
        
        find_func_name(node)
        
        return func_name
    
    def _gen_compound_statement(self, node):
        """Generate code for a compound statement (block)."""
        children = node.get('children', [])
        for child in children:
            self._traverse_ast(child)
    
    def _gen_declaration(self, node):
        """Generate code for a variable declaration."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # Process initializations in the declarator list
        self._traverse_ast(children[1])
    
    def _gen_expression_statement(self, node):
        """Generate code for an expression statement."""
        children = node.get('children', [])
        if not children:
            return
        
        # Generate code for the expression
        self._traverse_ast(children[0])
    
    def _gen_selection_statement(self, node):
        """Generate code for an if or switch statement."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be 'if', 'if_else', or 'switch'
        stmt_type = children[0].get('value', '')
        
        if stmt_type in ('if', 'if_else'):
            # Generate code for if statement
            cond_result = self._traverse_ast(children[1])
            if not cond_result:
                return
            
            else_label = self._gen_label()
            end_label = self._gen_label() if stmt_type == 'if_else' else else_label
            
            # Jump to else if condition is false
            self._add_instruction(IRInstruction('IF_FALSE_GOTO', None, else_label, cond_result))
            
            # Generate code for 'then' block
            if len(children) > 2:
                self._traverse_ast(children[2])
            
            # Jump to end after 'then' block (for if-else)
            if stmt_type == 'if_else':
                self._add_instruction(IRInstruction('GOTO', None, end_label))
            
            # Else label
            self._add_instruction(IRInstruction('LABEL', None, else_label))
            
            # Generate code for 'else' block (for if-else)
            if stmt_type == 'if_else' and len(children) > 3:
                self._traverse_ast(children[3])
            
            # End label (for if-else)
            if stmt_type == 'if_else':
                self._add_instruction(IRInstruction('LABEL', None, end_label))
        
        elif stmt_type == 'switch':
            # Generate code for switch statement (simplified)
            self._traverse_ast(children[1])  # Evaluate the switch expression
            if len(children) > 2:
                self._traverse_ast(children[2])  # Process the switch body
    
    def _gen_iteration_statement(self, node):
        """Generate code for a loop statement (while, do-while, for)."""
        children = node.get('children', [])
        if len(children) < 2:
            return
        
        # First child should be 'while', 'do_while', or 'for'
        stmt_type = children[0].get('value', '')
        
        if stmt_type == 'while':
            loop_start = self._gen_label()
            loop_end = self._gen_label()
            
            # Loop start label
            self._add_instruction(IRInstruction('LABEL', None, loop_start))
            
            # Evaluate condition
            cond_result = self._traverse_ast(children[1])
            if not cond_result:
                return
            
            # Jump to end if condition is false
            self._add_instruction(IRInstruction('IF_FALSE_GOTO', None, loop_end, cond_result))
            
            # Generate code for loop body
            if len(children) > 2:
                self._traverse_ast(children[2])
            
            # Jump back to start
            self._add_instruction(IRInstruction('GOTO', None, loop_start))
            
            # Loop end label
            self._add_instruction(IRInstruction('LABEL', None, loop_end))
        
        elif stmt_type == 'do_while':
            loop_start = self._gen_label()
            
            # Loop start label
            self._add_instruction(IRInstruction('LABEL', None, loop_start))
            
            # Generate code for loop body
            if len(children) > 1:
                self._traverse_ast(children[1])
            
            # Evaluate condition
            cond_result = self._traverse_ast(children[2]) if len(children) > 2 else None
            if not cond_result:
                return
            
            # Jump back to start if condition is true
            self._add_instruction(IRInstruction('IF_TRUE_GOTO', None, loop_start, cond_result))
        
        elif stmt_type == 'for':
            # Initialize
            if len(children) > 1:
                self._traverse_ast(children[1])
            
            loop_start = self._gen_label()
            loop_end = self._gen_label()
            
            # Loop start label
            self._add_instruction(IRInstruction('LABEL', None, loop_start))
            
            # Evaluate condition
            cond_result = None
            if len(children) > 2 and children[2].get('type') != 'empty':
                cond_result = self._traverse_ast(children[2])
            
            # Jump to end if condition is false
            if cond_result:
                self._add_instruction(IRInstruction('IF_FALSE_GOTO', None, loop_end, cond_result))
            
            # Generate code for loop body
            if len(children) > 4:
                self._traverse_ast(children[4])
            
            # Increment
            if len(children) > 3 and children[3].get('type') != 'empty':
                self._traverse_ast(children[3])
            
            # Jump back to start
            self._add_instruction(IRInstruction('GOTO', None, loop_start))
            
            # Loop end label
            self._add_instruction(IRInstruction('LABEL', None, loop_end))
    
    def _gen_jump_statement(self, node):
        """Generate code for a jump statement (return, break, continue, goto)."""
        children = node.get('children', [])
        if not children:
            return
        
        # First child should be 'return', 'break', 'continue', or 'goto'
        stmt_type = children[0].get('value', '')
        
        if stmt_type == 'return':
            # Return expression
            if len(children) > 1:
                ret_val = self._traverse_ast(children[1])
                self._add_instruction(IRInstruction('RETURN', None, ret_val))
            else:
                self._add_instruction(IRInstruction('RETURN'))
        
        elif stmt_type == 'break':
            # This is simplified; in a real compiler, we'd need to know which loop to break from
            self._add_instruction(IRInstruction('BREAK'))
        
        elif stmt_type == 'continue':
            # This is simplified; in a real compiler, we'd need to know which loop to continue
            self._add_instruction(IRInstruction('CONTINUE'))
        
        elif stmt_type == 'goto':
            # Goto label
            if len(children) > 1:
                label = children[1].get('value', '')
                self._add_instruction(IRInstruction('GOTO', None, f"label_{label}"))
    
    def _gen_expression(self, node):
        """Generate code for an expression."""
        children = node.get('children', [])
        if not children:
            return None
        
        # Process all expressions in the list
        result = None
        for child in children:
            result = self._traverse_ast(child)
        
        return result
    
    def _gen_assignment_expression(self, node):
        """Generate code for an assignment expression."""
        children = node.get('children', [])
        if len(children) < 2:
            return self._traverse_ast(children[0]) if children else None
        
        # This is an assignment: lvalue = rvalue
        lvalue = self._get_lvalue(children[0])
        op = children[1].get('value', '=')
        rvalue = self._traverse_ast(children[2])
        
        if not lvalue or not rvalue:
            return None
        
        # Simple assignment
        if op == '=':
            self._add_instruction(IRInstruction('ASSIGN', lvalue, rvalue))
            return lvalue
        
        # Compound assignment (+=, -=, etc.)
        op_code = op[:-1]  # Remove the = sign
        temp = self._gen_temp()
        
        # Generate binary operation first
        self._add_instruction(IRInstruction(op_code, temp, lvalue, rvalue))
        
        # Assign the result to the lvalue
        self._add_instruction(IRInstruction('ASSIGN', lvalue, temp))
        
        return lvalue
    
    def _get_lvalue(self, node):
        """Extract the left value from an expression (variable name, array element, etc.)."""
        # Simplified for demo; a real compiler would handle more complex lvalues
        if node.get('type') == 'unary_expression':
            children = node.get('children', [])
            if children and children[0].get('type') == 'postfix_expression':
                postfix = children[0]
                post_children = postfix.get('children', [])
                if post_children and post_children[0].get('type') == 'primary_expression':
                    primary = post_children[0]
                    primary_children = primary.get('children', [])
                    if primary_children and primary_children[0].get('type') == 'id':
                        return primary_children[0].get('value', '')
        
        return None
    
    def _gen_conditional_expression(self, node):
        """Generate code for a conditional expression (ternary operator)."""
        children = node.get('children', [])
        if len(children) < 2:
            return self._traverse_ast(children[0]) if children else None
        
        # This is a ternary: cond ? expr1 : expr2
        cond = self._traverse_ast(children[0])
        
        true_label = self._gen_label()
        false_label = self._gen_label()
        end_label = self._gen_label()
        
        result = self._gen_temp()
        
        # If condition is false, jump to false branch
        self._add_instruction(IRInstruction('IF_FALSE_GOTO', None, false_label, cond))
        
        # True branch
        expr1 = self._traverse_ast(children[1])
        self._add_instruction(IRInstruction('ASSIGN', result, expr1))
        self._add_instruction(IRInstruction('GOTO', None, end_label))
        
        # False branch
        self._add_instruction(IRInstruction('LABEL', None, false_label))
        expr2 = self._traverse_ast(children[2])
        self._add_instruction(IRInstruction('ASSIGN', result, expr2))
        
        # End
        self._add_instruction(IRInstruction('LABEL', None, end_label))
        
        return result
    
    def _gen_logical_or_expression(self, node):
        """Generate code for a logical OR expression."""
        children = node.get('children', [])
        if len(children) < 2:
            return self._traverse_ast(children[0]) if children else None
        
        # Short-circuit evaluation
        left = self._traverse_ast(children[0])
        
        true_label = self._gen_label()
        end_label = self._gen_label()
        
        result = self._gen_temp()
        
        # If left is true, short-circuit and use true
        self._add_instruction(IRInstruction('IF_TRUE_GOTO', None, true_label, left))
        
        # Evaluate right side
        right = self._traverse_ast(children[1])
        self._add_instruction(IRInstruction('ASSIGN', result, right))
        self._add_instruction(IRInstruction('GOTO', None, end_label))
        
        # True case (short-circuit)
        self._add_instruction(IRInstruction('LABEL', None, true_label))
        self._add_instruction(IRInstruction('ASSIGN', result, '1'))  # true
        
        # End
        self._add_instruction(IRInstruction('LABEL', None, end_label))
        
        return result
    
    def _gen_logical_and_expression(self, node):
        """Generate code for a logical AND expression."""
        children = node.get('children', [])
        if len(children) < 2:
            return self._traverse_ast(children[0]) if children else None
        
        # Short-circuit evaluation
        left = self._traverse_ast(children[0])
        
        false_label = self._gen_label()
        end_label = self._gen_label()
        
        result = self._gen_temp()
        
        # If left is false, short-circuit and use false
        self._add_instruction(IRInstruction('IF_FALSE_GOTO', None, false_label, left))
        
        # Evaluate right side
        right = self._traverse_ast(children[1])
        self._add_instruction(IRInstruction('ASSIGN', result, right))
        self._add_instruction(IRInstruction('GOTO', None, end_label))
        
        # False case (short-circuit)
        self._add_instruction(IRInstruction('LABEL', None, false_label))
        self._add_instruction(IRInstruction('ASSIGN', result, '0'))  # false
        
        # End
        self._add_instruction(IRInstruction('LABEL', None, end_label))
        
        return result
    
    def _gen_bitwise_or_expression(self, node):
        """Generate code for a bitwise OR expression."""
        return self._gen_binary_operation(node, '|')
    
    def _gen_bitwise_xor_expression(self, node):
        """Generate code for a bitwise XOR expression."""
        return self._gen_binary_operation(node, '^')
    
    def _gen_bitwise_and_expression(self, node):
        """Generate code for a bitwise AND expression."""
        return self._gen_binary_operation(node, '&')
    
    def _gen_equality_expression(self, node):
        """Generate code for an equality expression."""
        leaf = node.get('value')
        if leaf == '==':
            return self._gen_binary_operation(node, '==')
        elif leaf == '!=':
            return self._gen_binary_operation(node, '!=')
        else:
            children = node.get('children', [])
            return self._traverse_ast(children[0]) if children else None
    
    def _gen_relational_expression(self, node):
        """Generate code for a relational expression."""
        leaf = node.get('value')
        if leaf == '<':
            return self._gen_binary_operation(node, '<')
        elif leaf == '>':
            return self._gen_binary_operation(node, '>')
        elif leaf == '<=':
            return self._gen_binary_operation(node, '<=')
        elif leaf == '>=':
            return self._gen_binary_operation(node, '>=')
        else:
            children = node.get('children', [])
            return self._traverse_ast(children[0]) if children else None
    
    def _gen_shift_expression(self, node):
        """Generate code for a shift expression."""
        leaf = node.get('value')
        if leaf == '<<':
            return self._gen_binary_operation(node, '<<')
        elif leaf == '>>':
            return self._gen_binary_operation(node, '>>')
        else:
            children = node.get('children', [])
            return self._traverse_ast(children[0]) if children else None
    
    def _gen_additive_expression(self, node):
        """Generate code for an additive expression."""
        leaf = node.get('value')
        if leaf == '+':
            return self._gen_binary_operation(node, '+')
        elif leaf == '-':
            return self._gen_binary_operation(node, '-')
        else:
            children = node.get('children', [])
            return self._traverse_ast(children[0]) if children else None
    
    def _gen_multiplicative_expression(self, node):
        """Generate code for a multiplicative expression."""
        leaf = node.get('value')
        if leaf == '*':
            return self._gen_binary_operation(node, '*')
        elif leaf == '/':
            return self._gen_binary_operation(node, '/')
        elif leaf == '%':
            return self._gen_binary_operation(node, '%')
        else:
            children = node.get('children', [])
            return self._traverse_ast(children[0]) if children else None
    
    def _gen_binary_operation(self, node, op):
        """Generate code for a binary operation."""
        children = node.get('children', [])
        if len(children) < 2:
            return self._traverse_ast(children[0]) if children else None
        
        left = self._traverse_ast(children[0])
        right = self._traverse_ast(children[1])
        
        if not left or not right:
            return None
        
        result = self._gen_temp()
        self._add_instruction(IRInstruction(op, result, left, right))
        
        return result
    
    def _gen_cast_expression(self, node):
        """Generate code for a cast expression."""
        children = node.get('children', [])
        leaf = node.get('value')
        
        if leaf == 'cast' and len(children) >= 2:
            # This is a cast: (type)expr
            expr = self._traverse_ast(children[1])
            if not expr:
                return None
            
            # Get the target type
            type_name = self._extract_type_name(children[0])
            
            # Generate cast instruction
            result = self._gen_temp()
            self._add_instruction(IRInstruction('CAST', result, expr, type_name))
            
            return result
        else:
            return self._traverse_ast(children[0]) if children else None
    
    def _extract_type_name(self, node):
        """Extract type name from a type_name node."""
        # Simplified for demo
        return "unknown_type"
    
    def _gen_unary_expression(self, node):
        """Generate code for a unary expression."""
        children = node.get('children', [])
        if not children:
            return None
        
        leaf = node.get('value')
        
        if leaf and leaf.startswith('pre'):
            # This is a pre-increment/decrement: ++expr or --expr
            expr = self._traverse_ast(children[0])
            if not expr:
                return None
            
            op = leaf[3:]  # Get ++ or --
            result = expr  # The result is the same variable
            
            if op == '++':
                self._add_instruction(IRInstruction('+', result, expr, '1'))
            else:  # op == '--'
                self._add_instruction(IRInstruction('-', result, expr, '1'))
            
            return result
        
        elif len(children) >= 2 and children[0].get('type') == 'unary_operator':
            # This is a unary operation: op expr
            op = children[0].get('value')
            expr = self._traverse_ast(children[1])
            
            if not expr:
                return None
            
            result = self._gen_temp()
            
            if op == '&':  # Address-of operator
                self._add_instruction(IRInstruction('ADDR', result, expr))
            elif op == '*':  # Dereference operator
                self._add_instruction(IRInstruction('DEREF', result, expr))
            elif op == '+':  # Unary plus (no-op in C)
                self._add_instruction(IRInstruction('ASSIGN', result, expr))
            elif op == '-':  # Unary minus
                self._add_instruction(IRInstruction('-', result, '0', expr))
            elif op == '~':  # Bitwise NOT
                self._add_instruction(IRInstruction('~', result, expr))
            elif op == '!':  # Logical NOT
                self._add_instruction(IRInstruction('!', result, expr))
            
            return result
        
        elif leaf == 'sizeof':
            # This is a sizeof operator
            expr = self._traverse_ast(children[0])
            if not expr:
                return None
            
            result = self._gen_temp()
            self._add_instruction(IRInstruction('SIZEOF', result, expr))
            
            return result
        
        else:
            return self._traverse_ast(children[0])
    
    def _gen_postfix_expression(self, node):
        """Generate code for a postfix expression."""
        children = node.get('children', [])
        if not children:
            return None
        
        leaf = node.get('value')
        
        if leaf and leaf.startswith('post'):
            # This is a post-increment/decrement: expr++ or expr--
            expr = self._traverse_ast(children[0])
            if not expr:
                return None
            
            op = leaf[4:]  # Get ++ or --
            
            # Save the original value
            result = self._gen_temp()
            self._add_instruction(IRInstruction('ASSIGN', result, expr))
            
            # Perform the increment/decrement
            if op == '++':
                self._add_instruction(IRInstruction('+', expr, expr, '1'))
            else:  # op == '--'
                self._add_instruction(IRInstruction('-', expr, expr, '1'))
            
            return result
        
        elif leaf == 'array':
            # This is an array access: array[index]
            array = self._traverse_ast(children[0])
            index = self._traverse_ast(children[1])
            
            if not array or not index:
                return None
            
            result = self._gen_temp()
            self._add_instruction(IRInstruction('INDEX', result, array, index))
            
            return result
        
        elif leaf == 'function_call':
            # This is a function call: func(args)
            func = self._traverse_ast(children[0])
            
            if not func:
                return None
            
            # Process arguments
            args = []
            if len(children) > 1:
                self._extract_arguments(children[1], args)
            
            # Add parameter instructions
            for arg in args:
                self._add_instruction(IRInstruction('PARAM', None, arg))
            
            # Call the function
            result = self._gen_temp()
            self._add_instruction(IRInstruction('CALL', result, func, str(len(args))))
            
            return result
        
        elif leaf == '.':
            # This is a struct member access: struct.member
            struct = self._traverse_ast(children[0])
            member = children[1].get('value') if len(children) > 1 else None
            
            if not struct or not member:
                return None
            
            result = self._gen_temp()
            self._add_instruction(IRInstruction('MEMBER', result, struct, member))
            
            return result
        
        elif leaf == '->':
            # This is a struct pointer member access: ptr->member
            ptr = self._traverse_ast(children[0])
            member = children[1].get('value') if len(children) > 1 else None
            
            if not ptr or not member:
                return None
            
            result = self._gen_temp()
            self._add_instruction(IRInstruction('PTR_MEMBER', result, ptr, member))
            
            return result
        
        else:
            return self._traverse_ast(children[0])
    
    def _extract_arguments(self, node, args):
        """Extract function arguments from an argument_expression_list node."""
        if not node:
            return
        
        node_type = node.get('type', '')
        children = node.get('children', [])
        
        if node_type == 'assignment_expression':
            arg = self._traverse_ast(node)
            if arg:
                args.append(arg)
        
        # Check children recursively
        for child in children:
            self._extract_arguments(child, args)
    
    def _gen_primary_expression(self, node):
        """Generate code for a primary expression."""
        children = node.get('children', [])
        if not children:
            return None
        
        child = children[0]
        child_type = child.get('type', '')
        
        if child_type == 'id':
            # This is a variable
            return child.get('value', '')
        
        elif child_type == 'constant':
            # This is a constant
            return child.get('value', '0')
        
        elif child_type == 'string_literal':
            # This is a string literal
            str_val = child.get('value', '""')
            
            # Create a temporary for the string
            temp = self._gen_temp()
            self._add_instruction(IRInstruction('STRING', temp, str_val))
            
            return temp
        
        else:
            # This is a parenthesized expression
            return self._traverse_ast(child)
