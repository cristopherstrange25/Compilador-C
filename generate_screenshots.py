import os
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_example_screenshots():
    """
    Genera imágenes de ejemplo para cada fase del compilador.
    En un entorno real, estas serían capturas de pantalla reales,
    pero aquí las simulamos para fines ilustrativos.
    """
    # Asegúrate de que exista el directorio
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    # Tamaño común para las capturas
    width, height = 800, 600
    
    # Colores
    background_color = (240, 240, 240)
    header_color = (70, 130, 180)
    text_color = (0, 0, 0)
    code_bg_color = (250, 250, 250)
    code_border_color = (200, 200, 200)
    
    # Fuente (usamos una fuente por defecto si no está disponible)
    try:
        font = ImageFont.truetype("Arial", 16)
        font_title = ImageFont.truetype("Arial", 24)
        font_code = ImageFont.truetype("Courier", 14)
    except:
        font = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_code = ImageFont.load_default()
    
    # Fases del compilador
    phases = [
        "Análisis Léxico",
        "Análisis Sintáctico",
        "Análisis Semántico",
        "Código Intermedio",
        "Optimización",
        "Generación de Código",
        "Ejecución"
    ]
    
    # Ejemplos de código y resultados
    examples = {
        "Análisis Léxico": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": '[{"type": "INT", "value": "int", "line": 1},\n{"type": "ID", "value": "main", "line": 1},\n...]'
        },
        "Análisis Sintáctico": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": '{"type": "program",\n  "body": [\n    {"type": "function_declaration", "name": "main", ...}\n  ]\n}'
        },
        "Análisis Semántico": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": 'Variables:\n  x: {type: int, initialized: true, scope: main}\n\nFunciones:\n  main: {return_type: int, params: []}'
        },
        "Código Intermedio": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": 'FUNCTION_BEGIN main\n  t1 = 10\n  x = t1\n  PARAM "Valor: %d\\n"\n  PARAM x\n  t2 = CALL printf, 2\n  t3 = 0\n  RETURN t3\nFUNCTION_END'
        },
        "Optimización": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": 'FUNCTION_BEGIN main\n  x = 10\n  PARAM "Valor: %d\\n"\n  PARAM x\n  CALL printf, 2\n  RETURN 0\nFUNCTION_END'
        },
        "Generación de Código": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": '.globl main\nmain:\n    pushq %rbp\n    movq %rsp, %rbp\n    subq $16, %rsp\n    movl $10, -4(%rbp)\n    ...'
        },
        "Ejecución": {
            "code": 'int main() {\n    int x = 10;\n    printf("Valor: %d\\n", x);\n    return 0;\n}',
            "output": '(Simulación) Valor: 10\n'
        }
    }
    
    screenshots = {}
    
    # Generar una captura para cada fase
    for phase in phases:
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Dibujar encabezado
        draw.rectangle((0, 0, width, 60), fill=header_color)
        draw.text((width//2, 30), f"Compilador de C - {phase}", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        # Dibujar separadores de secciones
        draw.line(((0, 130), (width, 130)), fill=(200, 200, 200), width=2)
        draw.line(((width//2, 130), (width//2, height)), fill=(200, 200, 200), width=2)
        
        # Dibujar sección de código de entrada
        draw.text((20, 80), "Código Fuente:", font=font, fill=text_color)
        draw.rectangle((20, 100, width//2 - 20, 300), fill=code_bg_color, outline=code_border_color)
        
        # Agregar código de ejemplo
        y_pos = 110
        for line in examples[phase]["code"].split('\n'):
            draw.text((30, y_pos), line, font=font_code, fill=text_color)
            y_pos += 20
        
        # Dibujar sección de resultados
        draw.text((width//2 + 20, 80), f"Resultados del {phase}:", font=font, fill=text_color)
        draw.rectangle((width//2 + 20, 100, width - 20, 500), fill=code_bg_color, outline=code_border_color)
        
        # Agregar resultado de ejemplo
        y_pos = 110
        for line in examples[phase]["output"].split('\n'):
            draw.text((width//2 + 30, y_pos), line, font=font_code, fill=text_color)
            y_pos += 20
        
        # Guardar la imagen
        file_path = f"screenshots/{phase.lower().replace(' ', '_')}.png"
        img.save(file_path)
        screenshots[phase] = file_path
        print(f"Generada captura de pantalla simulada para {phase}")
    
    # Generar una captura de la interfaz completa
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Dibujar encabezado
    draw.rectangle((0, 0, width, 60), fill=header_color)
    draw.text((width//2, 30), "Compilador de C basado en Python", font=font_title, fill=(255, 255, 255), anchor="mm")
    
    # Dibujar pestañas
    tab_width = width // len(phases)
    for i, phase in enumerate(phases):
        if i == 0:  # Seleccionada por defecto
            draw.rectangle((i*tab_width, 60, (i+1)*tab_width, 90), fill=(100, 150, 200))
        else:
            draw.rectangle((i*tab_width, 60, (i+1)*tab_width, 90), fill=(150, 180, 220))
        draw.text(((i+0.5)*tab_width, 75), phase, font=font, fill=(0, 0, 0), anchor="mm")
    
    # Dibujar área principal
    draw.rectangle((20, 100, width - 20, 500), fill=code_bg_color, outline=code_border_color)
    
    # Guardar la imagen
    file_path = "screenshots/interfaz_completa.png"
    img.save(file_path)
    screenshots["Interfaz"] = file_path
    print("Generada captura de pantalla simulada de la interfaz completa")
    
    return screenshots

def enhance_pdf_with_screenshots(screenshots):
    """
    Mejora el PDF existente agregando las capturas de pantalla.
    """
    # Definir estilos
    styles = getSampleStyleSheet()
    # Modificar estilos existentes
    styles['Title'].fontSize = 18
    styles['Title'].spaceAfter = 12
    # Añadir nuevos estilos
    custom_heading2 = ParagraphStyle(name='CustomHeading2', parent=styles['Heading1'], fontSize=14, spaceBefore=10, spaceAfter=6)
    custom_heading3 = ParagraphStyle(name='CustomHeading3', parent=styles['Heading1'], fontSize=12, spaceBefore=8, spaceAfter=4)
    custom_code = ParagraphStyle(name='CustomCode', fontName='Courier', fontSize=9, spaceBefore=6, spaceAfter=6, leftIndent=20, rightIndent=20, backColor=colors.lightgrey)
    styles.add(custom_heading2)
    styles.add(custom_heading3)
    styles.add(custom_code)
    styles['Normal'].spaceBefore = 6
    styles['Normal'].spaceAfter = 6
    
    # Crear documento
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Contenido del PDF
    content = []
    
    # Título
    content.append(Paragraph("Manual con Capturas - Compilador de C basado en Python", styles['Title']))
    content.append(Spacer(1, 0.25 * inch))
    
    # Añadir captura de la interfaz completa
    content.append(Paragraph("Vista General de la Interfaz", styles['CustomHeading2']))
    content.append(Paragraph("La interfaz principal del compilador está organizada en pestañas, cada una correspondiente a una fase del proceso de compilación:", styles['Normal']))
    img = ReportLabImage(screenshots["Interfaz"], width=6*inch, height=4.5*inch)
    content.append(img)
    content.append(Spacer(1, 0.25 * inch))
    
    # Añadir capturas de cada fase
    phases = [
        "Análisis Léxico",
        "Análisis Sintáctico",
        "Análisis Semántico",
        "Código Intermedio",
        "Optimización",
        "Generación de Código",
        "Ejecución"
    ]
    
    phase_descriptions = {
        "Análisis Léxico": "El analizador léxico identifica tokens en el código fuente C. Los tokens incluyen palabras clave, identificadores, operadores, constantes, etc.",
        "Análisis Sintáctico": "El analizador sintáctico verifica la estructura del código según las reglas gramaticales del lenguaje C. Construye un árbol de sintaxis abstracta (AST).",
        "Análisis Semántico": "El analizador semántico verifica la coherencia del significado del código. Confirma que los tipos de datos sean compatibles y que las variables estén declaradas.",
        "Código Intermedio": "El generador de código intermedio produce una representación independiente de la máquina del código fuente, usando un formato de tres direcciones.",
        "Optimización": "El optimizador de código mejora el código intermedio para hacerlo más eficiente, aplicando técnicas como propagación de constantes y eliminación de código muerto.",
        "Generación de Código": "El generador de código convierte el código intermedio optimizado en código ensamblador específico para la arquitectura objetivo.",
        "Ejecución": "La fase de ejecución compila y ejecuta el código generado para mostrar la salida del programa."
    }
    
    for i, phase in enumerate(phases):
        # Agregar salto de página excepto para la primera fase
        if i > 0:
            content.append(PageBreak())
        
        content.append(Paragraph(f"{i+1}. {phase}", styles['CustomHeading2']))
        content.append(Paragraph(phase_descriptions[phase], styles['Normal']))
        
        # Añadir la imagen
        img = ReportLabImage(screenshots[phase], width=6*inch, height=4.5*inch)
        content.append(img)
        content.append(Spacer(1, 0.25 * inch))
        
        # Para algunas fases, agregar más detalles
        if phase == "Análisis Léxico":
            content.append(Paragraph("Tokens identificados en el código:", styles['CustomHeading3']))
            content.append(Paragraph("El análisis léxico identifica cada componente del código como un token con tipo, valor y posición. Esta información es crucial para detectar errores léxicos como identificadores inválidos o caracteres no reconocidos.", styles['Normal']))
        
        elif phase == "Análisis Sintáctico":
            content.append(Paragraph("Estructura del AST generado:", styles['CustomHeading3']))
            content.append(Paragraph("El Árbol de Sintaxis Abstracta (AST) representa la estructura jerárquica del código. El analizador sintáctico puede detectar problemas como paréntesis desbalanceados o puntos y coma faltantes.", styles['Normal']))
        
        elif phase == "Análisis Semántico":
            content.append(Paragraph("Verificación de tipos y ámbitos:", styles['CustomHeading3']))
            content.append(Paragraph("El análisis semántico verifica que las variables sean usadas de manera consistente con sus tipos declarados y que estén en el ámbito correcto. También verifica la compatibilidad de tipos en expresiones y asignaciones.", styles['Normal']))
    
    # Crear el PDF
    doc.build(content)
    
    # Guardar el PDF
    with open("manual_con_capturas.pdf", "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    print("Manual con capturas generado correctamente: manual_con_capturas.pdf")

if __name__ == "__main__":
    print("Generando capturas de pantalla simuladas...")
    screenshots = generate_example_screenshots()
    
    print("Mejorando el PDF con las capturas...")
    enhance_pdf_with_screenshots(screenshots)
    
    print("Proceso completo. Se han generado los siguientes archivos:")
    print("1. manual_compilador.pdf - Manual básico")
    print("2. manual_con_capturas.pdf - Manual con capturas de pantalla")