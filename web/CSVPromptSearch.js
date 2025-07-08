import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";

// MiniSearch no está siendo utilizado en este código, pero se mantiene por si se quiere añadir en el futuro.

async function getPromptList(file_path) {
	try {
		const response = await api.fetchApi("/csv_utils/get_prompts" , {
			method : "POST" ,
			headers : {"Content-Type" : "application/json"} ,
			body : JSON.stringify({ file_path : file_path })
		});
		if(response.status != 200) { throw new Error("Error querying prompts"); }
		const data = await response.json();
		return data.prompt_list;
	} catch(err) {
		app.extensionManager.toast.add({
			severity : "error" ,
			summary : "Internal Error" ,
			detail : err.message ,
			life : 5000
		});
		return [];
	}
}

function create_prompt_div(id, pos, neg, image_path) {
    let imageElement = '';
    
    if (image_path) {
        // Detectar si hay múltiples imágenes (separadas por ; o ,)
        const imagePaths = image_path.split(/[;,]/).map(p => p.trim()).filter(p => p.length > 0);
        const firstImagePath = imagePaths[0];
        
        let imageUrl = '';
        let processedPath = firstImagePath;
        
        // Normalizar separadores de ruta a forward slash
        processedPath = firstImagePath.replace(/\\/g, '/');
        
        // Limpiar rutas absolutas manteniendo subdirectorios
        if (processedPath.includes('/output/')) {
            // Extraer todo después de "output/"
            const outputMatch = processedPath.match(/output\/(.+)/);
            if (outputMatch) {
                processedPath = outputMatch[1];
            }
        }
        
        // Usar nuestro endpoint personalizado que soporta subdirectorios
        imageUrl = `/csv_image_view?filename=${encodeURIComponent(processedPath)}`;
        
        console.log(`[DEBUG] Imagen con subdirectorio: ${firstImagePath} -> procesada: ${processedPath} -> URL: ${imageUrl}`);
        
        // Crear contador si hay múltiples imágenes
        const counterElement = imagePaths.length > 1 ? 
            `<div class="csv-u-image-counter">1/${imagePaths.length}</div>` : '';
            
        imageElement = `
            <div class="csv-u-image-container">
                <img id="csv-preview-img-${id}" src="${imageUrl}" class="csv-u-preview-img" title="Click to zoom">
                ${counterElement}
            </div>
        `;
    }

	return `
		<div class="csv-u-prompt-container">
            ${imageElement}
			<div class="csv-u-text-prompts">
				<p class="csv-u-prompt-span csv-u-pos-span csv-u-p" title="Click to copy">${pos}</p>
				<p class="csv-u-prompt-span csv-u-neg-span csv-u-p" title="Click to copy">${neg}</p>
			</div>
		</div>
	`;
}

// Función para procesar ruta de imagen (común para todas las funciones)
function processImagePath(imagePath) {
	let processedPath = imagePath;
	
	// Normalizar separadores de ruta a forward slash
	processedPath = imagePath.replace(/\\/g, '/');
	
	// Limpiar rutas absolutas manteniendo subdirectorios
	if (processedPath.includes('/output/')) {
		// Extraer todo después de "output/"
		const outputMatch = processedPath.match(/output\/(.+)/);
		if (outputMatch) {
			processedPath = outputMatch[1];
		}
	}
	
	// Usar nuestro endpoint personalizado que soporta subdirectorios
	return `/csv_image_view?filename=${encodeURIComponent(processedPath)}`;
}

function createImageModal() {
	let modal = document.createElement("div");
	modal.className = "csv-u-modal";
	modal.innerHTML = `
		<div class="csv-u-modal-content">
			<span class="csv-u-modal-close">&times;</span>
			<div class="csv-u-image-counter-modal" style="display: none;">1/1</div>
			<img class="csv-u-modal-img" src="" alt="">
			<div class="csv-u-nav-controls" style="display: none;">
				<button class="csv-u-nav-btn" id="csv-u-prev-btn">← Previous</button>
				<button class="csv-u-nav-btn" id="csv-u-next-btn">Next →</button>
			</div>
			<div class="csv-u-zoom-info">🖱️ Scroll: Zoom | 🖐️ Drag: Pan | ESC: Close</div>
		</div>
	`;
	document.body.appendChild(modal);

	let currentScale = 1;
	let currentX = 0;
	let currentY = 0;
	let isDragging = false;
	let startX = 0;
	let startY = 0;
	let currentImages = [];
	let currentImageIndex = 0;

	const modalContent = modal.querySelector('.csv-u-modal-content');
	const modalImg = modal.querySelector('.csv-u-modal-img');
	const closeBtn = modal.querySelector('.csv-u-modal-close');
	const counterModal = modal.querySelector('.csv-u-image-counter-modal');
	const navControls = modal.querySelector('.csv-u-nav-controls');
	const prevBtn = modal.querySelector('#csv-u-prev-btn');
	const nextBtn = modal.querySelector('#csv-u-next-btn');

		// Función para actualizar imagen actual
	function updateCurrentImage() {
		const imagePath = currentImages[currentImageIndex];
		const imageUrl = processImagePath(imagePath);
		
		console.log(`[DEBUG] Actualizando imagen ${currentImageIndex + 1}/${currentImages.length}`);
		console.log(`[DEBUG] Ruta original: ${imagePath}`);
		console.log(`[DEBUG] URL procesada: ${imageUrl}`);
		
		modalImg.src = imageUrl;
		counterModal.textContent = `${currentImageIndex + 1}/${currentImages.length}`;
		
		// Añadir fallback para imágenes que no se encuentran
		modalImg.onerror = function() {
			this.onerror = null; // Evitar loop infinito
			// Ya procesamos la ruta al nombre del archivo, no hay más fallback necesario
		};
		
		// Actualizar botones
		prevBtn.disabled = currentImageIndex === 0;
		nextBtn.disabled = currentImageIndex === currentImages.length - 1;
		
		// Reset zoom y posición
		currentScale = 1;
		currentX = 0;
		currentY = 0;
		updateTransform();
	}

	// Función para abrir modal (modificada para múltiples imágenes)
	function openModal(imageSrc, allImages = null) {
		// Si se pasan múltiples imágenes, procesarlas
		if (allImages && allImages.length > 1) {
			currentImages = allImages;
			currentImageIndex = 0;
			counterModal.style.display = 'block';
			navControls.style.display = 'flex';
			updateCurrentImage();
		} else {
			// Una sola imagen (comportamiento original)
			currentImages = [imageSrc];
			currentImageIndex = 0;
			counterModal.style.display = 'none';
			navControls.style.display = 'none';
			modalImg.src = imageSrc;
			currentScale = 1;
			currentX = 0;
			currentY = 0;
			updateTransform();
		}
		
		modal.classList.add('show');
		
		// Calcular tamaño inicial
		modalImg.onload = () => {
			const containerWidth = window.innerWidth * 0.9;
			const containerHeight = window.innerHeight * 0.9;
			const imgRatio = modalImg.naturalWidth / modalImg.naturalHeight;
			const containerRatio = containerWidth / containerHeight;
			
			if (imgRatio > containerRatio) {
				modalImg.style.width = containerWidth + 'px';
				modalImg.style.height = 'auto';
			} else {
				modalImg.style.height = containerHeight + 'px';
				modalImg.style.width = 'auto';
			}
		};
	}

	// Función para cerrar modal
	function closeModal() {
		modal.classList.remove('show');
		currentScale = 1;
		currentX = 0;
		currentY = 0;
	}

	// Función para actualizar transformación
	function updateTransform() {
		modalImg.style.transform = `translate(${currentX}px, ${currentY}px) scale(${currentScale})`;
	}

	// Event listeners
	closeBtn.addEventListener('click', closeModal);
	modal.addEventListener('click', (e) => {
		if (e.target === modal) closeModal();
	});

	// Zoom con rueda del mouse
	modal.addEventListener('wheel', (e) => {
		e.preventDefault();
		const rect = modalImg.getBoundingClientRect();
		const centerX = rect.left + rect.width / 2;
		const centerY = rect.top + rect.height / 2;
		
		const mouseX = e.clientX - centerX;
		const mouseY = e.clientY - centerY;
		
		const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
		const newScale = Math.max(0.1, Math.min(5, currentScale * scaleFactor));
		
		if (newScale !== currentScale) {
			const scaleChange = newScale / currentScale;
			currentX = currentX * scaleChange;
			currentY = currentY * scaleChange;
			currentScale = newScale;
			updateTransform();
		}
	});

	// Arrastrar para paneo
	modalContent.addEventListener('mousedown', (e) => {
		if (e.target === modalImg || e.target === modalContent) {
			isDragging = true;
			startX = e.clientX - currentX;
			startY = e.clientY - currentY;
			modalContent.classList.add('dragging');
		}
	});

	document.addEventListener('mousemove', (e) => {
		if (isDragging) {
			currentX = e.clientX - startX;
			currentY = e.clientY - startY;
			updateTransform();
		}
	});

	document.addEventListener('mouseup', () => {
		isDragging = false;
		modalContent.classList.remove('dragging');
	});

	// Navegación con botones
	prevBtn.addEventListener('click', () => {
		if (currentImageIndex > 0) {
			currentImageIndex--;
			updateCurrentImage();
		}
	});

	nextBtn.addEventListener('click', () => {
		if (currentImageIndex < currentImages.length - 1) {
			currentImageIndex++;
			updateCurrentImage();
		}
	});

	// Navegación con flechas del teclado
	document.addEventListener('keydown', (e) => {
		if (modal.classList.contains('show')) {
			if (e.key === 'Escape') {
				closeModal();
			} else if (e.key === 'ArrowLeft' && currentImageIndex > 0) {
				currentImageIndex--;
				updateCurrentImage();
			} else if (e.key === 'ArrowRight' && currentImageIndex < currentImages.length - 1) {
				currentImageIndex++;
				updateCurrentImage();
			}
		}
	});

	return { openModal, closeModal };
}

function createResultWidget() {
	let result_container = document.createElement("div");
	result_container.className = "csv-u-result-container";

	let header = document.createElement("h3");
	header.innerText = "Search List";
	header.className = "csv-u-header";
	result_container.appendChild(header);

	let search_bar = document.createElement("input");
	search_bar.type = "text";
	search_bar.placeholder = "Search prompts...";
	search_bar.className = "csv-u-search-bar";
	result_container.appendChild(search_bar);

	let result_list = document.createElement("div");
	result_list.className = "csv-u-result-list";
	result_container.appendChild(result_list);

	return { result_container, result_list, search_bar };
}

app.registerExtension({
	name: "CSV-UTILS-SEARCH",

	async loadedGraphNode() {
		let style = document.createElement("style");
		style.innerHTML = `
            .csv-u-result-container { background-color: rgb(20, 20, 20); padding: 8px; border-radius: 8px; }
            .csv-u-header { text-align: center; margin-top: 0; margin-bottom: 10px; }
            .csv-u-search-bar { width: 100%; border: none; margin-bottom: 12px; background-color: white; border-radius: 4px; color: black; padding: 4px; box-sizing: border-box; }
            .csv-u-result-list { overflow-y: scroll; max-height: 300px; /* Limita la altura para que el nodo no sea gigante */ }
			.csv-u-prompt-container { display: flex; align-items: center; border-radius: 6px; padding: 5px; margin: 4px; gap: 8px; background-color: rgb(40, 40, 40); }
            .csv-u-text-prompts { display: flex; flex-direction: column; flex-grow: 1; gap: 4px; }
            .csv-u-image-container { position: relative; }
            .csv-u-preview-img { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; flex-shrink: 0; cursor: zoom-in; transition: all 0.2s ease; }
            .csv-u-preview-img:hover { transform: scale(1.05); filter: brightness(1.1); }
            .csv-u-image-counter { 
                position: absolute; 
                bottom: 2px; 
                right: 2px; 
                background: rgba(0, 0, 0, 0.8); 
                color: white; 
                padding: 2px 6px; 
                border-radius: 10px; 
                font-size: 10px; 
                font-weight: bold; 
                pointer-events: none; 
            }
            .csv-u-prompt-span { padding: 4px; font-size: x-small; color: #ddd; background-color: rgb(60, 60, 60); border-radius: 4px; cursor: pointer; word-break: break-word; }
            .csv-u-pos-span:hover { color: rgb(118, 199, 60); }
            .csv-u-neg-span:hover { color: rgb(199, 52, 57); }
            
            /* Modal Styles */
            .csv-u-modal { 
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100vw; 
                height: 100vh; 
                background: rgba(0, 0, 0, 0.95); 
                display: none; 
                justify-content: center; 
                align-items: center; 
                z-index: 10000; 
                cursor: zoom-out;
            }
            .csv-u-modal.show { display: flex; }
            .csv-u-modal-content { 
                position: relative; 
                max-width: 90vw; 
                max-height: 90vh; 
                overflow: hidden;
                cursor: grab;
            }
            .csv-u-modal-content.dragging { cursor: grabbing; }
            .csv-u-modal-img { 
                display: block; 
                max-width: none; 
                max-height: none; 
                transition: transform 0.1s ease-out;
                user-select: none;
                pointer-events: none;
            }
            .csv-u-modal-close { 
                position: absolute; 
                top: 20px; 
                right: 30px; 
                color: white; 
                font-size: 40px; 
                font-weight: bold; 
                cursor: pointer; 
                z-index: 10001;
                background: rgba(0, 0, 0, 0.5);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                line-height: 1;
            }
            .csv-u-modal-close:hover { background: rgba(255, 255, 255, 0.2); }
            .csv-u-zoom-info {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                color: white;
                background: rgba(0, 0, 0, 0.7);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 10001;
            }
            .csv-u-nav-controls {
                position: absolute;
                bottom: 60px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 10px;
                z-index: 10001;
            }
            .csv-u-nav-btn {
                background: rgba(0, 0, 0, 0.7);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s ease;
            }
            .csv-u-nav-btn:hover:not(:disabled) {
                background: rgba(255, 255, 255, 0.2);
            }
            .csv-u-nav-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .csv-u-image-counter-modal {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                color: white;
                background: rgba(0, 0, 0, 0.7);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 16px;
                z-index: 10001;
            }
		`;
		document.body.appendChild(style);
	},

	async nodeCreated(node) {
		if(node.comfyClass !== "CSVPromptSearch") return;

        const { result_container, result_list, search_bar } = createResultWidget();
        const { openModal } = createImageModal(); // Crear modal para este nodo
        node.addDOMWidget("list-results", "list", result_container);

        const updateList = async () => {
            const filePath = node.widgets[0].value;
            if (!filePath || filePath.trim() === '') {
                result_list.innerHTML = "<p style='color: #888; text-align: center;'>Please specify a CSV file path.</p>";
                return;
            }

            try {
                const promptList = await getPromptList(filePath);
                const searchTerm = search_bar.value.toLowerCase();

                // Simple filter, MiniSearch es overkill si no se necesita fuzzy search.
                const filteredList = searchTerm
                    ? promptList.filter(p => p.positive.toLowerCase().includes(searchTerm) || p.negative.toLowerCase().includes(searchTerm))
                    : promptList;

                result_list.innerHTML = ""; // Limpiar lista anterior

                if (filteredList.length === 0) {
                    result_list.innerHTML = "<p style='color: #888; text-align: center;'>No prompts found.</p>";
                    return;
                }

                for(const item of filteredList) {
                    const div = document.createElement("div");
                    div.innerHTML = create_prompt_div(item.id, item.positive, item.negative, item.image_path);
                    result_list.appendChild(div);

                                    // IMPORTANTE: Registrar eventos DESPUÉS de añadir el elemento al DOM.
                if (item.image_path) {
                    const imageEl = div.querySelector(`#csv-preview-img-${item.id}`);
                    if (imageEl) {
                        imageEl.addEventListener("click", (e) => {
                            e.stopPropagation();
                            
                            // Detectar múltiples imágenes
                            const imagePaths = item.image_path.split(/[;,]/).map(p => p.trim()).filter(p => p.length > 0);
                            
                            console.log(`[DEBUG] Click en imagen. Rutas detectadas:`, imagePaths);
                            console.log(`[DEBUG] Número de imágenes: ${imagePaths.length}`);
                            
                            if (imagePaths.length > 1) {
                                // Múltiples imágenes: usar las rutas originales para procesamiento
                                const firstImageUrl = processImagePath(imagePaths[0]);
                                console.log(`[DEBUG] Abriendo modal con múltiples imágenes. Primera URL: ${firstImageUrl}`);
                                openModal(firstImageUrl, imagePaths);
                            } else {
                                // Una sola imagen: usar también processImagePath para consistencia
                                const imageUrl = processImagePath(imagePaths[0]);
                                console.log(`[DEBUG] Abriendo modal con una imagen. URL: ${imageUrl}`);
                                openModal(imageUrl);
                            }
                        });
                    }
                }

                    // Eventos para copiar texto
                    div.querySelectorAll('.csv-u-prompt-span').forEach(span => {
                        span.addEventListener("click", (e) => {
                            navigator.clipboard.writeText(e.target.innerText);
                            app.extensionManager.toast.add({
                                severity: "success",
                                summary: "Copied to clipboard!",
                                life: 2000
                            });
                        });
                    });
                }
            } catch (error) {
                result_list.innerHTML = "<p style='color: #ff6b6b; text-align: center;'>Error loading prompts. Check the file path.</p>";
            }
        };

        let debounceTimeout;
        search_bar.addEventListener("input", () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(updateList, 300); // Espera 300ms antes de buscar
        });

        // Actualizar la lista cuando el path del archivo cambie
        const originalCallback = node.widgets[0].callback;
        node.widgets[0].callback = (value) => {
            if(originalCallback) originalCallback(value);
            updateList();
        };

        // Carga inicial con timeout para asegurar que el valor esté disponible
        setTimeout(() => {
            updateList();
        }, 100);

        // También verificar si el valor cambia después de la carga inicial
        const checkForInitialValue = () => {
            if (node.widgets[0].value && node.widgets[0].value.trim() !== '') {
                updateList();
            } else {
                setTimeout(checkForInitialValue, 200);
            }
        };
        
        checkForInitialValue();
	}
});