// Main script for the C compiler web interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CodeMirror editor
    const editor = CodeMirror.fromTextArea(document.getElementById('code-input'), {
        lineNumbers: true,
        mode: 'text/x-csrc',
        theme: 'darcula',
        indentUnit: 4,
        smartIndent: true,
        tabSize: 4,
        indentWithTabs: false,
        autoCloseBrackets: true,
        matchBrackets: true,
        extraKeys: {
            "Ctrl-Space": "autocomplete"
        }
    });

    // Set initial height
    editor.setSize(null, 400);

    // Sample C code for when the page loads
    const sampleCode = `// Sample C code


int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int num = 5;
    int result = factorial(num);
    printf("Factorial of %d is %d\\n", num, result);
    return 0;
}`;

    editor.setValue(sampleCode);

    // Handle tab navigation
    const tabs = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-pane');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // Get target attribute safely
            const target = this.getAttribute('data-bs-target');
            if (!target) {
                console.error('Tab has no data-bs-target attribute');
                return;
            }
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active', 'show'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            const targetId = target.substring(1); // remove the # character
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.classList.add('active', 'show');
            } else {
                console.error('Target element not found:', targetId);
            }
        });
    });

    // Compile button event handler
    document.getElementById('compile-btn').addEventListener('click', function() {
        const code = editor.getValue();
        if (!code.trim()) {
            showAlert('Please enter some C code first.', 'danger');
            return;
        }

        // Show loading state
        showLoader();
        
        // Send code to server for compilation
        fetch('/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            hideLoader();
            
            // Process compilation results
            processCompilationResults(data);
            
            // Activate lexical analysis tab to show results
            const lexicalTab = document.querySelector('.nav-link[data-bs-target="#lexical"]');
            if (lexicalTab) {
                lexicalTab.click();
            } else {
                console.error('Lexical analysis tab not found');
            }
        })
        .catch(error => {
            hideLoader();
            showAlert('Error during compilation: ' + error.message, 'danger');
        });
    });

    // Individual phase buttons
    document.querySelectorAll('.phase-btn').forEach(button => {
        button.addEventListener('click', function() {
            const phaseId = this.getAttribute('data-target');
            if (!phaseId) {
                console.error('Phase button has no data-target attribute');
                return;
            }
            
            const tabLink = document.querySelector(`.nav-link[data-bs-target="#${phaseId}"]`);
            if (tabLink) {
                tabLink.click();
            } else {
                console.error('Tab link not found for phase:', phaseId);
            }
        });
    });

    // Clear button event handler
    document.getElementById('clear-btn').addEventListener('click', function() {
        editor.setValue('');
        
        // Clear all results
        document.querySelectorAll('.result-container').forEach(container => {
            container.innerHTML = '';
        });
        
        document.querySelectorAll('.phase-status').forEach(status => {
            status.innerHTML = '<span class="badge bg-secondary">Not started</span>';
        });
    });

    // Function to process compilation results
    function processCompilationResults(data) {
        // Update status for each phase
        updatePhaseStatus('lexical', data.lexical);
        updatePhaseStatus('syntax', data.syntax);
        updatePhaseStatus('semantic', data.semantic);
        updatePhaseStatus('intermediate', data.intermediate);
        updatePhaseStatus('optimization', data.optimization);
        updatePhaseStatus('codegen', data.codegen);
        
        // Visualize each phase
        if (data.lexical && data.lexical.success) {
            visualizeLexicalAnalysis(data.lexical);
        }
        
        if (data.syntax && data.syntax.success) {
            visualizeSyntaxAnalysis(data.syntax);
        }
        
        if (data.semantic && data.semantic.success) {
            visualizeSemanticAnalysis(data.semantic);
        }
        
        if (data.intermediate && data.intermediate.success) {
            visualizeIntermediateCode(data.intermediate);
        }
        
        if (data.optimization && data.optimization.success) {
            visualizeOptimization(data.optimization);
        }
        
        if (data.codegen && data.codegen.success) {
            visualizeCodeGeneration(data.codegen);
        }
    }

    // Function to update phase status
    function updatePhaseStatus(phaseId, phaseData) {
        const statusElement = document.querySelector(`#${phaseId}-status`);
        if (!statusElement) return;
        
        if (!phaseData) {
            statusElement.innerHTML = '<span class="badge bg-secondary">Not started</span>';
            return;
        }
        
        if (phaseData.success) {
            statusElement.innerHTML = '<span class="badge bg-success">Success</span>';
        } else {
            const errorMsg = phaseData.error || 'Failed';
            statusElement.innerHTML = `<span class="badge bg-danger">Failed</span> <span class="text-danger">${errorMsg}</span>`;
        }
    }

    // Function to show loader
    function showLoader() {
        const loader = document.getElementById('compiler-loader');
        if (loader) {
            loader.style.display = 'flex';
        }
    }

    // Function to hide loader
    function hideLoader() {
        const loader = document.getElementById('compiler-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    // Function to show alert
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            console.error('Alert container not found');
            return;
        }
        
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertContainer.contains(alertDiv)) {
                    alertContainer.removeChild(alertDiv);
                }
            }, 150);
        }, 5000);
    }

    // Initial UI setup
    const initialTab = document.querySelector('.nav-link[data-bs-target="#code"]');
    if (initialTab) {
        initialTab.click();
    } else {
        console.error('Initial code tab not found');
    }
});

// Load examples dropdown
document.addEventListener('DOMContentLoaded', function() {
    const examples = [
        {
            name: "Hello World",
            code: `

int main() {
    printf("Hello, World!\\n");
    return 0;
}`
        },
        {
            name: "Factorial",
            code: `

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int num = 5;
    int result = factorial(num);
    printf("Factorial of %d is %d\\n", num, result);
    return 0;
}`
        },
        {
            name: "Fibonacci",
            code: `

int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int n = 10;
    printf("Fibonacci(%d) = %d\\n", n, fibonacci(n));
    return 0;
}`
        },
        {
            name: "Bubble Sort",
            code: `

void bubbleSort(int arr[], int n) {
    int i, j, temp;
    for (i = 0; i < n-1; i++) {
        for (j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                // Swap arr[j] and arr[j+1]
                temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}

int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(arr)/sizeof(arr[0]);
    int i;
    
    bubbleSort(arr, n);
    
    printf("Sorted array: \\n");
    for (i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
    
    return 0;
}`
        },
        {
            name: "Syntax Error Example",
            code: `

int main() {
    // Missing semicolon
    int x = 10
    
    printf("Value: %d\\n", x);
    
    // Unmatched bracket
    if (x > 5) {
        printf("x is greater than 5\\n");
    
    return 0;
}`
        }
    ];

    const examplesDropdown = document.getElementById('examples-dropdown');
    if (!examplesDropdown) return;

    examples.forEach(example => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.className = 'dropdown-item';
        link.href = '#';
        link.textContent = example.name;
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const editor = document.querySelector('.CodeMirror').CodeMirror;
            editor.setValue(example.code);
        });
        item.appendChild(link);
        examplesDropdown.appendChild(item);
    });
});
