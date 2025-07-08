# ComfyUI CSV Utils - Enhanced

Un conjunto completo de nodos para ComfyUI que permite guardar, buscar y gestionar prompts utilizando archivos CSV con soporte completo para imágenes.

## 🚀 Características

- **💾 Guardado Manual**: Guarda prompts manualmente con `CSV Prompt Saver`
- **🔍 Búsqueda Visual**: Navega prompts guardados con visor de imágenes en `CSV Prompt Search`
- **📸 Historial Automático**: Extrae prompts de imágenes generadas con `CSV History Scanner`
- **🖼️ Visor con Zoom**: Modal de imagen con zoom y pan (como ComfyUI nativo)
- **🗂️ Soporte Subdirectorios**: Funciona con `preview/` y otros subdirectorios
- **🔄 Imágenes Múltiples**: Soporte para múltiples imágenes por entrada (separadas por `;` o `,`)

## 📦 Instalación

1. Descarga o clona este repositorio en tu carpeta `custom_nodes` de ComfyUI
2. Reinicia ComfyUI
3. Los nodos aparecerán en la categoría "CSV Utils"

## 🛠️ Nodos Disponibles

### 1. CSV Prompt Saver
**Propósito**: Guardar prompts manualmente a un archivo CSV

**Entradas**:
- `positive_prompt`: Prompt positivo
- `negative_prompt`: Prompt negativo  
- `file_path`: Ruta del archivo CSV (ej: "prompts.csv")
- `image_path`: Ruta de imagen(es) opcional

**Características**:
- Previene duplicados automáticamente
- Soporte para múltiples imágenes separadas por `;` o `,`
- Interfaz web para ver prompts guardados

### 2. CSV Prompt Search  
**Propósito**: Buscar y navegar prompts guardados visualmente

**Entradas**:
- `csv_file_path`: Ruta del archivo CSV a leer (recuerda la última ubicación usada)

**Características**:
- **Memoria persistente** - recuerda automáticamente la última ruta CSV usada
- **Grid de thumbnails** con vista previa de imágenes
- **Modal con zoom/pan** - usa scroll para zoom, arrastra para mover
- **Navegación por teclado** - flechas, Escape para cerrar
- **Múltiples imágenes** - contador "1/5" en thumbnails, navegación automática
- **Soporte subdirectorios** - busca en `preview/`, root y recursivamente
- **Valor por defecto inteligente** - sugiere `output/prompt_history.csv`

**Controles del Modal**:
- `Scroll`: Zoom in/out (0.1x - 5x)
- `Click y arrastrar`: Pan/mover imagen
- `Escape o click fuera`: Cerrar modal
- `Flechas` (múltiples imágenes): Navegar entre imágenes

### 3. CSV History Scanner ⭐ **NUEVO**
**Propósito**: Revisar historial de imágenes generadas, extraer prompts y organizar colección

**Entradas**:
- `max_images`: Máximo número de imágenes a escanear (10-200)
- `scan_button`: Botón para ejecutar escaneo

**Características**:
- **Extracción automática** de prompts desde metadata PNG de ComfyUI
- **Agrupación inteligente** por prompts idénticos
- **Selección granular** - checkboxes por grupo e imagen individual
- **Modal de zoom** para vista detallada de imágenes
- **Organización automática** - mueve imágenes a `output/preview/`
- **CSV centralizado** - guarda en `output/prompt_history.csv`
- **Sin duplicados** - previene entradas repetidas

**Flujo de trabajo**:
1. Ejecuta el nodo para escanear folder output
2. Se abre panel con grupos de prompts y thumbnails
3. Selecciona grupos completos O imágenes individuales
4. Click "Move & Save" para organizar tu colección
5. Las imágenes se mueven a `output/preview/` y prompts se guardan en CSV

## 🎯 Casos de Uso

### Workflow Completo Automatizado
1. **Generar imágenes** en ComfyUI (automáticamente guarda metadata)
2. **Usar CSV History Scanner** para revisar generaciones recientes
3. **Seleccionar las mejores** (por grupo o individualmente)
4. **Click "Move & Save"** - automáticamente organiza todo:
   - 🖼️ Mueve imágenes a `output/preview/`
   - 📊 Guarda prompts en `output/prompt_history.csv`
5. **Usar CSV Prompt Search** para navegar tu colección organizada

### Gestión de Colecciones Organizada
- **Ubicación fija**: Todo en `output/preview/` y `output/prompt_history.csv`
- **Workflow limpio**: Las imágenes generadas se quedan en output, las curadas van a preview
- **Fácil navegación**: Usa CSV Prompt Search para explorar tu colección
- **Sin duplicados**: El sistema previene guardar el mismo prompt dos veces

## 🔧 Formato CSV

El formato CSV es simple y compatible:
```csv
positive_prompt,negative_prompt,image_path
"beautiful portrait, detailed",bad quality,"image1.png;image2.png"
"landscape, mountains",blurry,"preview/landscape.png"
```

**Notas**:
- **Múltiples imágenes**: Separar con `;` o `,`
- **Subdirectorios**: Soporta `preview/`, rutas relativas y absolutas
- **Encoding**: UTF-8 para caracteres especiales

## 🖼️ Soporte de Imágenes

### Rutas Soportadas
- `image.png` (en output root)
- `preview/image.png` (subdirectorio preview)
- `subfolder/image.png` (cualquier subdirectorio)
- Rutas absolutas y relativas

### Búsqueda Inteligente
El sistema busca imágenes en orden de prioridad:
1. Ruta exacta especificada
2. `preview/filename` si no se especifica directorio
3. `filename` en root
4. Búsqueda recursiva en subdirectorios

### Múltiples Imágenes
- Separar con `;` o `,` en el CSV
- Contador automático en thumbnails ("1/3")
- Navegación automática en modal

## 🎮 Controles del Visor

### Modal de Imagen
- **Zoom**: Rueda del ratón (10% - 500%)
- **Pan**: Click y arrastrar
- **Cerrar**: Escape, click fuera, o botón X
- **Navegación**: Flechas (si hay múltiples imágenes)

### History Scanner
- **Select All/None**: Selección rápida
- **Checkboxes**: Selección individual
- **Move & Save**: Guarda seleccionados y organiza archivos
- **Panel movible**: Arrastra desde header para reposicionar

## 💾 Memoria Persistente

### CSV Prompt Search
El nodo **recuerda automáticamente** la última ruta CSV que usaste:
- ✅ **Auto-carga** la ruta al crear un nuevo nodo
- 🔄 **Persiste** entre reinicios de ComfyUI
- 📁 **Toast informativo** cuando carga ruta guardada
- 🎯 **Valor por defecto** sugiere `output/prompt_history.csv`

**Funcionamiento**:
1. La primera vez, establece la ruta manualmente
2. El sistema guarda automáticamente esa ubicación
3. Los próximos nodos CSV Prompt Search usarán esa ruta por defecto
4. Si cambias la ruta, el sistema recuerda la nueva ubicación

## 🔍 Troubleshooting

### Imágenes no se muestran
1. Verifica que las rutas en CSV sean correctas
2. Usa rutas relativas al output folder de ComfyUI
3. El sistema buscará automáticamente en subdirectorios

### History Scanner no encuentra imágenes
1. Verifica que las imágenes tengan metadata de ComfyUI
2. Solo procesa archivos PNG con workflow embebido
3. Aumenta `max_images` si hay muchas imágenes

### Prompts no se extraen
1. Asegúrate que las imágenes se generaron con ComfyUI
2. Verifica que contengan nodos `CLIPTextEncode` en el workflow
3. Algunas imágenes externas no tendrán metadata

## 📝 Notas de Desarrollo

- Compatible con ComfyUI workflow metadata
- Utiliza endpoints personalizados para servir imágenes
- Previene duplicados automáticamente
- Interfaz responsive y moderna
- Soporte completo para caracteres Unicode

## 🔄 Changelog

### v2.0 (Current)
- ➕ Agregado CSV History Scanner
- 🔍 Modal de zoom/pan mejorado  
- 📁 Soporte completo para subdirectorios
- 🖼️ Múltiples imágenes por entrada
- 🎨 Interfaz moderna y responsive

### v1.0
- CSV Prompt Saver y Search básicos
- Funcionalidad core de CSV

---

**Desarrollado para ComfyUI - Gestión visual de prompts simplificada** 🎨