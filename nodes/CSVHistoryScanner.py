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
                "max_images": ("INT", {"default": 100, "min": 10, "max": 1000}),
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
            
            # Buscar archivos PNG con múltiples métodos - SIN LÍMITE para análisis
            png_files = self.find_png_files(output_path, max_images)
            print(f"[CSV History Scanner] Found {len(png_files)} PNG files")
            
            if not png_files:
                # Intentar métodos alternativos de búsqueda
                alt_files = self.alternative_search(output_path)
                print(f"[CSV History Scanner] Alternative search found: {len(alt_files)} files")
                return {"ui": {"scan_results": []}, "result": (f"No PNG files found in {output_path}. Alternative search found {len(alt_files)} files. Check permissions and metadata.",)}
            
            # Procesar TODAS las imágenes para extraer prompts
            prompt_groups = {}  # {prompt_key: [images]}
            processed_count = 0
            metadata_count = 0
            
            print(f"[CSV History Scanner] Processing {len(png_files)} images for prompt extraction...")
            
            for file_info in png_files:
                try:
                    prompts = self.extract_prompts_from_image(file_info['path'])
                    if prompts and (prompts.get('positive') or prompts.get('negative')):
                        # Crear clave única para agrupar prompts idénticos
                        prompt_key = f"{prompts.get('positive', '')}<SEP>{prompts.get('negative', '')}"
                        
                        # Agregar imagen al grupo
                        if prompt_key not in prompt_groups:
                            prompt_groups[prompt_key] = []
                        
                        image_data = {
                            'id': processed_count,
                            'filename': file_info['filename'],
                            'positive_prompt': prompts.get('positive', ''),
                            'negative_prompt': prompts.get('negative', ''),
                            'date': datetime.fromtimestamp(file_info['mtime']).strftime("%Y-%m-%d %H:%M:%S"),
                            'relative_path': file_info['relative_path'],
                            'selected': False
                        }
                        
                        prompt_groups[prompt_key].append(image_data)
                        processed_count += 1
                        metadata_count += 1
                        
                except Exception as e:
                    print(f"[CSV History Scanner] Error processing {file_info['filename']}: {e}")
                    continue
            
            # Limitar a máximo 10 imágenes por grupo de prompt
            results = []
            total_groups = len(prompt_groups)
            total_images_shown = 0
            
            print(f"[CSV History Scanner] Found {total_groups} unique prompt groups")
            
            for prompt_key, images in prompt_groups.items():
                # Ordenar por fecha (más recientes primero) y tomar máximo 10
                images.sort(key=lambda x: x['date'], reverse=True)
                limited_images = images[:10]  # Máximo 10 imágenes por prompt
                
                # Re-asignar IDs secuenciales
                for i, img in enumerate(limited_images):
                    img['id'] = len(results) + i
                
                results.extend(limited_images)
                total_images_shown += len(limited_images)
                
                if len(images) > 10:
                    print(f"[CSV History Scanner] Prompt group '{images[0]['positive_prompt'][:50]}...' had {len(images)} images, showing 10 most recent")
            
            status_msg = f"✅ Found {total_groups} unique prompts with {metadata_count} total images"
            status_msg += f"\nShowing {total_images_shown} images (max 10 per prompt)"
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
        Busca archivos PNG SOLO en el directorio principal de output
        NUNCA busca en preview/ (esas son imágenes ya organizadas)
        """
        png_files = []
        
        try:
            # Método 1: Buscar SOLO directamente en el directorio principal
            print(f"[CSV History Scanner] Searching for PNG files in: {output_path}")
            for file in os.listdir(output_path):
                if file.lower().endswith('.png'):
                    file_path = os.path.join(output_path, file)
                    # Verificar que sea archivo y NO esté en preview
                    if os.path.isfile(file_path):
                        png_files.append({
                            'filename': file,
                            'path': file_path,
                            'relative_path': file,
                            'mtime': os.path.getmtime(file_path)
                        })
                        print(f"[CSV History Scanner] Found PNG: {file}")
        except Exception as e:
            print(f"[CSV History Scanner] Error with os.listdir: {e}")
        
        # Si no encontramos nada en el directorio principal, intentar con subdirectorios
        # PERO EXCLUIR EXPLÍCITAMENTE preview y otros directorios de imágenes organizadas
        if not png_files:
            try:
                print(f"[CSV History Scanner] No files in main directory, checking subdirectories (excluding preview)")
                # Solo buscar en subdirectorios que NO sean preview, temp, etc.
                excluded_dirs = {'preview', 'temp', 'tmp', 'archive', 'organized'}
                
                for item in os.listdir(output_path):
                    item_path = os.path.join(output_path, item)
                    if os.path.isdir(item_path) and item.lower() not in excluded_dirs:
                        print(f"[CSV History Scanner] Checking subdirectory: {item}")
                        try:
                            for file in os.listdir(item_path):
                                if file.lower().endswith('.png'):
                                    file_path = os.path.join(item_path, file)
                                    if os.path.isfile(file_path):
                                        relative_path = os.path.join(item, file)
                                        png_files.append({
                                            'filename': file,
                                            'path': file_path,
                                            'relative_path': relative_path,
                                            'mtime': os.path.getmtime(file_path)
                                        })
                                        print(f"[CSV History Scanner] Found PNG in {item}: {file}")
                        except Exception as e:
                            print(f"[CSV History Scanner] Error searching in {item}: {e}")
            except Exception as e:
                print(f"[CSV History Scanner] Error with subdirectory search: {e}")
        
        # Ordenar por fecha (más recientes primero) y limitar
        png_files.sort(key=lambda x: x['mtime'], reverse=True)
        
        print(f"[CSV History Scanner] Total PNG files found: {len(png_files)} (excluding preview folder)")
        if png_files:
            print(f"[CSV History Scanner] Sample files: {[f['filename'] for f in png_files[:3]]}")
        
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
            positive_prompt = ""
            negative_prompt = ""
            
            # Método 1: metadata 'prompt' (más común en vast.ai)
            if hasattr(img, 'text') and 'prompt' in img.text:
                try:
                    prompt_data = json.loads(img.text['prompt'])
                    print(f"[CSV History Scanner] Processing prompt data for {os.path.basename(image_path)}")
                    print(f"[CSV History Scanner] Prompt data keys: {list(prompt_data.keys())}")
                    
                    # Buscar nodos CLIPTextEncode en el formato prompt
                    prompts = []
                    for node_id, node_data in prompt_data.items():
                        print(f"[CSV History Scanner] Node {node_id}: class_type = {node_data.get('class_type', 'unknown')}")
                        
                        # Nodos estándar CLIPTextEncode
                        if node_data.get('class_type') == 'CLIPTextEncode':
                            print(f"[CSV History Scanner] Found CLIPTextEncode node: {node_id}")
                            print(f"[CSV History Scanner] Node data keys: {list(node_data.keys())}")
                            # Buscar en inputs
                            if 'inputs' in node_data:
                                print(f"[CSV History Scanner] Inputs: {node_data['inputs']}")
                                if 'text' in node_data['inputs']:
                                    prompt_text = node_data['inputs']['text']
                                    print(f"[CSV History Scanner] Found text in inputs: {prompt_text}")
                                    if prompt_text and prompt_text.strip():
                                        prompts.append(prompt_text.strip())
                                        print(f"[CSV History Scanner] Added prompt: {prompt_text[:50]}...")
                                else:
                                    print(f"[CSV History Scanner] No 'text' key in inputs")
                            else:
                                print(f"[CSV History Scanner] No 'inputs' key in node data")
                        
                        # Nodos Efficiency (común en vast.ai)
                        elif node_data.get('class_type') == 'Efficient Loader':
                            print(f"[CSV History Scanner] Found Efficient Loader node: {node_id}")
                            print(f"[CSV History Scanner] Node data keys: {list(node_data.keys())}")
                            if 'inputs' in node_data:
                                print(f"[CSV History Scanner] Efficient Loader inputs: {node_data['inputs']}")
                                # Los prompts en Efficient Loader suelen estar en 'positive' y 'negative'
                                if 'positive' in node_data['inputs']:
                                    pos_text = node_data['inputs']['positive']
                                    print(f"[CSV History Scanner] Found positive text: {pos_text}")
                                    if pos_text and pos_text.strip():
                                        prompts.append(pos_text.strip())
                                        print(f"[CSV History Scanner] Added positive prompt: {pos_text[:50]}...")
                                
                                if 'negative' in node_data['inputs']:
                                    neg_text = node_data['inputs']['negative']
                                    print(f"[CSV History Scanner] Found negative text: {neg_text}")
                                    if neg_text and neg_text.strip():
                                        prompts.append(neg_text.strip())
                                        print(f"[CSV History Scanner] Added negative prompt: {neg_text[:50]}...")
                            else:
                                print(f"[CSV History Scanner] No 'inputs' key in Efficient Loader")
                        
                        # Otros nodos que podrían contener prompts
                        elif 'text' in node_data.get('class_type', '').lower() or 'prompt' in node_data.get('class_type', '').lower():
                            print(f"[CSV History Scanner] Found potential text node: {node_id} ({node_data.get('class_type')})")
                            if 'inputs' in node_data:
                                print(f"[CSV History Scanner] Text node inputs: {node_data['inputs']}")
                                # Buscar cualquier campo que pueda contener texto
                                for key, value in node_data['inputs'].items():
                                    if isinstance(value, str) and len(value) > 10:  # Probablemente un prompt
                                        print(f"[CSV History Scanner] Found text in {key}: {value}")
                                        if value.strip():
                                            prompts.append(value.strip())
                                            print(f"[CSV History Scanner] Added text prompt: {value[:50]}...")
                    
                    print(f"[CSV History Scanner] Total prompts found: {len(prompts)}")
                    
                    # Asignar prompts
                    if len(prompts) >= 1:
                        positive_prompt = prompts[0]
                    if len(prompts) >= 2:
                        negative_prompt = prompts[1]
                        
                        # Intercambiar si el primero parece negativo
                        if self.seems_negative_prompt(prompts[0]) and not self.seems_negative_prompt(prompts[1]):
                            positive_prompt = prompts[1]
                            negative_prompt = prompts[0]
                    
                    print(f"[CSV History Scanner] Final assignment - Positive: '{positive_prompt}', Negative: '{negative_prompt}'")
                    
                except Exception as e:
                    print(f"[CSV History Scanner] Error processing prompt metadata: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Método 2: metadata 'workflow' (formato alternativo)
            if not positive_prompt and hasattr(img, 'text') and 'workflow' in img.text:
                try:
                    workflow_data = json.loads(img.text['workflow'])
                    print(f"[CSV History Scanner] Processing workflow data for {os.path.basename(image_path)}")
                    
                    # Buscar nodos CLIPTextEncode
                    prompts = []
                    for node in workflow_data.get('nodes', []):
                        if node.get('type') == 'CLIPTextEncode':
                            if 'widgets_values' in node and node['widgets_values']:
                                prompt_text = node['widgets_values'][0]
                                if prompt_text and prompt_text.strip():
                                    prompts.append(prompt_text.strip())
                                    print(f"[CSV History Scanner] Found workflow prompt: {prompt_text[:50]}...")
                    
                    # Asignar prompts
                    if len(prompts) >= 1:
                        positive_prompt = prompts[0]
                    if len(prompts) >= 2:
                        negative_prompt = prompts[1]
                        
                        # Intercambiar si el primero parece negativo
                        if self.seems_negative_prompt(prompts[0]) and not self.seems_negative_prompt(prompts[1]):
                            positive_prompt = prompts[1]
                            negative_prompt = prompts[0]
                    
                    print(f"[CSV History Scanner] Extracted from workflow - Positive: {positive_prompt[:30]}..., Negative: {negative_prompt[:30]}...")
                    
                except Exception as e:
                    print(f"[CSV History Scanner] Error processing workflow metadata: {e}")
            
            # Verificar que obtuvimos algo
            if positive_prompt or negative_prompt:
                return {
                    'positive': positive_prompt,
                    'negative': negative_prompt
                }
            else:
                print(f"[CSV History Scanner] No valid prompts found in {os.path.basename(image_path)}")
                return None
                
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