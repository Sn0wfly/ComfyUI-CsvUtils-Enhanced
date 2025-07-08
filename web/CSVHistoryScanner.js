import { app } from "../../scripts/app.js";

// Función para procesar ruta de imagen (igual que en CSVPromptSearch)
function processImagePath(imagePath) {
    let processedPath = imagePath;
    
    // Normalizar separadores de ruta a forward slash
    processedPath = imagePath.replace(/\\/g, '/');
    
    // Limpiar rutas absolutas manteniendo subdirectorios
    if (processedPath.includes('/output/')) {
        const outputIndex = processedPath.lastIndexOf('/output/');
        processedPath = processedPath.substring(outputIndex + 8); // +8 para saltar "/output/"
    }
    
    return `/csv_image_view?filename=${encodeURIComponent(processedPath)}`;
}

function createHistoryInterface(node, results) {
    const container = document.createElement('div');
    container.className = 'csv-history-container';
    container.innerHTML = `
        <style>
            .csv-history-container {
                background: #2a2a2a;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                max-height: 600px;
                overflow-y: auto;
                font-family: Arial, sans-serif;
            }
            
            .csv-history-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid #555;
            }
            
            .csv-history-title {
                color: #fff;
                font-size: 18px;
                font-weight: bold;
            }
            
            .csv-history-controls {
                display: flex;
                gap: 10px;
            }
            
            .csv-history-btn {
                background: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            
            .csv-history-btn:hover {
                background: #357abd;
            }
            
            .csv-history-btn:disabled {
                background: #666;
                cursor: not-allowed;
            }
            
            .csv-history-item {
                display: flex;
                align-items: center;
                background: #333;
                margin-bottom: 10px;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid transparent;
                transition: all 0.2s;
            }
            
            .csv-history-item:hover {
                background: #3a3a3a;
            }
            
            .csv-history-item.selected {
                border-left-color: #4a90e2;
                background: #2a3a4a;
            }
            
            .csv-history-checkbox {
                margin-right: 15px;
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            
            .csv-history-image {
                width: 80px;
                height: 80px;
                object-fit: cover;
                border-radius: 4px;
                margin-right: 15px;
                cursor: pointer;
                border: 2px solid transparent;
                transition: border-color 0.2s;
            }
            
            .csv-history-image:hover {
                border-color: #4a90e2;
            }
            
            .csv-history-content {
                flex: 1;
                min-width: 0;
            }
            
            .csv-history-filename {
                color: #fff;
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 14px;
            }
            
            .csv-history-date {
                color: #aaa;
                font-size: 12px;
                margin-bottom: 8px;
            }
            
            .csv-history-prompt {
                color: #ddd;
                font-size: 13px;
                margin-bottom: 4px;
                line-height: 1.3;
            }
            
            .csv-history-prompt.positive {
                border-left: 3px solid #5cb85c;
                padding-left: 8px;
            }
            
            .csv-history-prompt.negative {
                border-left: 3px solid #d9534f;
                padding-left: 8px;
            }
            
            .csv-history-prompt-text {
                display: block;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 400px;
            }
            
            .csv-history-stats {
                color: #aaa;
                font-size: 14px;
                margin-bottom: 10px;
            }
            
            .csv-history-empty {
                text-align: center;
                color: #aaa;
                padding: 40px;
                font-size: 16px;
            }
        </style>
        
        <div class="csv-history-header">
            <div class="csv-history-title">📷 History Scanner</div>
            <div class="csv-history-controls">
                <button class="csv-history-btn" id="selectAll">Select All</button>
                <button class="csv-history-btn" id="selectNone">Select None</button>
                <button class="csv-history-btn" id="addToCSV" disabled>Add Selected to CSV</button>
            </div>
        </div>
        
        <div class="csv-history-stats" id="historyStats"></div>
        <div class="csv-history-results" id="historyResults"></div>
    `;
    
    return container;
}

function updateHistoryDisplay(container, data) {
    const resultsContainer = container.querySelector('#historyResults');
    const statsContainer = container.querySelector('#historyStats');
    const selectAllBtn = container.querySelector('#selectAll');
    const selectNoneBtn = container.querySelector('#selectNone');
    const addToCSVBtn = container.querySelector('#addToCSV');
    
    if (!data || data.length === 0) {
        resultsContainer.innerHTML = '<div class="csv-history-empty">No images found with extractable prompts</div>';
        statsContainer.textContent = 'No results';
        return;
    }
    
    // Actualizar estadísticas
    const selectedCount = data.filter(item => item.selected).length;
    statsContainer.textContent = `Found ${data.length} images • ${selectedCount} selected`;
    
    // Habilitar/deshabilitar botón
    addToCSVBtn.disabled = selectedCount === 0;
    
    // Crear elementos para cada imagen
    resultsContainer.innerHTML = '';
    
    data.forEach((item, index) => {
        const itemElement = document.createElement('div');
        itemElement.className = `csv-history-item ${item.selected ? 'selected' : ''}`;
        
        const imageUrl = processImagePath(item.relative_path);
        
        itemElement.innerHTML = `
            <input type="checkbox" class="csv-history-checkbox" ${item.selected ? 'checked' : ''} data-index="${index}">
            <img src="${imageUrl}" class="csv-history-image" alt="${item.filename}" data-index="${index}">
            <div class="csv-history-content">
                <div class="csv-history-filename">${item.filename}</div>
                <div class="csv-history-date">${item.date}</div>
                <div class="csv-history-prompt positive">
                    <strong>Positive:</strong>
                    <span class="csv-history-prompt-text">${item.positive_prompt || 'None'}</span>
                </div>
                <div class="csv-history-prompt negative">
                    <strong>Negative:</strong>
                    <span class="csv-history-prompt-text">${item.negative_prompt || 'None'}</span>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(itemElement);
    });
    
    // Event listeners para checkboxes
    container.querySelectorAll('.csv-history-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const index = parseInt(e.target.dataset.index);
            data[index].selected = e.target.checked;
            
            // Actualizar clase visual
            const item = e.target.closest('.csv-history-item');
            if (e.target.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
            
            updateHistoryDisplay(container, data);
        });
    });
    
    // Event listeners para imágenes (preview)
    container.querySelectorAll('.csv-history-image').forEach(img => {
        img.addEventListener('click', (e) => {
            // Aquí se puede abrir el modal de imagen como en CSVPromptSearch
            console.log('Image clicked:', e.target.src);
        });
    });
    
    // Event listeners para botones
    selectAllBtn.onclick = () => {
        data.forEach(item => item.selected = true);
        updateHistoryDisplay(container, data);
    };
    
    selectNoneBtn.onclick = () => {
        data.forEach(item => item.selected = false);
        updateHistoryDisplay(container, data);
    };
    
    addToCSVBtn.onclick = () => {
        const selectedItems = data.filter(item => item.selected);
        if (selectedItems.length > 0) {
            addSelectedToCSV(selectedItems);
        }
    };
}

function addSelectedToCSV(selectedItems) {
    // Crear el CSV data
    const csvData = selectedItems.map(item => ({
        positive_prompt: item.positive_prompt,
        negative_prompt: item.negative_prompt,
        image_path: item.relative_path
    }));
    
    console.log('Adding to CSV:', csvData);
    alert(`Adding ${csvData.length} items to CSV (functionality to be implemented)`);
    
    // TODO: Aquí se conectaría con la lógica de CSVPromptSaver para agregar al archivo
}

// Extensión del nodo
app.registerExtension({
    name: "CSV.HistoryScanner",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "CSVHistoryScanner") {
            
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                if (message && message.scan_results) {
                    try {
                        const results = JSON.parse(message.scan_results);
                        
                        // Buscar o crear el contenedor
                        let container = document.getElementById('csv-history-interface');
                        if (!container) {
                            container = createHistoryInterface(this, results);
                            container.id = 'csv-history-interface';
                            document.body.appendChild(container);
                        }
                        
                        updateHistoryDisplay(container, results);
                        
                    } catch (error) {
                        console.error('Error parsing scan results:', error);
                    }
                }
            };
        }
    }
}); 