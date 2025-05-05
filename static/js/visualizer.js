// Visualization functions for compiler phases

/**
 * Visualize lexical analysis results
 * @param {Object} lexicalData - Lexical analysis data from the server
 */
function visualizeLexicalAnalysis(lexicalData) {
    console.log("visualizeLexicalAnalysis called with data:", lexicalData);
    
    const container = document.getElementById('lexical-result');
    if (!container) {
        console.error("Lexical result container not found");
        return;
    }
    
    container.innerHTML = '';
    
    // Add status alert
    if (lexicalData.success === true) {
        const successAlert = document.createElement('div');
        successAlert.className = 'alert alert-success';
        successAlert.textContent = 'El análisis léxico se completó correctamente.';
        container.appendChild(successAlert);
    } else if (lexicalData.success === false) {
        const failAlert = document.createElement('div');
        failAlert.className = 'alert alert-danger';
        failAlert.textContent = 'El análisis léxico falló. Revisa los errores a continuación.';
        container.appendChild(failAlert);
    }
    

    
    // Create tokens table
    const tokensTable = document.createElement('div');
    tokensTable.className = 'table-responsive mb-4';
    tokensTable.innerHTML = `
        <h5>Tokens</h5>
        <table class="table table-sm table-dark">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Line</th>
                    <th>Position</th>
                </tr>
            </thead>
            <tbody id="tokens-tbody">
            </tbody>
        </table>
    `;
    container.appendChild(tokensTable);
    
    const tbody = document.getElementById('tokens-tbody');
    if (!tbody) {
        console.error("Tokens tbody not found after appending to container");
        return;
    }
    
    // Add rows for each token
    if (lexicalData.tokens && lexicalData.tokens.length) {
        lexicalData.tokens.forEach(token => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-primary">${token.type}</span></td>
                <td><code>${token.value}</code></td>
                <td>${token.line}</td>
                <td>${token.position}</td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="4">No tokens found</td></tr>';
    }
    
    // Display errors if any
    if (lexicalData.errors && lexicalData.errors.length) {
        const errorsDiv = document.createElement('div');
        errorsDiv.className = 'alert alert-danger';
        errorsDiv.innerHTML = '<h5>Lexical Errors</h5><ul id="lexical-errors-list"></ul>';
        container.appendChild(errorsDiv);
        
        const errorsList = document.getElementById('lexical-errors-list');
        lexicalData.errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = `Line ${error.line}: ${error.message}`;
            errorsList.appendChild(li);
        });
    }
}

/**
 * Visualize syntax analysis results
 * @param {Object} syntaxData - Syntax analysis data from the server
 */
function visualizeSyntaxAnalysis(syntaxData) {

    const container = document.getElementById('syntax-result');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create AST visualization
    const astDiv = document.createElement('div');
    astDiv.className = 'mb-4';
    astDiv.innerHTML = `<h5>Abstract Syntax Tree</h5>`;
    container.appendChild(astDiv);
    
    // Use D3.js to create an interactive tree visualization
    if (syntaxData.ast) {
        try {
            // Parse the AST JSON if it's a string
            const ast = typeof syntaxData.ast === 'string' ? JSON.parse(syntaxData.ast) : syntaxData.ast;
            
            // Create the tree container
            const treeContainer = document.createElement('div');
            treeContainer.id = 'ast-tree';
            treeContainer.className = 'tree-container';
            astDiv.appendChild(treeContainer);
            
            // Convert the AST to a d3-compatible hierarchy
            const root = d3.hierarchy(ast);
            
            // Set up the tree layout
            const treeLayout = d3.tree().size([800, 500]);
            treeLayout(root);
            
            // Create the SVG container
            const svg = d3.select('#ast-tree')
                .append('svg')
                .attr('width', 900)
                .attr('height', 600)
                .append('g')
                .attr('transform', 'translate(50,50)');
            
            // Draw links
            svg.selectAll('.link')
                .data(root.links())
                .enter()
                .append('path')
                .attr('class', 'link')
                .attr('d', d => {
                    return `M${d.source.x},${d.source.y}
                            C${d.source.x},${(d.source.y + d.target.y) / 2}
                             ${d.target.x},${(d.source.y + d.target.y) / 2}
                             ${d.target.x},${d.target.y}`;
                })
                .attr('fill', 'none')
                .attr('stroke', '#aaa');
            
            // Draw nodes
            const nodes = svg.selectAll('.node')
                .data(root.descendants())
                .enter()
                .append('g')
                .attr('class', 'node')
                .attr('transform', d => `translate(${d.x},${d.y})`);
            
            // Node circles
            nodes.append('circle')
                .attr('r', 5)
                .attr('fill', '#6c757d');
            
            // Node labels
            nodes.append('text')
                .attr('dy', '.31em')
                .attr('y', d => d.children ? -10 : 10)
                .attr('text-anchor', 'middle')
                .text(d => {
                    let text = d.data.type || '';
                    if (d.data.value) {
                        text += `: ${d.data.value}`;
                    }
                    return text;
                })
                .attr('fill', 'white')
                .attr('font-size', '12px');
        } catch (e) {
            astDiv.innerHTML += `<div class="alert alert-warning">Error rendering AST: ${e.message}</div>`;
            
            // Fallback: Show AST as formatted code
            const pre = document.createElement('pre');
            pre.className = 'bg-dark text-light p-3 rounded';
            pre.textContent = syntaxData.ast;
            astDiv.appendChild(pre);
        }
    } else {
        astDiv.innerHTML += '<div class="alert alert-warning">No AST available</div>';
    }
    
    // Display errors if any
    if (syntaxData.error) {
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.innerHTML = `<strong>Parser Error:</strong> ${syntaxData.error}`;
        container.appendChild(errorAlert);
    }
}

/**
 * Visualize semantic analysis results
 * @param {Object} semanticData - Semantic analysis data from the server
 */
function visualizeSemanticAnalysis(semanticData) {
    const container = document.getElementById('semantic-result');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create symbol table visualization
    const symbolTableDiv = document.createElement('div');
    symbolTableDiv.className = 'table-responsive mb-4';
    symbolTableDiv.innerHTML = `
        <h5>Symbol Table</h5>
        <table class="table table-sm table-dark">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Scope</th>
                    <th>Line</th>
                    <th>Is Function</th>
                    <th>Used</th>
                </tr>
            </thead>
            <tbody id="symbol-table-tbody">
            </tbody>
        </table>
    `;
    container.appendChild(symbolTableDiv);
    
    const tbody = document.getElementById('symbol-table-tbody');
    
    // Add rows for each symbol
    if (semanticData.symbol_table && semanticData.symbol_table.length) {
        semanticData.symbol_table.forEach(symbol => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${symbol.name}</code></td>
                <td>${symbol.type}</td>
                <td>${symbol.scope}</td>
                <td>${symbol.line}</td>
                <td>${symbol.is_function ? 'Yes' : 'No'}</td>
                <td>${symbol.used ? 'Yes' : 'No'}</td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="6">No symbols found</td></tr>';
    }
    
    // Display errors and warnings if any
    if (semanticData.errors && semanticData.errors.length) {
        const errorsDiv = document.createElement('div');
        errorsDiv.className = 'mb-4';
        errorsDiv.innerHTML = '<h5>Semantic Errors and Warnings</h5>';
        container.appendChild(errorsDiv);
        
        const errorsList = document.createElement('ul');
        errorsList.className = 'list-group';
        errorsDiv.appendChild(errorsList);
        
        semanticData.errors.forEach(error => {
            const li = document.createElement('li');
            li.className = `list-group-item ${error.type === 'warning' ? 'list-group-item-warning' : 'list-group-item-danger'}`;
            li.innerHTML = `
                <strong>${error.type === 'warning' ? 'Warning' : 'Error'}:</strong> 
                ${error.message} 
                ${error.line ? `(Line ${error.line})` : ''}
            `;
            errorsList.appendChild(li);
        });
    }
}

/**
 * Visualize intermediate code generation results
 * @param {Object} irData - Intermediate code data from the server
 */
function visualizeIntermediateCode(irData) {
    const container = document.getElementById('intermediate-result');
    if (!container) return;
    
    container.innerHTML = '';
    
    // IR Code display
    const irCodeDiv = document.createElement('div');
    irCodeDiv.className = 'mb-4';
    irCodeDiv.innerHTML = '<h5>Intermediate Representation</h5>';
    container.appendChild(irCodeDiv);
    
    if (irData.ir_code && irData.ir_code.length) {
        const pre = document.createElement('pre');
        pre.className = 'bg-dark text-light p-3 rounded';
        pre.innerHTML = irData.ir_code.map((line, i) => `${i+1}: ${line}`).join('\n');
        irCodeDiv.appendChild(pre);
    } else {
        irCodeDiv.innerHTML += '<div class="alert alert-warning">No intermediate code generated</div>';
    }
    
    // Control Flow Graph
    if (irData.cfg) {
        const cfgDiv = document.createElement('div');
        cfgDiv.className = 'mb-4';
        cfgDiv.innerHTML = '<h5>Control Flow Graph</h5>';
        container.appendChild(cfgDiv);
        
        // Create a div for the CFG visualization
        const cfgContainer = document.createElement('div');
        cfgContainer.id = 'cfg-container';
        cfgContainer.className = 'cfg-container';
        cfgDiv.appendChild(cfgContainer);
        
        try {
            // Create CFG visualization using D3.js
            const width = 800;
            const height = 600;
            
            // Create the SVG container
            const svg = d3.select('#cfg-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', 'translate(50,50)');
                
            // Create force simulation
            const simulation = d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(150))
                .force('charge', d3.forceManyBody().strength(-500))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            // Process CFG data
            const blocks = irData.cfg.blocks || [];
            
            // Create nodes and links
            const nodes = blocks.map(block => {
                return {
                    id: block.label || `Block_${block.id || Math.random().toString(36).substr(2, 9)}`,
                    label: block.label || 'Block',
                    instructions: block.instructions || []
                };
            });
            
            const links = [];
            blocks.forEach(block => {
                const source = block.label || `Block_${block.id || Math.random().toString(36).substr(2, 9)}`;
                (block.successors || []).forEach(succ => {
                    links.push({
                        source: source,
                        target: typeof succ === 'string' ? succ : `Block_${succ}`
                    });
                });
            });
            
            // Draw links
            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('stroke', '#999')
                .attr('stroke-width', 1.5)
                .attr('marker-end', 'url(#arrowhead)');
            
            // Define arrow marker for links
            svg.append('defs').append('marker')
                .attr('id', 'arrowhead')
                .attr('viewBox', '0 -5 10 10')
                .attr('refX', 15)
                .attr('refY', 0)
                .attr('orient', 'auto')
                .attr('markerWidth', 8)
                .attr('markerHeight', 8)
                .append('path')
                .attr('d', 'M0,-5L10,0L0,5')
                .attr('fill', '#999');
            
            // Draw nodes
            const node = svg.append('g')
                .selectAll('g')
                .data(nodes)
                .enter()
                .append('g');
            
            // Add rectangles for nodes
            node.append('rect')
                .attr('width', 120)
                .attr('height', d => Math.max(50, d.instructions.length * 15 + 20))
                .attr('rx', 5)
                .attr('ry', 5)
                .attr('fill', '#495057')
                .attr('stroke', '#6c757d')
                .attr('stroke-width', 1);
            
            // Add labels for nodes
            node.append('text')
                .attr('x', 60)
                .attr('y', 15)
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .text(d => d.label);
            
            // Add instructions text
            node.each(function(d) {
                const g = d3.select(this);
                d.instructions.slice(0, 3).forEach((instr, i) => {
                    g.append('text')
                        .attr('x', 60)
                        .attr('y', 35 + i * 15)
                        .attr('text-anchor', 'middle')
                        .attr('fill', 'white')
                        .attr('font-size', '10px')
                        .text(instr.length > 20 ? instr.substring(0, 20) + '...' : instr);
                });
                
                if (d.instructions.length > 3) {
                    g.append('text')
                        .attr('x', 60)
                        .attr('y', 35 + 3 * 15)
                        .attr('text-anchor', 'middle')
                        .attr('fill', 'white')
                        .attr('font-size', '10px')
                        .text(`... (${d.instructions.length - 3} more)`);
                }
            });
            
            // Add drag behavior to nodes
            node.call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
            
            // Set up the simulation
            simulation
                .nodes(nodes)
                .on('tick', ticked);
            
            simulation.force('link')
                .links(links);
            
            // Functions for handling drag events
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
            
            // Update positions on each tick
            function ticked() {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('transform', d => `translate(${d.x - 60},${d.y - 30})`);
            }
        } catch (e) {
            cfgDiv.innerHTML += `<div class="alert alert-warning">Error rendering CFG: ${e.message}</div>`;
            
            // Fallback: Show basic block information
            const blocksList = document.createElement('ul');
            blocksList.className = 'list-group';
            cfgDiv.appendChild(blocksList);
            
            (irData.cfg.blocks || []).forEach(block => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.innerHTML = `
                    <h6>${block.label || 'Block'}</h6>
                    <pre class="mb-2 text-light">${(block.instructions || []).join('\n')}</pre>
                    <div>
                        <strong>Successors:</strong> 
                        ${(block.successors || []).map(s => `<span class="badge bg-secondary mx-1">${s}</span>`).join('')}
                    </div>
                `;
                blocksList.appendChild(li);
            });
        }
    }
    
    // Display errors if any
    if (irData.errors && irData.errors.length) {
        const errorsDiv = document.createElement('div');
        errorsDiv.className = 'alert alert-danger';
        errorsDiv.innerHTML = '<h5>Intermediate Code Generation Errors</h5><ul id="ir-errors-list"></ul>';
        container.appendChild(errorsDiv);
        
        const errorsList = document.getElementById('ir-errors-list');
        irData.errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error.message || error;
            errorsList.appendChild(li);
        });
    }
}

/**
 * Visualize optimization results
 * @param {Object} optimizationData - Optimization data from the server
 */
function visualizeOptimization(optimizationData) {
    const container = document.getElementById('optimization-result');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Create comparison view: before and after optimization
    const comparisonDiv = document.createElement('div');
    comparisonDiv.className = 'row mb-4';
    comparisonDiv.innerHTML = `
        <div class="col-md-6">
            <h5>Before Optimization</h5>
            <pre id="before-optimization" class="bg-dark text-light p-3 rounded" style="height: 400px; overflow-y: auto;"></pre>
        </div>
        <div class="col-md-6">
            <h5>After Optimization</h5>
            <pre id="after-optimization" class="bg-dark text-light p-3 rounded" style="height: 400px; overflow-y: auto;"></pre>
        </div>
    `;
    container.appendChild(comparisonDiv);
    
    // Populate before/after code
    const beforePre = document.getElementById('before-optimization');
    const afterPre = document.getElementById('after-optimization');
    
    if (optimizationData.original_code && optimizationData.original_code.length) {
        beforePre.innerHTML = optimizationData.original_code.map((line, i) => {
            return `<div id="before-line-${i}" class="line">${i+1}: ${line}</div>`;
        }).join('');
    } else {
        beforePre.textContent = 'No code available';
    }
    
    if (optimizationData.optimized_code && optimizationData.optimized_code.length) {
        afterPre.innerHTML = optimizationData.optimized_code.map((line, i) => {
            return `<div id="after-line-${i}" class="line">${i+1}: ${line}</div>`;
        }).join('');
    } else {
        afterPre.textContent = 'No optimized code available';
    }
    
    // Optimization details
    if (optimizationData.optimization_details) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'mb-4';
        detailsDiv.innerHTML = '<h5>Optimization Details</h5>';
        container.appendChild(detailsDiv);
        
        // Create tabs for different optimization types
        const tabsDiv = document.createElement('div');
        tabsDiv.innerHTML = `
            <ul class="nav nav-tabs" id="optimization-tabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="const-fold-tab" data-bs-toggle="tab" data-bs-target="#const-fold" type="button" role="tab">
                        Constant Folding
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="const-prop-tab" data-bs-toggle="tab" data-bs-target="#const-prop" type="button" role="tab">
                        Constant Propagation
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="dead-code-tab" data-bs-toggle="tab" data-bs-target="#dead-code" type="button" role="tab">
                        Dead Code Elimination
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="common-sub-tab" data-bs-toggle="tab" data-bs-target="#common-sub" type="button" role="tab">
                        Common Subexpression
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="strength-red-tab" data-bs-toggle="tab" data-bs-target="#strength-red" type="button" role="tab">
                        Strength Reduction
                    </button>
                </li>
            </ul>
            <div class="tab-content p-3 border border-top-0 rounded-bottom" id="optimization-tab-content">
                <div class="tab-pane fade show active" id="const-fold" role="tabpanel"></div>
                <div class="tab-pane fade" id="const-prop" role="tabpanel"></div>
                <div class="tab-pane fade" id="dead-code" role="tabpanel"></div>
                <div class="tab-pane fade" id="common-sub" role="tabpanel"></div>
                <div class="tab-pane fade" id="strength-red" role="tabpanel"></div>
            </div>
        `;
        detailsDiv.appendChild(tabsDiv);
        
        // Populate tabs with optimization details
        const details = optimizationData.optimization_details;
        populateOptimizationTab('const-fold', 'Constant Folding', details.constant_folding || []);
        populateOptimizationTab('const-prop', 'Constant Propagation', details.constant_propagation || []);
        populateOptimizationTab('dead-code', 'Dead Code Elimination', details.dead_code_elimination || []);
        populateOptimizationTab('common-sub', 'Common Subexpression Elimination', details.common_subexpression_elimination || []);
        populateOptimizationTab('strength-red', 'Strength Reduction', details.strength_reduction || []);
    }
    
    // Helper function to populate optimization tabs
    function populateOptimizationTab(id, title, optimizations) {
        const tab = document.getElementById(id);
        if (!tab) return;
        
        if (optimizations.length === 0) {
            tab.innerHTML = `<div class="alert alert-info">No ${title} optimizations applied</div>`;
            return;
        }
        
        // Create a table to show the optimizations
        const table = document.createElement('table');
        table.className = 'table table-sm table-dark';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Original</th>
                    <th>Optimized</th>
                </tr>
            </thead>
            <tbody id="${id}-tbody"></tbody>
        `;
        tab.appendChild(table);
        
        const tbody = document.getElementById(`${id}-tbody`);
        optimizations.forEach(opt => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${opt.original || ''}</code></td>
                <td><code>${opt.optimized || ''}</code></td>
            `;
            tbody.appendChild(row);
        });
    }
}

/**
 * Visualize code generation results
 * @param {Object} codegenData - Code generation data from the server
 */
function visualizeCodeGeneration(codegenData) {
    const container = document.getElementById('codegen-result');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Assembly code display
    const assemblyDiv = document.createElement('div');
    assemblyDiv.className = 'mb-4';
    assemblyDiv.innerHTML = '<h5>Generated Assembly Code</h5>';
    container.appendChild(assemblyDiv);
    
    if (codegenData.assembly_code && codegenData.assembly_code.length) {
        const pre = document.createElement('pre');
        pre.className = 'bg-dark text-light p-3 rounded';
        pre.style.maxHeight = '400px';
        pre.style.overflowY = 'auto';
        pre.innerHTML = codegenData.assembly_code.map((line, i) => {
            // Add syntax highlighting based on the type of instruction
            let lineClass = '';
            if (line.includes(':')) {
                lineClass = 'text-warning'; // Labels
            } else if (line.trim().startsWith(';')) {
                lineClass = 'text-muted'; // Comments
            } else if (line.includes('mov') || line.includes('add') || line.includes('sub') || 
                      line.includes('mul') || line.includes('div') || line.includes('imul')) {
                lineClass = 'text-info'; // Arithmetic instructions
            } else if (line.includes('jmp') || line.includes('je') || line.includes('jne') ||
                      line.includes('call') || line.includes('ret')) {
                lineClass = 'text-danger'; // Control flow instructions
            }
            
            return `<div class="${lineClass}">${line}</div>`;
        }).join('\n');
        assemblyDiv.appendChild(pre);
    } else {
        assemblyDiv.innerHTML += '<div class="alert alert-warning">No assembly code generated</div>';
    }
    
    // Register allocation
    if (codegenData.register_allocation) {
        const registerDiv = document.createElement('div');
        registerDiv.className = 'mb-4';
        registerDiv.innerHTML = '<h5>Register Allocation</h5>';
        container.appendChild(registerDiv);
        
        const table = document.createElement('table');
        table.className = 'table table-sm table-dark';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Variable</th>
                    <th>Register</th>
                </tr>
            </thead>
            <tbody id="register-allocation-tbody"></tbody>
        `;
        registerDiv.appendChild(table);
        
        const tbody = document.getElementById('register-allocation-tbody');
        for (const [variable, register] of Object.entries(codegenData.register_allocation)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${variable}</code></td>
                <td><code>${register}</code></td>
            `;
            tbody.appendChild(row);
        }
    }
    
    // Stack frame
    if (codegenData.stack_frame) {
        const stackDiv = document.createElement('div');
        stackDiv.className = 'mb-4';
        stackDiv.innerHTML = '<h5>Stack Frame</h5>';
        container.appendChild(stackDiv);
        
        const table = document.createElement('table');
        table.className = 'table table-sm table-dark';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Variable</th>
                    <th>Offset</th>
                </tr>
            </thead>
            <tbody id="stack-frame-tbody"></tbody>
        `;
        stackDiv.appendChild(table);
        
        const tbody = document.getElementById('stack-frame-tbody');
        for (const [variable, offset] of Object.entries(codegenData.stack_frame)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${variable}</code></td>
                <td><code>[rbp-${offset}]</code></td>
            `;
            tbody.appendChild(row);
        }
    }
    
    // Display errors if any
    if (codegenData.errors && codegenData.errors.length) {
        const errorsDiv = document.createElement('div');
        errorsDiv.className = 'alert alert-danger';
        errorsDiv.innerHTML = '<h5>Code Generation Errors</h5><ul id="codegen-errors-list"></ul>';
        container.appendChild(errorsDiv);
        
        const errorsList = document.getElementById('codegen-errors-list');
        codegenData.errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error.message || error;
            errorsList.appendChild(li);
        });
    }
}
