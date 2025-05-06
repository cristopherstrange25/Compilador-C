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
            # Set up the executable path
            exe_name = "program.exe" if os.name == "nt" else "program"
            self.executable = Path(self.temp_dir.name) / exe_name

            
            # Compile with GCC
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
            if not os.path.exists(self.executable):
                return "", "Executable not found"
            
            # Make sure the file is executable
            os.chmod(self.executable, 0o755)
            
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
