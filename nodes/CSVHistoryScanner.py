import os
import json
from PIL import Image
from datetime import datetime
import glob

try:
    import folder_paths
except ImportError:
    # Fallback for testing outside ComfyUI
    class FolderPaths:
        output_directory = "C:\\ComfyUI\\output"
    folder_paths = FolderPaths()

class CSVHistoryScanner:
    """
    Escanea imágenes generadas, extrae prompts y organiza en colección preview
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_images": ("INT", {"default": 50, "min": 10, "max": 200}),
                "scan_button": ("BOOLEAN", {"default": False, "label_on": "Scan Images", "label_off": "Scan Images"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "scan_and_display"
    CATEGORY = "CSV Utils"
    OUTPUT_NODE = True  # Esto es importante para que se ejecute y envíe datos al frontend
    
    def scan_and_display(self, max_images, scan_button):
        """
        Escanea imágenes del output y prepara datos para la interfaz web
        Las imágenes seleccionadas se moverán a output/preview/ y se guardarán en output/prompt_history.csv
        """
        try:
            # Debug info
            output_path = folder_paths.output_directory
            print(f"[CSV History Scanner] Output path: {output_path}")
            print(f"[CSV History Scanner] Path exists: {os.path.exists(output_path)}")
            print(f"[CSV History Scanner] Path readable: {os.access(output_path, os.R_OK)}")
            
            if not os.path.exists(output_path):
                return {"ui": {"scan_results": []}, "result": (f"Error: Output folder doesn't exist: {output_path}",)}
            
            if not os.access(output_path, os.R_OK):
                return {"ui": {"scan_results": []}, "result": (f"Error: Cannot read output folder: {output_path}",)}
            
            # Buscar archivos PNG con múltiples métodos
            png_files = self.find_png_files(output_path, max_images)
            print(f"[CSV History Scanner] Found {len(png_files)} PNG files")
            
            if not png_files:
                # Intentar métodos alternativos de búsqueda
                alt_files = self.alternative_search(output_path)
                print(f"[CSV History Scanner] Alternative search found: {len(alt_files)} files")
                return {"ui": {"scan_results": []}, "result": (f"No PNG files found in {output_path}. Alternative search found {len(alt_files)} files. Check permissions and metadata.",)}
            
            results = []
            processed_count = 0
            metadata_count = 0
            
            for file_info in png_files:
                try:
                    prompts = self.extract_prompts_from_image(file_info['path'])
                    if prompts and (prompts.get('positive') or prompts.get('negative')):
                        result = {
                            'id': processed_count,
                            'filename': file_info['filename'],
                            'positive_prompt': prompts.get('positive', ''),
                            'negative_prompt': prompts.get('negative', ''),
                            'date': datetime.fromtimestamp(file_info['mtime']).strftime("%Y-%m-%d %H:%M:%S"),
                            'relative_path': file_info['relative_path'],
                            'selected': False
                        }
                        results.append(result)
                        processed_count += 1
                        metadata_count += 1
                    else:
                        # Archivo PNG sin metadata válida
                        pass
                        
                except Exception as e:
                    print(f"[CSV History Scanner] Error processing {file_info['filename']}: {e}")
                    continue
            
            status_msg = f"✅ Found {len(results)} images with prompts (from {len(png_files)} PNG files, {metadata_count} with metadata)"
            status_msg += f"\nOutput folder: {output_path}"
            status_msg += f"\nSelected images will be moved to output/preview/ and saved to output/prompt_history.csv"
            
            # Pasar resultados al frontend
            return {
                "ui": {
                    "scan_results": results,
                    "status": status_msg
                },
                "result": (status_msg,)
            }
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[CSV History Scanner] Exception: {e}")
            return {
                "ui": {
                    "scan_results": [],
                    "status": error_msg
                },
                "result": (error_msg,)
            }
    
    def find_png_files(self, output_path, max_images):
        """
        Busca archivos PNG con múltiples métodos para mayor compatibilidad
        """
        png_files = []
        
        try:
            # Método 1: Buscar directamente en el directorio
            for file in os.listdir(output_path):
                if file.lower().endswith('.png'):
                    file_path = os.path.join(output_path, file)
                    if os.path.isfile(file_path):
                        png_files.append({
                            'filename': file,
                            'path': file_path,
                            'relative_path': file,
                            'mtime': os.path.getmtime(file_path)
                        })
        except Exception as e:
            print(f"[CSV History Scanner] Error with os.listdir: {e}")
        
        # Método 2: Si no encontramos nada, buscar recursivamente
        if not png_files:
            try:
                pattern = os.path.join(output_path, "**", "*.png")
                for file_path in glob.glob(pattern, recursive=True):
                    if os.path.isfile(file_path):
                        filename = os.path.basename(file_path)
                        relative_path = os.path.relpath(file_path, output_path)
                        png_files.append({
                            'filename': filename,
                            'path': file_path,
                            'relative_path': relative_path,
                            'mtime': os.path.getmtime(file_path)
                        })
            except Exception as e:
                print(f"[CSV History Scanner] Error with glob search: {e}")
        
        # Método 3: Buscar específicamente en subdirectorios conocidos
        if not png_files:
            known_subdirs = ['', 'preview', 'temp', 'output']
            for subdir in known_subdirs:
                try:
                    search_path = os.path.join(output_path, subdir) if subdir else output_path
                    if os.path.exists(search_path):
                        for file in os.listdir(search_path):
                            if file.lower().endswith('.png'):
                                file_path = os.path.join(search_path, file)
                                if os.path.isfile(file_path):
                                    relative_path = os.path.join(subdir, file) if subdir else file
                                    png_files.append({
                                        'filename': file,
                                        'path': file_path,
                                        'relative_path': relative_path,
                                        'mtime': os.path.getmtime(file_path)
                                    })
                except Exception as e:
                    print(f"[CSV History Scanner] Error searching in {subdir}: {e}")
        
        # Ordenar por fecha (más recientes primero) y limitar
        png_files.sort(key=lambda x: x['mtime'], reverse=True)
        return png_files[:max_images]
    
    def alternative_search(self, output_path):
        """
        Búsqueda alternativa para debug - encuentra cualquier archivo
        """
        try:
            all_files = []
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    all_files.append(os.path.join(root, file))
            return all_files
        except:
            return []
    
    def extract_prompts_from_image(self, image_path):
        """
        Extrae prompts de la metadata de una imagen PNG de ComfyUI
        """
        try:
            img = Image.open(image_path)
            
            # Debug: mostrar qué metadata está disponible
            metadata_keys = list(img.text.keys()) if hasattr(img, 'text') else []
            print(f"[CSV History Scanner] {os.path.basename(image_path)} metadata keys: {metadata_keys}")
            
            # Verificar diferentes formas de metadata
            workflow_data = None
            
            # Método 1: metadata 'workflow'
            if hasattr(img, 'text') and 'workflow' in img.text:
                try:
                    workflow_data = json.loads(img.text['workflow'])
                except:
                    pass
            
            # Método 2: metadata 'prompt' (formato alternativo)
            if not workflow_data and hasattr(img, 'text') and 'prompt' in img.text:
                try:
                    prompt_data = json.loads(img.text['prompt'])
                    # Convertir formato prompt a formato workflow si es necesario
                    workflow_data = {'nodes': []}
                    for node_id, node_data in prompt_data.items():
                        if node_data.get('class_type') == 'CLIPTextEncode':
                            workflow_data['nodes'].append({
                                'type': 'CLIPTextEncode',
                                'widgets_values': [node_data.get('inputs', {}).get('text', '')]
                            })
                except:
                    pass
            
            if not workflow_data:
                print(f"[CSV History Scanner] No valid workflow data in {os.path.basename(image_path)}")
                return None
                
            # Buscar nodos CLIPTextEncode
            prompts = []
            for node in workflow_data.get('nodes', []):
                if node.get('type') == 'CLIPTextEncode':
                    if 'widgets_values' in node and node['widgets_values']:
                        prompt_text = node['widgets_values'][0]
                        if prompt_text and prompt_text.strip():
                            prompts.append(prompt_text.strip())
            
            # Detectar positivo vs negativo
            positive_prompt = ""
            negative_prompt = ""
            
            if len(prompts) >= 1:
                positive_prompt = prompts[0]
            if len(prompts) >= 2:
                negative_prompt = prompts[1]
                
                # Intercambiar si el primero parece negativo
                if self.seems_negative_prompt(prompts[0]) and not self.seems_negative_prompt(prompts[1]):
                    positive_prompt = prompts[1]
                    negative_prompt = prompts[0]
            
            return {
                'positive': positive_prompt,
                'negative': negative_prompt
            }
            
        except Exception as e:
            print(f"[CSV History Scanner] Error extracting prompts from {image_path}: {e}")
            return None
    
    def seems_negative_prompt(self, prompt):
        """
        Detecta si un prompt parece ser negativo
        """
        negative_indicators = [
            'low quality', 'blurry', 'bad anatomy', 'deformed', 
            'worst quality', 'ugly', 'mutation', 'extra limbs',
            'bad hands', 'missing fingers', 'extra fingers'
        ]
        
        prompt_lower = prompt.lower()
        return sum(1 for indicator in negative_indicators if indicator in prompt_lower) >= 2


# Registrar el nodo
NODE_CLASS_MAPPINGS = {
    "CSVHistoryScanner": CSVHistoryScanner
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CSVHistoryScanner": "CSV History Scanner"
} 