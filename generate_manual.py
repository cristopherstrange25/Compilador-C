import os
import requests
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
from io import BytesIO
import time

# Definir estilos
styles = getSampleStyleSheet()
# Modificar estilos existentes
styles['Title'].fontSize = 18
styles['Title'].spaceAfter = 12
# Usar los estilos existentes con nuevos nombres
custom_heading2 = ParagraphStyle(name='CustomHeading2', parent=styles['Heading1'], fontSize=14, spaceBefore=10, spaceAfter=6)
custom_heading3 = ParagraphStyle(name='CustomHeading3', parent=styles['Heading1'], fontSize=12, spaceBefore=8, spaceAfter=4)
styles.add(custom_heading2)
styles.add(custom_heading3)
styles['Normal'].spaceBefore = 6
styles['Normal'].spaceAfter = 6
styles.add(ParagraphStyle(name='CustomCode', fontName='Courier', fontSize=9, spaceBefore=6, spaceAfter=6, leftIndent=20, rightIndent=20, backColor=colors.lightgrey))

# Crear documento
pdf_buffer = BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

# Contenido del PDF
content = []

# Título
content.append(Paragraph("Manual de Usuario - Compilador de C basado en Python", styles['Title']))
content.append(Spacer(1, 0.25 * inch))

# Introducción
content.append(Paragraph("Introducción", styles['CustomHeading2']))
content.append(Paragraph("""Este manual describe el funcionamiento de un compilador de C basado en Python con una interfaz web interactiva. El compilador permite visualizar cada fase del proceso de compilación, incluyendo análisis léxico, sintáctico, semántico, generación de código intermedio, optimización y ejecución. Esta herramienta está diseñada principalmente con fines educativos.""", styles['Normal']))
content.append(Spacer(1, 0.25 * inch))

# Captura de pantalla de la aplicación
try:
    # Intentar capturar la aplicación Streamlit (esto en realidad no funcionará en el entorno de Replit)
    # En su lugar, usaremos una descripción de la captura
    content.append(Paragraph("Vista General de la Aplicación", styles['CustomHeading2']))
    content.append(Paragraph("""La aplicación está organizada en pestañas, cada una correspondiente a una fase del proceso de compilación. La interfaz incluye:
    - Un editor de código C donde el usuario puede escribir o pegar código
    - Secciones de visualización de resultados para cada fase
    - Mensajes de error detallados con sugerencias
    - Visualizaciones gráficas para ayudar a entender el proceso de compilación""", styles['Normal']))
    content.append(Spacer(1, 0.25 * inch))
except Exception as e:
    content.append(Paragraph(f"No se pudo capturar la pantalla: {str(e)}", styles['Normal']))

# Descripción de cada fase
# 1. Análisis Léxico
content.append(Paragraph("1. Análisis Léxico", styles['CustomHeading2']))
content.append(Paragraph("""El analizador léxico identifica tokens en el código fuente C. Los tokens incluyen palabras clave, identificadores, operadores, constantes, etc. Esta fase detecta errores léxicos como caracteres no reconocidos o literales mal formados.""", styles['Normal']))

content.append(Paragraph("Ejemplo de código:", styles['CustomHeading3']))
code_example = """int main() {
    int x = 10;
    printf("Valor: %d\\n", x);
    return 0;
}"""
content.append(Paragraph(code_example, styles['CustomCode']))

content.append(Paragraph("Tokens generados:", styles['CustomHeading3']))
tokens_example = """[
    {'type': 'INT', 'value': 'int', 'line': 1, 'position': 1},
    {'type': 'ID', 'value': 'main', 'line': 1, 'position': 5},
    {'type': 'LPAREN', 'value': '(', 'line': 1, 'position': 9},
    {'type': 'RPAREN', 'value': ')', 'line': 1, 'position': 10},
    {'type': 'LBRACE', 'value': '{', 'line': 1, 'position': 12},
    ...
]"""
content.append(Paragraph(tokens_example, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# 2. Análisis Sintáctico
content.append(Paragraph("2. Análisis Sintáctico", styles['CustomHeading2']))
content.append(Paragraph("""El analizador sintáctico verifica la estructura del código según las reglas gramaticales del lenguaje C. Construye un árbol de sintaxis abstracta (AST) a partir de los tokens. Esta fase detecta errores como paréntesis desbalanceados, falta de puntos y coma, o estructuras de control mal formadas.""", styles['Normal']))

content.append(Paragraph("Ejemplo de AST generado:", styles['CustomHeading3']))
ast_example = """{
    "type": "program",
    "body": [
        {
            "type": "function_declaration",
            "name": "main",
            "return_type": "int",
            "params": [],
            "body": {
                "type": "block_statement",
                "body": [
                    {
                        "type": "variable_declaration",
                        "name": "x",
                        "data_type": "int",
                        "initial_value": {
                            "type": "literal",
                            "value": 10
                        }
                    },
                    ...
                ]
            }
        }
    ]
}"""
content.append(Paragraph(ast_example, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# 3. Análisis Semántico
content.append(Paragraph("3. Análisis Semántico", styles['CustomHeading2']))
content.append(Paragraph("""El analizador semántico verifica la coherencia del significado del código. Confirma que los tipos de datos sean compatibles en las operaciones y que las variables estén declaradas antes de su uso. Construye una tabla de símbolos para rastrear variables, funciones y sus atributos.""", styles['Normal']))

content.append(Paragraph("Ejemplo de tabla de símbolos:", styles['CustomHeading3']))
symbols_example = """{
    "variables": {
        "x": {
            "type": "int",
            "line_declared": 2,
            "scope": "main",
            "initialized": true
        }
    },
    "functions": {
        "main": {
            "return_type": "int",
            "parameters": [],
            "line_declared": 1
        },
        "printf": {
            "return_type": "int",
            "parameters": ["const char*", "..."],
            "line_declared": 0,
            "is_extern": true
        }
    }
}"""
content.append(Paragraph(symbols_example, styles['CustomCode']))
content.append(PageBreak())

# 4. Generación de Código Intermedio
content.append(Paragraph("4. Generación de Código Intermedio", styles['CustomHeading2']))
content.append(Paragraph("""El generador de código intermedio produce una representación independiente de la máquina del código fuente. Este código de tres direcciones es más fácil de optimizar y traducir a código de máquina.""", styles['Normal']))

content.append(Paragraph("Ejemplo de código intermedio:", styles['CustomHeading3']))
intermediate_code = """FUNCTION_BEGIN main
    t1 = 10
    x = t1
    PARAM "Valor: %d\n"
    PARAM x
    t2 = CALL printf, 2
    t3 = 0
    RETURN t3
FUNCTION_END"""
content.append(Paragraph(intermediate_code, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# 5. Optimización de Código
content.append(Paragraph("5. Optimización de Código", styles['CustomHeading2']))
content.append(Paragraph("""El optimizador de código mejora el código intermedio para hacerlo más eficiente. Aplica técnicas como propagación de constantes, eliminación de código muerto, y plegado de constantes.""", styles['Normal']))

content.append(Paragraph("Ejemplo de código optimizado:", styles['CustomHeading3']))
optimized_code = """FUNCTION_BEGIN main
    x = 10
    PARAM "Valor: %d\n"
    PARAM x
    CALL printf, 2
    RETURN 0
FUNCTION_END"""
content.append(Paragraph(optimized_code, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# 6. Generación de Código de Máquina
content.append(Paragraph("6. Generación de Código de Máquina", styles['CustomHeading2']))
content.append(Paragraph("""El generador de código convierte el código intermedio optimizado en código ensamblador específico para la arquitectura objetivo (como x86).""", styles['Normal']))

content.append(Paragraph("Ejemplo de código ensamblador:", styles['CustomHeading3']))
assembly_code = """; Código Ensamblador Simulado
.text
.globl main
main:
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $16, %rsp
    
    ; Inicializar x = 10
    movl    $10, -4(%rbp)
    
    ; Llamada a printf("Valor: %d\n")
    leaq    .LC0(%rip), %rdi
    movl    -4(%rbp), %esi
    call    printf@PLT
    
    ; Retornar 0
    movl    $0, %eax
    leave
    ret

.section .rodata
.LC0:
    .string "Valor: %d\n"
"""
content.append(Paragraph(assembly_code, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# 7. Ejecución
content.append(Paragraph("7. Ejecución", styles['CustomHeading2']))
content.append(Paragraph("""La fase de ejecución compila y ejecuta el código generado para mostrar la salida del programa. En entornos donde no está disponible el compilador real (como Replit), se proporciona una simulación educativa.""", styles['Normal']))

content.append(Paragraph("Ejemplo de salida:", styles['CustomHeading3']))
output_example = """(Simulación) Valor: 10
"""
content.append(Paragraph(output_example, styles['CustomCode']))
content.append(Spacer(1, 0.25 * inch))

# Detección de errores
content.append(PageBreak())
content.append(Paragraph("Detección de Errores", styles['CustomHeading2']))
content.append(Paragraph("""El compilador proporciona mensajes de error detallados en cada fase del proceso. Los mensajes incluyen:
- Número de línea y posición exacta del error
- Descripción del problema en lenguaje claro
- Sugerencias para la corrección
- Indicadores visuales que señalan el punto exacto del error""", styles['Normal']))

content.append(Paragraph("Ejemplos de errores comunes:", styles['CustomHeading3']))

# Tabla de errores comunes
error_data = [
    ["Tipo de Error", "Ejemplo", "Mensaje"],
    ["Error léxico", "int 2x = 10;", "Error léxico: Identificador inválido '2x' en línea 1, posición 5. Los identificadores deben comenzar con una letra o guion bajo."],
    ["Error sintáctico", "if (x > 0) {\nprint(x)\n}", "Error sintáctico: Falta punto y coma (;) después de 'print(x)' en línea 2."],
    ["Error semántico", "int x = \"hello\";", "Error semántico: No se puede asignar string a variable de tipo int en línea 1."],
]

table = Table(error_data, colWidths=[1.2*inch, 1.5*inch, 3*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))

content.append(table)
content.append(Spacer(1, 0.25 * inch))

# Características adicionales
content.append(Paragraph("Características Adicionales", styles['CustomHeading2']))
content.append(Paragraph("""El compilador incluye varias características adicionales que lo hacen ideal para entornos educativos:
- Interfaz completamente en español
- Visualización del flujo de control del programa
- Simulación de ejecución cuando el compilador real no está disponible
- Sugerencias contextuales para corregir errores comunes
- Ejemplos de código predefinidos para cada fase del compilador""", styles['Normal']))

# Crear el PDF
doc.build(content)

# Guardar el PDF
with open("manual_compilador.pdf", "wb") as f:
    f.write(pdf_buffer.getvalue())

print("Manual generado correctamente: manual_compilador.pdf")