import os
import logging
from flask import Flask, render_template, request, jsonify
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.intermediate import IntermediateCodeGenerator
from compiler.optimizer import Optimizer
from compiler.codegen import CodeGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

@app.route('/')
def index():
    """Render the main page of the compiler."""
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    """Process the compilation of C code and return results for each phase."""
    try:
        source_code = request.json.get('code', '')
        logger.debug(f"Received code for compilation: {source_code[:50]}...")

        # Initialize compiler components
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        semantic_analyzer = SemanticAnalyzer()
        intermediate_gen = IntermediateCodeGenerator()
        optimizer = Optimizer()
        code_generator = CodeGenerator()

        # Step 1: Lexical Analysis
        lexical_result = lexer.tokenize()
        
        # Step 2: Syntax Analysis
        if lexical_result.get('success'):
            syntax_result = parser.parse()
        else:
            syntax_result = {"success": False, "error": "Skipped due to lexical errors"}
        
        # Step 3: Semantic Analysis
        if syntax_result.get('success'):
            semantic_result = semantic_analyzer.analyze(parser.ast)
        else:
            semantic_result = {"success": False, "error": "Skipped due to syntax errors"}
        
        # Step 4: Intermediate Code Generation
        if semantic_result.get('success'):
            intermediate_result = intermediate_gen.generate(semantic_analyzer.ast, semantic_analyzer.symbol_table)
        else:
            intermediate_result = {"success": False, "error": "Skipped due to semantic errors"}
        
        # Step 5: Code Optimization
        if intermediate_result.get('success'):
            optimization_result = optimizer.optimize(intermediate_result.get('ir_code'))
        else:
            optimization_result = {"success": False, "error": "Skipped due to intermediate code errors"}
        
        # Step 6: Code Generation
        if optimization_result.get('success'):
            codegen_result = code_generator.generate(optimization_result.get('optimized_code'))
        else:
            codegen_result = {"success": False, "error": "Skipped due to optimization errors"}
        
        # Compile results from all phases
        result = {
            'lexical': lexical_result,
            'syntax': syntax_result,
            'semantic': semantic_result,
            'intermediate': intermediate_result,
            'optimization': optimization_result,
            'codegen': codegen_result
        }
        
        # Log the output for debugging
        logger.debug(f"Returning lexical result with {len(lexical_result.get('tokens', []))} tokens")
        if 'tokens' in lexical_result:
            logger.debug(f"First few tokens: {lexical_result['tokens'][:3]}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error during compilation: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f"Compilation error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
