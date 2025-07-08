import os
import json
from PIL import Image
from datetime import datetime
import folder_paths

class CSVHistoryScanner:
    """
    Nodo para escanear el historial de imágenes generadas y extraer prompts
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scan_folder": (["output", "output/preview"], {"default": "output"}),
                "max_images": ("INT", {"default": 50, "min": 1, "max": 500}),
                "sort_by": (["date_desc", "date_asc", "name"], {"default": "date_desc"}),
            },
            "optional": {
                "refresh": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("scan_results", "images_found")
    FUNCTION = "scan_history"
    CATEGORY = "CSV Utils"
    
    def scan_history(self, scan_folder, max_images, sort_by, refresh=False):
        """
        Escanea las imágenes generadas y extrae los prompts de su metadata
        """
        try:
            # Determinar el folder a escanear
            if scan_folder == "output":
                scan_path = folder_paths.output_directory
            else:
                scan_path = os.path.join(folder_paths.output_directory, "preview")
            
            if not os.path.exists(scan_path):
                return (f"Error: Folder no existe: {scan_path}", 0)
            
            # Buscar archivos PNG
            png_files = []
            for file in os.listdir(scan_path):
                if file.lower().endswith('.png'):
                    file_path = os.path.join(scan_path, file)
                    png_files.append({
                        'filename': file,
                        'path': file_path,
                        'mtime': os.path.getmtime(file_path)
                    })
            
            # Ordenar archivos
            if sort_by == "date_desc":
                png_files.sort(key=lambda x: x['mtime'], reverse=True)
            elif sort_by == "date_asc":
                png_files.sort(key=lambda x: x['mtime'])
            else:  # name
                png_files.sort(key=lambda x: x['filename'])
            
            # Limitar cantidad
            png_files = png_files[:max_images]
            
            results = []
            processed_count = 0
            
            for file_info in png_files:
                try:
                    prompts = self.extract_prompts_from_image(file_info['path'])
                    if prompts:
                        result = {
                            'id': processed_count,
                            'filename': file_info['filename'],
                            'positive_prompt': prompts.get('positive', ''),
                            'negative_prompt': prompts.get('negative', ''),
                            'date': datetime.fromtimestamp(file_info['mtime']).strftime("%Y-%m-%d %H:%M:%S"),
                            'relative_path': os.path.relpath(file_info['path'], folder_paths.output_directory).replace('\\', '/'),
                            'selected': False
                        }
                        results.append(result)
                        processed_count += 1
                        
                except Exception as e:
                    print(f"Error procesando {file_info['filename']}: {e}")
                    continue
            
            # Convertir a JSON string para el frontend
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            
            return (results_json, len(results))
            
        except Exception as e:
            return (f"Error: {str(e)}", 0)
    
    def extract_prompts_from_image(self, image_path):
        """
        Extrae prompts de la metadata de una imagen PNG de ComfyUI
        """
        try:
            img = Image.open(image_path)
            
            if not hasattr(img, 'text') or 'workflow' not in img.text:
                return None
                
            workflow_data = json.loads(img.text['workflow'])
            
            # Buscar nodos CLIPTextEncode
            prompts = []
            for node in workflow_data.get('nodes', []):
                if node.get('type') == 'CLIPTextEncode':
                    if 'widgets_values' in node and node['widgets_values']:
                        prompt_text = node['widgets_values'][0]
                        if prompt_text and prompt_text.strip():
                            prompts.append(prompt_text.strip())
            
            # Heurística para detectar positivo vs negativo
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
            print(f"Error extrayendo prompts de {image_path}: {e}")
            return None
    
    def seems_negative_prompt(self, prompt):
        """
        Heurística simple para detectar si un prompt es negativo
        """
        negative_indicators = [
            'low quality', 'blurry', 'bad anatomy', 'deformed', 
            'worst quality', 'ugly', 'mutation', 'extra limbs',
            'bad hands', 'missing fingers', 'extra fingers'
        ]
        
        prompt_lower = prompt.lower()
        negative_count = sum(1 for indicator in negative_indicators if indicator in prompt_lower)
        
        return negative_count >= 2  # Si tiene 2+ indicadores negativos


# Registrar el nodo
NODE_CLASS_MAPPINGS = {
    "CSVHistoryScanner": CSVHistoryScanner
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CSVHistoryScanner": "CSV History Scanner"
} 