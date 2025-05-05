"""
Utility functions for the compiler.
"""
import json

def format_tokens_for_visualization(tokens):
    """
    Format tokens for visualization in the web interface.
    
    Args:
        tokens: List of token dictionaries
        
    Returns:
        Formatted tokens for visualization
    """
    result = []
    for token in tokens:
        result.append({
            'type': token['type'],
            'value': token['value'],
            'line': token['line'],
            'position': token['position']
        })
    return result

def format_ast_for_visualization(ast_node):
    """
    Format the AST for visualization in the web interface.
    Converts sets to lists and prepares for JSON serialization.
    """
    def node_to_dict(node):
        if isinstance(node, dict):
            return {k: node_to_dict(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [node_to_dict(elem) for elem in node]
        elif isinstance(node, set):
            return [node_to_dict(elem) for elem in node]
        elif hasattr(node, '__dict__'):
            return {k: node_to_dict(v) for k, v in vars(node).items() if not k.startswith('_')}
        else:
            return node

    serializable_ast = node_to_dict(ast_node)
    return json.dumps(serializable_ast, indent=2)



def convert_sets_to_lists(obj):
    """
    Recursively convert all sets in a data structure to lists.
    """
    if isinstance(obj, dict):
        return {k: convert_sets_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(elem) for elem in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj





def format_symbol_table(symbols):
    """
    Format the symbol table for visualization in the web interface.
    
    Args:
        symbols: List of symbol dictionaries
        
    Returns:
        Formatted symbol table for visualization
    """
    result = []
    for symbol in symbols:
        result.append({
            'name': symbol['name'],
            'type': symbol['type'],
            'scope': symbol['scope'],
            'line': symbol['line'],
            'is_function': symbol['is_function'],
            'params': list(symbol['params']) if 'params' in symbol else [],
            'used': symbol['used'] if 'used' in symbol else False
        })
    return result

def format_errors(errors):
    """
    Format error messages for visualization in the web interface.
    
    Args:
        errors: List of error dictionaries
        
    Returns:
        Formatted error messages for visualization
    """
    result = []
    for error in errors:
        result.append({
            'type': error.get('type', 'error'),
            'message': error.get('message', 'Unknown error'),
            'line': error.get('line', 0),
            'position': error.get('position', 0) if 'position' in error else 0
        })
    return result

def highlight_code_with_token_positions(code, tokens):
    """
    Create a mapping of line and character positions to token types for syntax highlighting.
    
    Args:
        code: Source code as a string
        tokens: List of token dictionaries
        
    Returns:
        Dictionary mapping line and character positions to token types
    """
    lines = code.split('\n')
    highlights = {}
    
    for token in tokens:
        if 'line' not in token or 'position' not in token:
            continue
            
        line = token['line']
        pos = token['position']
        
        # Calculate the actual position in the line
        if line > 1:
            for i in range(line - 1):
                if i < len(lines):
                    pos -= len(lines[i]) + 1  # +1 for the newline character
        
        token_length = len(str(token['value']))
        
        # Initialize the line if not present
        if line not in highlights:
            highlights[line] = {}
        
        # Add token type for each character in the token
        for i in range(pos, pos + token_length):
            highlights[line][i] = token['type']
    
    return highlights

def create_control_flow_graph_data(cfg):
    """
    Create data structure for visualizing control flow graph.
    
    Args:
        cfg: Control Flow Graph dictionary
        
    Returns:
        Data structure for D3.js visualization
    """
    nodes = []
    links = []
    
    if not cfg or 'blocks' not in cfg:
        return {'nodes': nodes, 'links': links}
    
    # Create nodes
    for i, block in enumerate(cfg['blocks']):
        label = block.get('label', f"Block_{i}")
        
        # Format instructions for display
        instructions = []
        for instr in block.get('instructions', []):
            if isinstance(instr, dict):
                instr_str = f"{instr.get('result', '')} = {instr.get('arg1', '')} {instr.get('opcode', '')} {instr.get('arg2', '')}"
                instructions.append(instr_str.strip())
            else:
                instructions.append(str(instr))
        
        nodes.append({
            'id': label,
            'label': label,
            'instructions': instructions
        })
    
    # Create links
    for i, block in enumerate(cfg['blocks']):
        source = block.get('label', f"Block_{i}")
        
        for succ_label in block.get('successors', []):
            if isinstance(succ_label, str):
                target = succ_label
            else:
                # If successors is a list of indices or objects
                for j, succ_block in enumerate(cfg['blocks']):
                    if j == succ_label or succ_block.get('label') == succ_label:
                        target = succ_block.get('label', f"Block_{j}")
                        break
                else:
                    continue
            
            links.append({
                'source': source,
                'target': target
            })
    
    return {'nodes': nodes, 'links': links}
