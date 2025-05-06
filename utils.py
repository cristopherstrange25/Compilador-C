import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

def visualize_graph(graph):
    """
    Visualize a NetworkX graph.
    
    Args:
        graph (networkx.Graph): The graph to visualize
        
    Returns:
        matplotlib.figure.Figure: The figure containing the graph visualization
    """
    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    # Set up layout
    pos = nx.spring_layout(graph, seed=42)
    
    # Get node types for coloring
    node_types = {}
    for node, data in graph.nodes(data=True):
        node_types[node] = data.get('type', 'unknown')
    
    # Create color map
    type_colors = {
        'variable': 'skyblue',
        'value': 'lightgreen',
        'expression': 'yellow',
        'binary_expr': 'orange',
        'unary_expr': 'pink',
        'if_statement': 'red',
        'condition': 'purple',
        'if_body': 'lightgray',
        'else_body': 'darkgray',
        'while_loop': 'brown',
        'for_loop': 'olive',
        'method': 'teal',
        'parameter': 'lavender',
        'class': 'gold',
        'attribute': 'coral',
        'case': 'lightblue',
        'default_case': 'plum',
        'switch_statement': 'khaki',
        'block': 'lightgray',
        'method_body': 'white',
        'unknown': 'white'
    }
    
    # Draw nodes with colors based on type
    for node_type, color in type_colors.items():
        nodes = [node for node, type_ in node_types.items() if type_ == node_type]
        if nodes:
            nx.draw_networkx_nodes(graph, pos, nodelist=nodes, node_color=color, node_size=500, alpha=0.8)
    
    # Draw edges with labels
    edge_labels = {(u, v): d.get('label', '') for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5, arrows=True)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)
    
    # Draw node labels
    node_labels = {}
    for node, data in graph.nodes(data=True):
        if 'condition' in data:
            node_labels[node] = f"{data['type']}\n{data['condition']}"
        elif 'expr' in data:
            node_labels[node] = f"{data['type']}\n{data['expr']}"
        else:
            node_labels[node] = str(node)
    
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8)
    
    # Set up the plot
    plt.axis('off')
    plt.tight_layout()
    
    # Return the figure
    return plt.gcf()

def highlight_error_in_code(code, error_msg):
    """
    Highlight the part of the code where an error occurred.
    
    Args:
        code (str): The source code
        error_msg (str): The error message containing line/position information
        
    Returns:
        None: Displays the highlighted code in the Streamlit app
    """
    try:
        # Extract line number from error message if available
        line_num = None
        
        # Try to find 'line X' or 'line: X' pattern
        if 'line' in error_msg:
            parts = error_msg.split('line')
            if len(parts) > 1:
                # Try to extract the number after 'line'
                num_str = ''.join(c for c in parts[1].split()[0] if c.isdigit())
                if num_str:
                    line_num = int(num_str) - 1  # Convert to 0-indexed
        
        # If we found a line number, highlight that line
        if line_num is not None and line_num >= 0:
            lines = code.split('\n')
            if line_num < len(lines):
                # Create a list of line numbers for display
                line_numbers = list(range(1, len(lines) + 1))
                
                # Create the display text with highlighted error line
                display_lines = []
                for i, line in enumerate(lines):
                    if i == line_num:
                        display_lines.append(f"➡️ {line}")
                    else:
                        display_lines.append(f"   {line}")
                
                # Display with line numbers
                error_display = '\n'.join(f"{num}: {line}" for num, line in zip(line_numbers, display_lines))
                st.code(error_display, language="c")
            else:
                # Line number out of range, show the regular code
                st.code(code, language="c")
        else:
            # No line number found, show the regular code
            st.code(code, language="c")
        
        # Display the error message separately
        st.error(error_msg)
    
    except Exception as e:
        # If anything goes wrong, just show the regular code
        st.code(code, language="c")
        st.error(f"{error_msg}\n(Error highlighting failed: {str(e)})")

def generate_control_flow_diagram(code):
    """
    Generate a control flow diagram from code.
    
    Args:
        code (str): The source code
        
    Returns:
        networkx.DiGraph: A graph representing the control flow
    """
    # Create a new directed graph
    cfg = nx.DiGraph()
    
    # This is a simplified approach - a real CFG generator would parse the code
    lines = code.split('\n')
    
    # Identify basic blocks and control structures
    current_block = "start"
    cfg.add_node(current_block, type="block", lines=[])
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//') or line.startswith('/*'):
            continue
        
        # Record the line in the current block
        if 'lines' in cfg.nodes[current_block]:
            cfg.nodes[current_block]['lines'].append(line)
        
        # Check for control structures
        if "if" in line and "(" in line and ")" in line:
            # Extract condition
            condition = line[line.find("(")+1:line.find(")")]
            
            # Create conditional node
            cond_node = f"if_{i}"
            cfg.add_node(cond_node, type="condition", condition=condition)
            
            # Connect current block to condition
            cfg.add_edge(current_block, cond_node)
            
            # Create then and else blocks
            then_block = f"then_{i}"
            else_block = f"else_{i}"
            cfg.add_node(then_block, type="block", lines=[])
            cfg.add_node(else_block, type="block", lines=[])
            
            # Connect condition to branches
            cfg.add_edge(cond_node, then_block, label="true")
            cfg.add_edge(cond_node, else_block, label="false")
            
            # Update current block
            current_block = then_block
        
        elif "else" in line:
            # This is an else block following an if
            # Create a join node for after the if-else
            join_node = f"join_{i}"
            cfg.add_node(join_node, type="block", lines=[])
            
            # Connect current block to join
            cfg.add_edge(current_block, join_node)
            
            # Find the corresponding else block and update current block
            for node in cfg.nodes():
                if isinstance(node, str) and node.startswith("else_"):
                    current_block = node
                    break
        
        elif "for" in line or "while" in line:
            # Extract loop condition
            if "(" in line and ")" in line:
                condition = line[line.find("(")+1:line.find(")")]
            else:
                condition = "unknown"
            
            # Create loop nodes
            loop_header = f"loop_{i}"
            loop_body = f"loop_body_{i}"
            loop_exit = f"loop_exit_{i}"
            
            cfg.add_node(loop_header, type="condition", condition=condition)
            cfg.add_node(loop_body, type="block", lines=[])
            cfg.add_node(loop_exit, type="block", lines=[])
            
            # Connect nodes
            cfg.add_edge(current_block, loop_header)
            cfg.add_edge(loop_header, loop_body, label="true")
            cfg.add_edge(loop_header, loop_exit, label="false")
            cfg.add_edge(loop_body, loop_header)  # Loop back
            
            # Update current block
            current_block = loop_body
        
        elif "switch" in line:
            # Create switch node
            switch_node = f"switch_{i}"
            exit_node = f"switch_exit_{i}"
            
            if "(" in line and ")" in line:
                expr = line[line.find("(")+1:line.find(")")]
            else:
                expr = "unknown"
                
            cfg.add_node(switch_node, type="switch", expr=expr)
            cfg.add_node(exit_node, type="block", lines=[])
            
            # Connect current block to switch
            cfg.add_edge(current_block, switch_node)
            
            # Update current block
            current_block = switch_node
        
        elif "case" in line or "default" in line:
            # Create case node
            case_node = f"case_{i}"
            
            if ":" in line:
                value = line.split(":")[0].replace("case", "").strip()
            else:
                value = "unknown"
                
            cfg.add_node(case_node, type="case", value=value)
            
            # Find the parent switch
            for node in cfg.nodes():
                if isinstance(node, str) and node.startswith("switch_"):
                    cfg.add_edge(node, case_node)
                    break
            
            # Update current block
            current_block = case_node
        
        elif "break" in line:
            # Find the enclosing control structure's exit
            for node in cfg.nodes():
                if isinstance(node, str) and (
                    node.startswith("switch_exit_") or
                    node.startswith("loop_exit_") or
                    node.startswith("join_")
                ):
                    cfg.add_edge(current_block, node)
                    break
        
        elif "return" in line:
            # Create an exit node
            exit_node = "exit"
            if "exit" not in cfg.nodes():
                cfg.add_node(exit_node, type="exit")
            
            # Connect current block to exit
            cfg.add_edge(current_block, exit_node)
    
    # Connect any dangling blocks to exit
    for node in cfg.nodes():
        if not list(cfg.successors(node)) and node != "exit":
            if "exit" not in cfg.nodes():
                cfg.add_node("exit", type="exit")
            cfg.add_edge(node, "exit")
    
    return cfg
