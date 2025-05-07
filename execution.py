import tempfile
import os
import subprocess
from pathlib import Path

class Executor:
    """
    Execute C code for the compiler.
    Uses system tools (GCC) to compile and run the code.
    """
    
    def __init__(self, c_code):
        self.c_code = c_code
        self.temp_dir = None
        self.c_file = None
        self.executable = None
        self.errors = []
    
    def execute(self):
        """
        Compile and execute the C code.
        
        Returns:
            tuple: (output, errors) where output is the program's stdout
                  and errors is a list of error messages.
        """
        # Reset state
        self.errors = []
        
        try:
            # Create temporary directory for files
            self.temp_dir = tempfile.TemporaryDirectory()
            
            # Write C code to temporary file
            self.c_file = Path(self.temp_dir.name) / "program.c"
            with open(self.c_file, 'w') as f:
                f.write(self.c_code)
            
            # Compile the code
            compile_result, compile_errors = self._compile()
            if compile_errors:
                self.errors.append(f"Compilation failed: {compile_errors}")
                print("COMPILATION ERROR:", compile_errors)  # <- AÑADE ESTA LÍNEA
                return "", self.errors
            
            # Run the compiled program
            run_output, run_errors = self._run()
            if run_errors:
                self.errors.append(f"Runtime error: {run_errors}")
            
            return run_output, self.errors
        
        except Exception as e:
            self.errors.append(f"Execution error: {str(e)}")
            return "", self.errors
        
        finally:
            # Clean up temporary files
            self._cleanup()
    
    def _compile(self):
        """
        Compile the C code using GCC.
        
        Returns:
            tuple: (result, error) where result is True if compilation succeeded
                  and error is any error message.
        """
        try:
            # Ensure temp_dir exists
            if not self.temp_dir:
                self.temp_dir = tempfile.TemporaryDirectory()
                
            # Set up the executable path
            # Set up the executable path
            exe_name = "program.exe" if os.name == "nt" else "program"
            self.executable = Path(self.temp_dir.name) / exe_name
            
            # Check if GCC is installed
            gcc_check = subprocess.run(
                ["gcc", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            
            # If GCC is not installed, simulate compilation for educational purposes
            if gcc_check.returncode != 0:
                # Check if code compiles (basic syntax check)
                if "int main" not in self.c_code:
                    return False, "El código debe contener una función main"
                
                # Create a dummy executable marker file
                with open(str(self.executable), 'w') as f:
                    f.write("dummy_executable")
                
                return True, None
            
            # Compile with GCC if available
            process = subprocess.run(
                ["gcc", str(self.c_file), "-o", str(self.executable), "-Wall"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                return False, process.stderr
            
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    def _run(self):
        """
        Run the compiled executable.
        
        Returns:
            tuple: (output, error) where output is the program's stdout
                  and error is any error message.
        """
        try:
            # Ensure executable is set
            if self.executable is None:
                return "", "Executable not found"
                
            # Check if executable exists
            if not os.path.exists(str(self.executable)):
                return "", "Executable not found"
            
            # Check if it's our simulated executable
            try:
                with open(str(self.executable), 'r') as f:
                    content = f.read()
                    if content.strip() == "dummy_executable":
                        # Simulate program execution by analyzing the code
                        return self._simulate_execution(), None
            except:
                # If we can't read the file, assume it's a binary executable
                pass
            
            # Make sure the file is executable
            os.chmod(str(self.executable), 0o755)
            
            # Run the program with a timeout
            process = subprocess.run(
                [str(self.executable)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,  # 5 second timeout to prevent infinite loops
                check=False
            )
            
            if process.returncode != 0:
                return process.stdout, process.stderr
            
            return process.stdout, None
        
        except subprocess.TimeoutExpired:
            return "", "Program execution timed out (possible infinite loop)"
        
        except Exception as e:
            return "", str(e)
            
    def _simulate_execution(self):
        """
        Simulate program execution for educational purposes.
        Analyzes the code and returns expected output.
        """
        # Extract printf statements from the code
        output = []
        lines = self.c_code.split('\n')
        
        for line in lines:
            # Look for printf statements
            if 'printf' in line and '"' in line:
                # Extract the string between quotes
                start = line.find('"') + 1
                end = line.find('"', start)
                if start > 0 and end > start:
                    # Replace escape sequences
                    text = line[start:end].replace('\\n', '\n').replace('\\t', '\t')
                    output.append(text)
        
        # If there are no printf statements, provide a default output
        if not output:
            return "(Simulación) Programa ejecutado correctamente, pero no produce salida visible."
        
        return "(Simulación) " + ''.join(output)
    
    def _cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir:
                self.temp_dir.cleanup()
        except:
            pass
    
    def get_assembly(self):
        """
        Generate assembly output for the C code.
        
        Returns:
            tuple: (assembly, errors) where assembly is the generated assembly code
                  and errors is a list of error messages.
        """
        try:
            # Check if GCC is installed
            gcc_check = subprocess.run(
                ["which", "gcc"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # If GCC is not installed, simulate assembly generation
            if gcc_check.returncode != 0:
                return self._simulate_assembly(), []
            
            # Create temporary directory if needed
            if not self.temp_dir:
                self.temp_dir = tempfile.TemporaryDirectory()
            
            # Write C code to temporary file
            self.c_file = Path(self.temp_dir.name) / "program.c"
            with open(self.c_file, 'w') as f:
                f.write(self.c_code)
            
            # Generate assembly with GCC
            asm_file = Path(self.temp_dir.name) / "program.s"
            process = subprocess.run(
                ["gcc", "-S", str(self.c_file), "-o", str(asm_file), "-Wall"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                return "", [process.stderr]
            
            # Read the assembly file
            with open(asm_file, 'r') as f:
                assembly = f.read()
            
            return assembly, []
        
        except Exception as e:
            return "", [f"Assembly generation error: {str(e)}"]
        
        finally:
            # Clean up temporary files
            self._cleanup()
            
    def _simulate_assembly(self):
        """
        Simulate assembly code generation for educational purposes.
        Returns a representative assembly code for the given C code.
        """
        # Create a basic assembly template
        assembly = f"""; Código Ensamblador Simulado para fines educativos
; Generado a partir de ejemplo de código C
; Nota: Este es un ejemplo simplificado y no representa el código real que sería generado

.text
.globl main
main:
    ; Prólogo de la función
    pushq   %rbp
    movq    %rsp, %rbp
    subq    $16, %rsp        ; Reservar espacio para variables locales
"""
        
        # Add variable declarations if detected
        variables = []
        for line in self.c_code.split('\n'):
            if 'int ' in line and '=' in line and ';' in line:
                var_name = line.split('int')[1].split('=')[0].strip()
                var_value = line.split('=')[1].split(';')[0].strip()
                if var_name and var_value:
                    variables.append((var_name, var_value))
                    assembly += f"\n    ; Inicializar {var_name} = {var_value}\n"
                    assembly += f"    movl    ${var_value}, -{len(variables)*4}(%rbp)\n"
        
        # Add printf calls if detected
        for line in self.c_code.split('\n'):
            if 'printf' in line and '"' in line:
                start = line.find('"') + 1
                end = line.find('"', start)
                if start > 0 and end > start:
                    string_content = line[start:end]
                    assembly += f"\n    ; Llamada a printf(\"{string_content}\")\n"
                    assembly += f"    leaq    .LC0(%rip), %rdi\n"
                    assembly += f"    call    printf@PLT\n"
        
        # Add function epilogue
        assembly += f"""
    ; Epílogo de la función
    movl    $0, %eax        ; Código de retorno = 0
    leave
    ret

.section .rodata
.LC0:
    .string "(Simulación de código ensamblador)"
"""
        
        return assembly
