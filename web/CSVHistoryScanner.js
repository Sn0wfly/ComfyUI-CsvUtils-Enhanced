import { app } from "../../scripts/app.js";

let currentHistoryData = [];

// Función para procesar ruta de imagen
function processImagePath(imagePath) {
    return `/csv_image_view?filename=${encodeURIComponent(imagePath)}`;
}

// Crear modal de imagen (igual que en CSVPromptSearch)
function createImageModal() {
    if (document.getElementById('csv-history-modal')) {
        return;
    }

    const modal = document.createElement('div');
    modal.id = 'csv-history-modal';
    modal.innerHTML = `
        <style>
            #csv-history-modal {
                display: none;
                position: fixed;
                z-index: 10000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
                backdrop-filter: blur(4px);
            }
            
            .csv-history-modal-content {
                position: relative;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            
            .csv-history-modal-image {
                max-width: 90%;
                max-height: 90%;
                cursor: move;
                user-select: none;
                transition: transform 0.1s ease;
            }
            
            .csv-history-close {
                position: absolute;
                top: 20px;
                right: 35px;
                color: #ffffff;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
                z-index: 10001;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            }
            
            .csv-history-close:hover {
                color: #ff6b6b;
            }
            
            .csv-history-zoom-info {
                position: absolute;
                bottom: 20px;
                left: 20px;
                color: white;
                background: rgba(0,0,0,0.7);
                padding: 8px 12px;
                border-radius: 4px;
                font-family: monospace;
                z-index: 10001;
            }
        </style>
        
        <div class="csv-history-modal-content">
            <span class="csv-history-close">&times;</span>
            <img class="csv-history-modal-image" src="" alt="">
            <div class="csv-history-zoom-info">Scroll: zoom | Drag: pan | ESC/Click: close</div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('.csv-history-close');
    const modalImg = modal.querySelector('.csv-history-modal-image');
    const zoomInfo = modal.querySelector('.csv-history-zoom-info');

    let scale = 1;
    let isDragging = false;
    let startX, startY, translateX = 0, translateY = 0;

    // Funciones de control del modal (iguales que en CSVPromptSearch)
    function updateTransform() {
        modalImg.style.transform = `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
        zoomInfo.textContent = `Zoom: ${Math.round(scale * 100)}% | Scroll: zoom | Drag: pan | ESC/Click: close`;
    }

    function resetView() {
        scale = 1;
        translateX = 0;
        translateY = 0;
        updateTransform();
    }

    function closeModal() {
        modal.style.display = 'none';
        resetView();
    }

    // Event listeners
    closeBtn.onclick = closeModal;
    modal.onclick = (e) => {
        if (e.target === modal) closeModal();
    };

    document.addEventListener('keydown', (e) => {
        if (modal.style.display === 'block' && e.key === 'Escape') {
            closeModal();
        }
    });

    modalImg.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomSpeed = 0.1;
        const prevScale = scale;
        
        if (e.deltaY < 0) {
            scale = Math.min(scale + zoomSpeed, 5);
        } else {
            scale = Math.max(scale - zoomSpeed, 0.1);
        }
        
        if (scale !== prevScale) {
            updateTransform();
        }
    });

    modalImg.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX - translateX;
        startY = e.clientY - translateY;
        modalImg.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            updateTransform();
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        modalImg.style.cursor = 'move';
    });

    // Función para abrir modal con imagen
    window.openHistoryImageModal = function(imageSrc) {
        modalImg.src = imageSrc;
        resetView();
        modal.style.display = 'block';
    };
}

// Función para agrupar imágenes por prompt
function groupImagesByPrompt(data) {
    const groups = {};
    
    data.forEach(item => {
        // Crear key único basado en prompts (ignorando espacios extra)
        const positiveKey = (item.positive_prompt || '').trim().toLowerCase();
        const negativeKey = (item.negative_prompt || '').trim().toLowerCase();
        const groupKey = `${positiveKey}|||${negativeKey}`;
        
        if (!groups[groupKey]) {
            groups[groupKey] = {
                positive_prompt: item.positive_prompt || '',
                negative_prompt: item.negative_prompt || '',
                images: [],
                selected: false
            };
        }
        
        // Agregar selected a cada imagen individual
        if (!item.hasOwnProperty('selected')) {
            item.selected = false;
        }
        
        groups[groupKey].images.push(item);
    });
    
    return Object.values(groups);
}

// Crear interfaz principal
function createHistoryInterface() {
    let container = document.getElementById('csv-history-container');
    if (container) {
        container.remove();
    }

    container = document.createElement('div');
    container.id = 'csv-history-container';
    container.innerHTML = `
        <style>
            #csv-history-container {
                background: #2a2a2a;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
                max-height: 80vh;
                overflow-y: auto;
                font-family: Arial, sans-serif;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 600px;
                z-index: 9999;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                resize: both;
                min-width: 400px;
                min-height: 300px;
            }
            
            .csv-history-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding: 5px 0 10px 0;
                border-bottom: 1px solid #555;
                cursor: move;
                user-select: none;
            }
            
            .csv-history-title {
                color: #fff;
                font-size: 16px;
                font-weight: bold;
            }
            
            .csv-history-close-panel {
                background: #ff4444;
                border: none;
                color: #fff;
                font-size: 16px;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                width: auto;
                height: auto;
            }
            
            .csv-history-close-panel:hover {
                background: #ff6666;
            }
            
            .csv-history-controls {
                display: flex;
                gap: 8px;
                margin-bottom: 15px;
            }
            
            .csv-history-btn {
                background: #4a90e2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                flex: 1;
            }
            
            .csv-history-btn:hover {
                background: #357abd;
            }
            
            .csv-history-btn:disabled {
                background: #666;
                cursor: not-allowed;
            }
            
            .csv-history-stats {
                color: #aaa;
                font-size: 12px;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .csv-history-group {
                background: #333;
                border-radius: 6px;
                margin-bottom: 15px;
                overflow: hidden;
                border: 2px solid transparent;
                transition: border-color 0.2s;
            }
            
            .csv-history-group.selected {
                border-color: #4a90e2;
            }
            
            .csv-history-group-header {
                background: #3a3a3a;
                padding: 10px;
                border-bottom: 1px solid #555;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .csv-history-group-checkbox {
                width: 16px;
                height: 16px;
                cursor: pointer;
            }
            
            .csv-history-group-prompts {
                flex: 1;
                min-width: 0;
            }
            
            .csv-history-prompt-line {
                margin-bottom: 4px;
                font-size: 12px;
                line-height: 1.3;
            }
            
            .csv-history-prompt-line.positive {
                color: #5cb85c;
            }
            
            .csv-history-prompt-line.negative {
                color: #d9534f;
            }
            
            .csv-history-prompt-text {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
            }
            
            .csv-history-image-count {
                background: #4a90e2;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 11px;
                min-width: 20px;
                text-align: center;
            }
            
            .csv-history-images-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
                gap: 6px;
                padding: 10px;
            }
            
            .csv-history-image-item {
                position: relative;
                cursor: pointer;
                border-radius: 4px;
                overflow: hidden;
                transition: transform 0.2s;
            }
            
            .csv-history-image-item:hover {
                transform: scale(1.05);
            }
            
            .csv-history-thumbnail {
                width: 100%;
                height: 60px;
                object-fit: cover;
                display: block;
            }
            
            .csv-history-filename-mini {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.8);
                color: white;
                font-size: 8px;
                padding: 1px 2px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .csv-history-image-checkbox {
                position: absolute;
                top: 4px;
                left: 4px;
                width: 14px;
                height: 14px;
                z-index: 10;
                cursor: pointer;
                background: rgba(255,255,255,0.9);
                border-radius: 2px;
            }
            
            .csv-history-image-item.selected-image {
                border: 2px solid #4a90e2;
                border-radius: 4px;
                box-shadow: 0 0 8px rgba(74, 144, 226, 0.6);
            }
            
            .csv-history-image-item.selected-image .csv-history-thumbnail {
                opacity: 0.8;
            }
        </style>
        
        <div class="csv-history-header" id="csvHistoryHeader">
            <div class="csv-history-title">📷 History Scanner → Preview Collection</div>
            <button class="csv-history-close-panel" id="closeHistoryPanel">✕</button>
        </div>
        
        <div class="csv-history-controls">
            <button class="csv-history-btn" id="selectAll">All</button>
            <button class="csv-history-btn" id="selectNone">None</button>
            <button class="csv-history-btn" id="addToCSV" disabled>Move & Save</button>
        </div>
        
        <div class="csv-history-stats" id="historyStats">No data</div>
        <div class="csv-history-groups" id="historyGroups"></div>
    `;

    document.body.appendChild(container);
    createImageModal();
    
    // Hacer el panel draggable
    makeDraggable(container);
    
    return container;
}

// Función para hacer el panel draggable
function makeDraggable(container) {
    const header = container.querySelector('#csvHistoryHeader');
    const closeBtn = container.querySelector('#closeHistoryPanel');
    
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    closeBtn.onclick = () => {
        container.style.display = 'none';
    };

    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', dragMove);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
        if (e.target === closeBtn) return;
        
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;

        if (e.target === header || header.contains(e.target)) {
            isDragging = true;
            container.style.cursor = 'grabbing';
        }
    }

    function dragMove(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;

            xOffset = currentX;
            yOffset = currentY;

            container.style.transform = `translate(${currentX}px, ${currentY}px)`;
        }
    }

    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
        container.style.cursor = 'default';
    }
}

// Actualizar display con los datos agrupados
function updateHistoryDisplay(data) {
    const container = document.getElementById('csv-history-container');
    if (!container) return;

    const groupsContainer = container.querySelector('#historyGroups');
    const stats = container.querySelector('#historyStats');
    const selectAllBtn = container.querySelector('#selectAll');
    const selectNoneBtn = container.querySelector('#selectNone');
    const addToCSVBtn = container.querySelector('#addToCSV');

    if (!data || data.length === 0) {
        groupsContainer.innerHTML = '<div style="text-align: center; color: #aaa; padding: 20px;">No images found</div>';
        stats.textContent = 'No results';
        return;
    }

    // Agrupar por prompts
    const groups = groupImagesByPrompt(data);
    
    // Actualizar estado de selección de grupos basado en imágenes individuales
    groups.forEach(group => {
        const selectedImages = group.images.filter(img => img.selected).length;
        group.selected = selectedImages > 0;
        group.partiallySelected = selectedImages > 0 && selectedImages < group.images.length;
    });
    
    // Actualizar estadísticas
    const totalImages = groups.reduce((sum, group) => sum + group.images.length, 0);
    const selectedImages = groups.reduce((sum, group) => 
        sum + group.images.filter(img => img.selected).length, 0);
    
    stats.textContent = `${groups.length} prompt groups • ${totalImages} images • ${selectedImages} selected`;
    addToCSVBtn.disabled = selectedImages === 0;

    // Crear grupos
    groupsContainer.innerHTML = '';
    groups.forEach((group, groupIndex) => {
        const selectedInGroup = group.images.filter(img => img.selected).length;
        const isFullySelected = selectedInGroup === group.images.length;
        const isPartiallySelected = selectedInGroup > 0 && selectedInGroup < group.images.length;
        
        const groupElement = document.createElement('div');
        groupElement.className = `csv-history-group ${selectedInGroup > 0 ? 'selected' : ''}`;
        
        groupElement.innerHTML = `
            <div class="csv-history-group-header">
                <input type="checkbox" class="csv-history-group-checkbox" 
                       ${isFullySelected ? 'checked' : ''} 
                       data-group="${groupIndex}"
                       ${isPartiallySelected ? 'style="opacity: 0.5;"' : ''}>
                <div class="csv-history-group-prompts">
                    <div class="csv-history-prompt-line positive">
                        <strong>+:</strong> <span class="csv-history-prompt-text">${group.positive_prompt || 'No positive prompt'}</span>
                    </div>
                    <div class="csv-history-prompt-line negative">
                        <strong>-:</strong> <span class="csv-history-prompt-text">${group.negative_prompt || 'No negative prompt'}</span>
                    </div>
                </div>
                <div class="csv-history-image-count">${selectedInGroup}/${group.images.length}</div>
            </div>
            <div class="csv-history-images-grid" id="group-${groupIndex}"></div>
        `;

        // Agregar imágenes del grupo
        const imagesGrid = groupElement.querySelector(`#group-${groupIndex}`);
        group.images.forEach((item, imageIndex) => {
            const imageElement = document.createElement('div');
            imageElement.className = `csv-history-image-item ${item.selected ? 'selected-image' : ''}`;
            
            const imageUrl = processImagePath(item.relative_path);
            
            imageElement.innerHTML = `
                <input type="checkbox" class="csv-history-image-checkbox" 
                       ${item.selected ? 'checked' : ''} 
                       data-group="${groupIndex}" 
                       data-image="${imageIndex}">
                <img src="${imageUrl}" class="csv-history-thumbnail" alt="${item.filename}">
                <div class="csv-history-filename-mini">${item.filename}</div>
            `;

            // Click en imagen abre modal
            const img = imageElement.querySelector('.csv-history-thumbnail');
            img.addEventListener('click', (e) => {
                e.stopPropagation();
                window.openHistoryImageModal(imageUrl);
            });

            // Click en checkbox de imagen individual
            const imageCheckbox = imageElement.querySelector('.csv-history-image-checkbox');
            imageCheckbox.addEventListener('change', (e) => {
                e.stopPropagation();
                const groupIdx = parseInt(e.target.dataset.group);
                const imageIdx = parseInt(e.target.dataset.image);
                
                groups[groupIdx].images[imageIdx].selected = e.target.checked;
                imageElement.classList.toggle('selected-image', e.target.checked);
                
                // Actualizar todo el display
                updateHistoryDisplay(data);
            });

            imagesGrid.appendChild(imageElement);
        });

        // Click en checkbox de grupo (selecciona/deselecciona todo el grupo)
        const groupCheckbox = groupElement.querySelector('.csv-history-group-checkbox');
        groupCheckbox.addEventListener('change', (e) => {
            e.stopPropagation();
            const groupIdx = parseInt(e.target.dataset.group);
            const shouldSelect = e.target.checked;
            
            // Seleccionar/deseleccionar todas las imágenes del grupo
            groups[groupIdx].images.forEach(img => {
                img.selected = shouldSelect;
            });
            
            // Actualizar todo el display
            updateHistoryDisplay(data);
        });

        groupsContainer.appendChild(groupElement);
    });

    // Event listeners para botones
    selectAllBtn.onclick = () => {
        groups.forEach(group => {
            group.images.forEach(img => {
                img.selected = true;
            });
        });
        updateHistoryDisplay(data);
    };

    selectNoneBtn.onclick = () => {
        groups.forEach(group => {
            group.images.forEach(img => {
                img.selected = false;
            });
        });
        updateHistoryDisplay(data);
    };

    addToCSVBtn.onclick = () => {
        // Recopilar todas las imágenes seleccionadas individualmente
        const selectedImages = [];
        groups.forEach(group => {
            group.images.forEach(img => {
                if (img.selected) {
                    selectedImages.push({
                        positive_prompt: group.positive_prompt,
                        negative_prompt: group.negative_prompt,
                        relative_path: img.relative_path
                    });
                }
            });
        });
        
        if (selectedImages.length > 0) {
            saveSelectedToCSV(selectedImages);
        }
    };
}

// Guardar seleccionados en CSV
async function saveSelectedToCSV(selectedImages) {
    try {
        // Agrupar imágenes por combinación de prompts
        const promptGroups = {};
        
        selectedImages.forEach(item => {
            const promptKey = `${item.positive_prompt}|||${item.negative_prompt}`;
            
            if (!promptGroups[promptKey]) {
                promptGroups[promptKey] = {
                    positive_prompt: item.positive_prompt || '',
                    negative_prompt: item.negative_prompt || '',
                    image_paths: []
                };
            }
            
            promptGroups[promptKey].image_paths.push(item.relative_path);
        });

        // Convertir grupos a formato CSV (una entrada por prompt con múltiples imágenes)
        const csvData = Object.values(promptGroups).map(group => ({
            positive_prompt: group.positive_prompt,
            negative_prompt: group.negative_prompt,
            image_path: group.image_paths.join(';')  // Unir múltiples imágenes con ';'
        }));

        // Llamar al endpoint de guardado
        const response = await fetch('/csv_utils/save_to_csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                entries: csvData
            })
        });

        const result = await response.json();
        
        if (result.success) {
            let message = `✅ Success!\n\n`;
            message += `📊 Saved: ${result.saved} prompt entries\n`;
            message += `🖼️ Moved: ${result.moved} images to preview folder\n`;
            if (result.skipped > 0) {
                message += `⏭️ Skipped: ${result.skipped} duplicate prompts\n`;
            }
            message += `\n📁 CSV Location: output/prompt_history.csv\n`;
            message += `📂 Images Location: output/preview/\n\n`;
            message += `Images with same prompts were grouped together!\n`;
            message += `Use "CSV Prompt Search" to browse your collection!`;
            
            alert(message);
            
            // Cerrar el panel después de guardar exitosamente
            const container = document.getElementById('csv-history-container');
            if (container) {
                container.style.display = 'none';
            }
        } else {
            alert(`❌ Error saving to CSV: ${result.message}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
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
                
                // Los datos del nodo llegan a través del campo 'ui'
                if (message && message.scan_results) {
                    currentHistoryData = message.scan_results;
                    
                    console.log("[CSV History] Received data:", currentHistoryData.length, "images");
                    
                    const container = createHistoryInterface();
                    container.style.display = 'block';
                    updateHistoryDisplay(currentHistoryData);
                }
            };
        }
    }
}); 