import os
import json
from PIL import Image
from datetime import datetime

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
            output_path = folder_paths.output_directory
            
            if not os.path.exists(output_path):
                return {"ui": {"scan_results": []}, "result": ("Error: Output folder no existe",)}
            
            # Buscar archivos PNG ordenados por fecha (más recientes primero)
            png_files = []
            for file in os.listdir(output_path):
                if file.lower().endswith('.png'):
                    file_path = os.path.join(output_path, file)
                    png_files.append({
                        'filename': file,
                        'path': file_path,
                        'mtime': os.path.getmtime(file_path)
                    })
            
            # Ordenar por fecha (más recientes primero)
            png_files.sort(key=lambda x: x['mtime'], reverse=True)
            png_files = png_files[:max_images]
            
            results = []
            processed_count = 0
            
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
                            'relative_path': file_info['filename'],  # Simplificado: solo el nombre del archivo
                            'selected': False
                        }
                        results.append(result)
                        processed_count += 1
                        
                except Exception as e:
                    print(f"Error procesando {file_info['filename']}: {e}")
                    continue
            
            status_msg = f"✅ Found {len(results)} images with prompts (from {len(png_files)} total PNG files)"
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
            return {
                "ui": {
                    "scan_results": [],
                    "status": error_msg
                },
                "result": (error_msg,)
            }
    
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
            print(f"Error extrayendo prompts de {image_path}: {e}")
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