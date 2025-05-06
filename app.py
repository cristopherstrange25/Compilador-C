import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import StringIO
import tempfile
import os
import subprocess

# Import compiler components
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from intermediate_code import IntermediateCodeGenerator
from code_optimizer import CodeOptimizer
from code_generator import CodeGenerator
from execution import Executor
from utils import visualize_graph, highlight_error_in_code

# Set page configuration
st.set_page_config(
    page_title="Compilador de C",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a header
st.title("Compilador de C basado en Python")
st.write("Ingresa código en C y analiza cada fase de compilación")

# Add the stock images in the sidebar
st.sidebar.header("Acerca de")
st.sidebar.image("https://images.unsplash.com/photo-1488590528505-98d2b5aba04b", 
                 caption="Editor de Código", use_column_width=True)
st.sidebar.image("https://images.unsplash.com/photo-1578674351410-8b28ab3c66b6", 
                caption="Diagrama del Compilador", use_column_width=True)

# Create session state variables if they don't exist
if 'c_code' not in st.session_state:
    st.session_state.c_code = """
// Código de ejemplo en C
#include <stdio.h>

int main() {
    int a = 10;
    int b = 20;
    int suma = a + b;
    
    if (suma > 20) {
        printf("La suma es mayor que 20\\n");
    } else {
        printf("La suma es menor o igual a 20\\n");
    }
    
    return 0;
}
"""

if 'lexer_output' not in st.session_state:
    st.session_state.lexer_output = None
if 'parser_output' not in st.session_state:
    st.session_state.parser_output = None
if 'semantic_output' not in st.session_state:
    st.session_state.semantic_output = None
if 'intermediate_code' not in st.session_state:
    st.session_state.intermediate_code = None
if 'optimized_code' not in st.session_state:
    st.session_state.optimized_code = None
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'execution_output' not in st.session_state:
    st.session_state.execution_output = None
if 'symbol_table' not in st.session_state:
    st.session_state.symbol_table = None
if 'errors' not in st.session_state:
    st.session_state.errors = {}

# Code editor
st.subheader("Editor de Código C")
c_code = st.text_area("", st.session_state.c_code, height=300)

if c_code != st.session_state.c_code:
    st.session_state.c_code = c_code
    # Reset all outputs when code changes
    st.session_state.lexer_output = None
    st.session_state.parser_output = None
    st.session_state.semantic_output = None
    st.session_state.intermediate_code = None
    st.session_state.optimized_code = None
    st.session_state.generated_code = None
    st.session_state.execution_output = None
    st.session_state.symbol_table = None
    st.session_state.errors = {}

# Create tabs for different phases
tab_titles = [
    "Análisis Léxico", 
    "Análisis Sintáctico", 
    "Análisis Semántico", 
    "Código Intermedio", 
    "Optimización de Código", 
    "Generación de Código",
    "Ejecución"
]

tabs = st.tabs(tab_titles)

# Lexical Analysis Tab
with tabs[0]:
    st.header("Análisis Léxico")
    
    if st.button("Ejecutar Análisis Léxico"):
        lexer = Lexer(st.session_state.c_code)
        tokens, errors = lexer.tokenize()
        
        st.session_state.lexer_output = tokens
        if errors:
            st.session_state.errors['lexical'] = errors
        else:
            st.session_state.errors.pop('lexical', None)
    
    if st.session_state.lexer_output is not None:
        if 'lexical' in st.session_state.errors:
            st.error("🔍 Errores léxicos encontrados:")
            error_container = st.container()
            with error_container:
                for error in st.session_state.errors['lexical']:
                    st.error(error)
                    # Intentar resaltar el error en el código
                    try:
                        highlight_error_in_code(st.session_state.c_code, error)
                    except:
                        pass
        else:
            st.success("✅ Análisis léxico completado correctamente")
            
            # Display tokens in a table
            tokens_df = pd.DataFrame(st.session_state.lexer_output)
            if not tokens_df.empty:
                st.write("Tokens:")
                st.dataframe(tokens_df)
            else:
                st.write("No tokens generated.")

# Syntax Analysis Tab
with tabs[1]:
    st.header("Análisis Sintáctico")
    
    syntax_option = st.selectbox(
        "Seleccione tipo de análisis sintáctico",
        ["Variables y Constantes", "Expresiones", "Estructuras de Control", "Métodos y Clases"]
    )
    
    if st.button("Ejecutar Análisis Sintáctico"):
        if st.session_state.lexer_output is None:
            st.warning("¡Por favor ejecute primero el Análisis Léxico!")
        else:
            parser = Parser(st.session_state.lexer_output)
            
            if syntax_option == "Variables y Constantes":
                ast, errors = parser.parse_variables()
            elif syntax_option == "Expresiones":
                ast, errors = parser.parse_expressions()
            elif syntax_option == "Estructuras de Control":
                ast, errors = parser.parse_control_structures()
            else:  # Métodos y Clases
                ast, errors = parser.parse_methods_classes()
            
            st.session_state.parser_output = ast
            
            if errors:
                st.session_state.errors['syntax'] = errors
            else:
                st.session_state.errors.pop('syntax', None)
    
    if st.session_state.parser_output is not None:
        if 'syntax' in st.session_state.errors:
            st.error("🔍 Errores sintácticos encontrados:")
            error_container = st.container()
            with error_container:
                for error in st.session_state.errors['syntax']:
                    st.error(error)
                    # Intentar resaltar el error en el código
                    try:
                        highlight_error_in_code(st.session_state.c_code, error)
                    except:
                        pass
        else:
            st.success("✅ Análisis sintáctico completado correctamente")
            
            # Visualize AST as a graph
            st.write("Árbol de Sintaxis Abstracta:")
            graph = st.session_state.parser_output.get('graph', None)
            if graph:
                fig = visualize_graph(graph)
                st.pyplot(fig)
            
            # Display parsed elements in a structured format
            elements = st.session_state.parser_output.get('elements', [])
            if elements:
                st.write("Elementos Analizados:")
                for elem in elements:
                    st.text(f"{elem['type']}: {elem['value']}")

# Semantic Analysis Tab
with tabs[2]:
    st.header("Análisis Semántico")
    
    semantic_option = st.selectbox(
        "Seleccione tipo de análisis semántico",
        ["Gestión de Tabla de Símbolos", "Verificación de Tipos", "Verificación de Expresiones", "Verificación de Flujo de Control"]
    )
    
    if st.button("Ejecutar Análisis Semántico"):
        if st.session_state.parser_output is None:
            st.warning("¡Por favor ejecute primero el Análisis Sintáctico!")
        else:
            analyzer = SemanticAnalyzer(st.session_state.parser_output)
            
            if semantic_option == "Gestión de Tabla de Símbolos":
                result, symbol_table, errors = analyzer.analyze_symbols()
                st.session_state.symbol_table = symbol_table
            elif semantic_option == "Verificación de Tipos":
                result, errors = analyzer.type_check()
            elif semantic_option == "Verificación de Expresiones":
                result, errors = analyzer.verify_expressions()
            else:  # Verificación de Flujo de Control
                result, errors = analyzer.verify_control_flow()
            
            st.session_state.semantic_output = result
            
            if errors:
                st.session_state.errors['semantic'] = errors
            else:
                st.session_state.errors.pop('semantic', None)
    
    if st.session_state.semantic_output is not None:
        if 'semantic' in st.session_state.errors:
            st.error("🔍 Errores semánticos encontrados:")
            error_container = st.container()
            with error_container:
                for error in st.session_state.errors['semantic']:
                    st.error(error)
                    # Intentar resaltar el error en el código
                    try:
                        highlight_error_in_code(st.session_state.c_code, error)
                    except:
                        pass
        else:
            st.success("✅ Análisis semántico completado correctamente")
            
            # Show Symbol Table
            if semantic_option == "Gestión de Tabla de Símbolos" and st.session_state.symbol_table is not None:
                st.write("Tabla de Símbolos:")
                symbol_df = pd.DataFrame(st.session_state.symbol_table)
                st.dataframe(symbol_df)
            
            # Show other semantic analysis results
            st.write("Resultado del Análisis Semántico:")
            st.json(st.session_state.semantic_output)

# Intermediate Code Tab
with tabs[3]:
    st.header("Generación de Código Intermedio")
    
    # Mostrar ejemplos de código intermedio
    with st.expander("Ver Ejemplos de Generación de Código Intermedio"):
        st.markdown("""
        ### Asignación de Constantes a Variables
        Instrucciones para asignar valores constantes a variables. Cada constante se representa mediante una etiqueta temporal en el código intermedio.
        
        **Código Fuente:**
        ```c
        x = 5;
        y = 10;
        ```
        
        **Código Intermedio:**
        ```
        t1 = 5       # t1 es una etiqueta temporal que representa la constante 5
        x = t1       # Asigna el valor de t1 a x
         
        t2 = 10      # t2 es una etiqueta temporal que representa la constante 10
        y = t2       # Asigna el valor de t2 a y
        ```
        
        ### Uso de Variables
        Cuando se utilizan variables, el código intermedio refleja las operaciones que se realizan sobre ellas.
        
        **Código Fuente:**
        ```c
        z = x + y;
        ```
        
        **Código Intermedio:**
        ```
        t3 = x + y    # t3 es una etiqueta temporal que representa la suma de x e y
        z = t3        # Asigna el valor de t3 a z
        ```
        
        ### Expresiones Aritméticas
        Conversión de operaciones aritméticas en instrucciones intermedias.
        
        **Código Fuente:**
        ```c
        result = a * (b + c);
        ```
        
        **Código Intermedio:**
        ```
        t4 = b + c    # t4 es una etiqueta temporal que representa la suma de b y c
        t5 = a * t4   # t5 es una etiqueta temporal que representa la multiplicación de a por t4
        result = t5   # Asigna el valor de t5 a result
        ```
        
        ### Expresiones Lógicas
        Transformación de expresiones lógicas en instrucciones intermedias.
        
        **Código Fuente:**
        ```c
        flag = (x > y) && (z < 10);
        ```
        
        **Código Intermedio:**
        ```
        t6 = x > y    # t6 es una etiqueta temporal para la comparación x > y
        t7 = z < 10   # t7 es una etiqueta temporal para la comparación z < 10
        t8 = t6 && t7  # t8 toma el valor de la operación lógica AND entre t6 y t7
        flag = t8     # Asigna el valor de t8 a flag
        ```
        
        ### Gestión de Errores y Validaciones
        
        **Código Fuente:**
        ```c
        result = a / b;
        ```
        
        **Código Intermedio:**
        ```
        if b == 0 then error "Division by zero" # Valida que no se realice división por cero
        t9 = a / b    # t9 es una etiqueta temporal para la división de a entre b
        result = t9   # Asigna el valor de t9 a result
        ```
        """)
    
    if st.button("Generar Código Intermedio"):
        if st.session_state.semantic_output is None:
            st.warning("¡Por favor ejecute primero el Análisis Semántico!")
        else:
            ic_generator = IntermediateCodeGenerator(st.session_state.parser_output, st.session_state.symbol_table)
            intermediate_code, errors = ic_generator.generate()
            
            st.session_state.intermediate_code = intermediate_code
            
            if errors:
                st.session_state.errors['intermediate'] = errors
            else:
                st.session_state.errors.pop('intermediate', None)
    
    if st.session_state.intermediate_code is not None:
        if 'intermediate' in st.session_state.errors:
            st.error("Errores en la generación de código intermedio:")
            for error in st.session_state.errors['intermediate']:
                st.text(error)
        else:
            st.success("✅ Código intermedio generado correctamente")
            
            # Display the intermediate code
            st.write("Código Intermedio Generado:")
            st.code(st.session_state.intermediate_code, language="c")
            
            # Visualize control flow graph
            st.write("Gráfico de Flujo de Control:")
            ic_generator = IntermediateCodeGenerator(st.session_state.parser_output, st.session_state.symbol_table)
            cfg = ic_generator.generate_control_flow_graph()
            if cfg:
                fig = visualize_graph(cfg)
                st.pyplot(fig)

# Code Optimization Tab
with tabs[4]:
    st.header("Optimización de Código")
    
    optimization_level = st.slider("Nivel de Optimización", 0, 3, 1)
    
    if st.button("Optimizar Código"):
        if st.session_state.intermediate_code is None:
            st.warning("¡Por favor genere primero el Código Intermedio!")
        else:
            optimizer = CodeOptimizer(st.session_state.intermediate_code, optimization_level)
            optimized_code, optimizations = optimizer.optimize()
            
            st.session_state.optimized_code = optimized_code
            st.session_state.optimizations = optimizations
    
    if st.session_state.optimized_code is not None:
        st.success("✅ Optimización de código completada")
        
        # Display optimized code
        st.write("Código Optimizado:")
        st.code(st.session_state.optimized_code, language="c")
        
        # Show optimization details
        st.write("Optimizaciones Aplicadas:")
        for opt in st.session_state.optimizations:
            st.text(f"- {opt}")

# Code Generation Tab
with tabs[5]:
    st.header("Generación de Código")
    
    target_architecture = st.selectbox(
        "Seleccione Arquitectura Objetivo",
        ["x86", "x86_64", "ARM"]
    )
    
    if st.button("Generar Código Objetivo"):
        if st.session_state.optimized_code is None:
            if st.session_state.intermediate_code is None:
                st.warning("¡Por favor genere primero el Código Intermedio!")
            else:
                # Use intermediate code if optimized code is not available
                code_gen = CodeGenerator(st.session_state.intermediate_code, target_architecture)
                target_code, errors = code_gen.generate()
                
                st.session_state.generated_code = target_code
                
                if errors:
                    st.session_state.errors['code_gen'] = errors
                else:
                    st.session_state.errors.pop('code_gen', None)
        else:
            # Use optimized code if available
            code_gen = CodeGenerator(st.session_state.optimized_code, target_architecture)
            target_code, errors = code_gen.generate()
            
            st.session_state.generated_code = target_code
            

            
            if errors:
                st.session_state.errors['code_gen'] = errors
            else:
                st.session_state.errors.pop('code_gen', None)
    
    if st.session_state.generated_code is not None:
        if 'code_gen' in st.session_state.errors:
            st.error("Errores en la generación de código:")
            for error in st.session_state.errors['code_gen']:
                st.text(error)
        else:
            st.success("✅ Generación de código completada correctamente")
            
            # Display the target code
            st.write(f"Código {target_architecture} Generado:")
            st.code(st.session_state.generated_code, language="asm")

# Execution Tab
with tabs[6]:
    st.header("Ejecución de Código")
    
    if st.button("Ejecutar Código"):
        if st.session_state.c_code:
            executor = Executor(st.session_state.c_code)
            output, errors = executor.execute()
            
            st.session_state.execution_output = output
            
            if errors:
                st.session_state.errors['execution'] = errors
            else:
                st.session_state.errors.pop('execution', None)
    
    if 'execution_output' in st.session_state and st.session_state.execution_output is not None:
        if 'execution' in st.session_state.errors:
            st.error("Errores de ejecución:")
            for error in st.session_state.errors['execution']:
                st.text(error)
        else:
            st.success("✅ Código ejecutado correctamente")
            
            # Display execution output
            st.write("Salida del Programa:")
            st.code(st.session_state.execution_output)

# Add footer
st.markdown("---")
st.markdown("Compilador de C basado en Python - Proyecto de Construcción de Compiladores")
