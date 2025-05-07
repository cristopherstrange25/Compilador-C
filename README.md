# Manual de Usuario - Compilador de C basado en Python

## Introducción
Este manual describe el funcionamiento de un compilador de C basado en Python con una interfaz web interactiva. El compilador permite visualizar cada fase del proceso de compilación, incluyendo análisis léxico, sintáctico, semántico, generación de código intermedio, optimización y ejecución. Esta herramienta está diseñada principalmente con fines educativos.

## Vista General de la Aplicación
La aplicación está organizada en pestañas, cada una correspondiente a una fase del proceso de compilación. La interfaz incluye:
- Un editor de código C donde el usuario puede escribir o pegar código.
- Secciones de visualización de resultados para cada fase.
- Mensajes de error detallados con sugerencias.
- Visualizaciones gráficas para ayudar a entender el proceso de compilación.

---

## 1. Análisis Léxico
El análisis léxico es la primera fase del proceso de compilación. Se encarga de leer el código fuente y dividirlo en una secuencia de unidades léxicas llamadas *tokens*. Estos tokens representan elementos básicos como palabras clave, identificadores, operadores, literales numéricos y cadenas de texto.

Esta fase también detecta errores léxicos, tales como:
- Caracteres no válidos.
- Identificadores mal formados.
- Literales no cerrados correctamente.

---

## 2. Análisis Sintáctico
El análisis sintáctico valida la estructura gramatical del código fuente según las reglas del lenguaje C. A partir de los tokens generados en la fase anterior, se construye un Árbol de Sintaxis Abstracta (AST) que representa la organización jerárquica del programa.

En esta fase se detectan errores como:
- Paréntesis o llaves desbalanceadas.
- Ausencia de signos de puntuación como punto y coma.
- Uso incorrecto de estructuras de control.

---

## 3. Análisis Semántico
Durante el análisis semántico se verifica que el significado del programa sea coherente. Se comprueba, por ejemplo:
- Que todas las variables estén declaradas antes de su uso.
- Que los tipos de datos en operaciones y asignaciones sean compatibles.
- Que las funciones reciban argumentos válidos en cantidad y tipo.

Esta fase también genera la **tabla de símbolos**, que almacena información sobre variables, funciones, tipos, ámbitos, y estado de inicialización.

---

## 4. Generación de Código Intermedio
La generación de código intermedio traduce el Árbol de Sintaxis Abstracta en una representación más simple y abstracta, que no depende de una arquitectura específica. Esta representación facilita la optimización y posterior traducción a código de máquina. Usualmente se emplea código de tres direcciones para representar operaciones, asignaciones, llamadas a funciones, etc.

---

## 5. Optimización de Código
El optimizador transforma el código intermedio para mejorar su rendimiento y eficiencia. Entre las técnicas aplicadas se incluyen:
- Eliminación de código muerto.
- Propagación de constantes.
- Plegado de constantes.
- Reducción de expresiones redundantes.

El resultado es un código más compacto y rápido, sin modificar su funcionalidad.

---

## 6. Generación de Código de Máquina
Esta etapa traduce el código intermedio optimizado a código ensamblador o máquina, dirigido a una arquitectura específica (como x86). Esta representación ya puede ser ejecutada por el sistema operativo, directamente o a través de herramientas externas.

Incluye instrucciones de bajo nivel para manipulación de memoria, llamadas a funciones estándar, operaciones aritméticas, y control de flujo.

---

## 7. Ejecución
El compilador permite compilar y ejecutar el programa generado. En entornos donde no es posible una ejecución real (como plataformas web), se simula la ejecución para ilustrar el comportamiento esperado del programa. Esto permite a los usuarios observar el flujo del programa y los efectos de las instrucciones, incluso sin acceso a un compilador nativo.

---

## Detección de Errores
Durante cada fase del proceso, el compilador detecta errores específicos y proporciona mensajes detallados que incluyen:
- Tipo de error (léxico, sintáctico, semántico).
- Número de línea y posición del error.
- Descripción clara y sugerencia de corrección.
- Resaltado visual del error en el editor.

### Ejemplos de errores comunes:

| Tipo de Error   | Código                          | Mensaje                                                                      |
|------------------|--------------------------------|-------------------------------------------------------------------------------|
| Léxico           | `int 2x = 10;`                 | Identificador inválido '2x'. Debe comenzar con una letra o guion bajo.       |
| Sintáctico       | `if (x > 0) { print(x) }`      | Falta punto y coma después de `print(x)`.                                    |
| Semántico        | `int x = "hola";`              | No se puede asignar un string a una variable de tipo `int`.                  |

---

## Características Adicionales
- Interfaz completamente en español.
- Visualización del flujo de control del programa.
- Simulación de ejecución educativa en navegadores.
- Sugerencias inteligentes para corregir errores comunes.
- Ejemplos de código integrados para cada fase del proceso.
- Compatible con plataformas educativas y accesible desde la web.
