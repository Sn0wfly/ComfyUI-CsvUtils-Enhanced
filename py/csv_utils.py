import csv
import os
import shutil
from aiohttp import web
import server
import folder_paths
import json


DELIMITER = ","

def save_to_csv(file_path : str , pos_prompt :str , neg_prompt :str, image_path: str = "") : 
        
        if already_exists(file_path , pos_prompt , neg_prompt) : 
            return False
                
        with open(file_path , 'a' , newline='' , encoding="utf8") as csv_file:

            writer_object = csv.writer(csv_file , delimiter=DELIMITER)

            print("prompt put in the row :" , pos_prompt)
            writer_object.writerow([pos_prompt , neg_prompt, image_path])

            csv_file.close()

        return True

def save_multiple_to_csv_with_move(entries: list) -> dict:
    """
    Guarda múltiples entradas en CSV y mueve imágenes a preview folder
    """
    try:
        output_dir = folder_paths.output_directory
        
        # Hardcodear ubicación del CSV en output folder
        csv_file_path = os.path.join(output_dir, "prompt_history.csv")
        
        # Asegurar que existe el directorio preview
        preview_dir = os.path.join(output_dir, "preview")
        os.makedirs(preview_dir, exist_ok=True)
        
        saved_count = 0
        skipped_count = 0
        moved_count = 0
        
        with open(csv_file_path, 'a', newline='', encoding="utf8") as csv_file:
            writer_object = csv.writer(csv_file, delimiter=DELIMITER)
            
            for entry in entries:
                pos_prompt = entry.get('positive_prompt', '').strip()
                neg_prompt = entry.get('negative_prompt', '').strip()
                original_image_path = entry.get('image_path', '').strip()
                
                if not original_image_path:
                    continue
                    
                # Construir rutas completas
                source_path = os.path.join(output_dir, original_image_path)
                filename = os.path.basename(original_image_path)
                dest_path = os.path.join(preview_dir, filename)
                preview_relative_path = f"preview/{filename}"
                
                # Verificar si ya existe el prompt (con la nueva ruta)
                if not already_exists(csv_file_path, pos_prompt, neg_prompt):
                    try:
                        # Mover imagen a preview folder (solo si no está ya ahí)
                        if os.path.exists(source_path) and source_path != dest_path:
                            if os.path.exists(dest_path):
                                # Si ya existe en destino, generar nombre único
                                base_name, ext = os.path.splitext(filename)
                                counter = 1
                                while os.path.exists(dest_path):
                                    new_filename = f"{base_name}_{counter}{ext}"
                                    dest_path = os.path.join(preview_dir, new_filename)
                                    preview_relative_path = f"preview/{new_filename}"
                                    counter += 1
                            
                            shutil.move(source_path, dest_path)
                            moved_count += 1
                            print(f"[CSV] Moved image: {original_image_path} -> {preview_relative_path}")
                        
                        # Guardar en CSV con la nueva ruta en preview
                        writer_object.writerow([pos_prompt, neg_prompt, preview_relative_path])
                        saved_count += 1
                        print(f"[CSV] Saved: {pos_prompt[:50]}...")
                        
                    except Exception as e:
                        print(f"[CSV] Error moving image {original_image_path}: {e}")
                        # Si falla el movimiento, guardar con ruta original
                        writer_object.writerow([pos_prompt, neg_prompt, original_image_path])
                        saved_count += 1
                else:
                    skipped_count += 1
                    print(f"[CSV] Skipped duplicate: {pos_prompt[:50]}...")
        
        return {
            'success': True,
            'saved': saved_count,
            'skipped': skipped_count,
            'moved': moved_count,
            'csv_path': csv_file_path,
            'message': f'Saved {saved_count} prompts, moved {moved_count} images to preview folder. Skipped {skipped_count} duplicates.'
        }
        
    except Exception as e:
        print(f"[CSV] Error saving with move: {e}")
        return {
            'success': False,
            'message': str(e)
        }

def save_multiple_to_csv(file_path: str, entries: list) -> dict:
    """
    Guarda múltiples entradas en CSV, evitando duplicados (versión original)
    """
    try:
        saved_count = 0
        skipped_count = 0
        
        with open(file_path, 'a', newline='', encoding="utf8") as csv_file:
            writer_object = csv.writer(csv_file, delimiter=DELIMITER)
            
            for entry in entries:
                pos_prompt = entry.get('positive_prompt', '').strip()
                neg_prompt = entry.get('negative_prompt', '').strip()
                image_path = entry.get('image_path', '').strip()
                
                # Verificar si ya existe
                if not already_exists(file_path, pos_prompt, neg_prompt):
                    writer_object.writerow([pos_prompt, neg_prompt, image_path])
                    saved_count += 1
                    print(f"[CSV] Saved: {pos_prompt[:50]}...")
                else:
                    skipped_count += 1
                    print(f"[CSV] Skipped duplicate: {pos_prompt[:50]}...")
        
        return {
            'success': True,
            'saved': saved_count,
            'skipped': skipped_count,
            'message': f'Saved {saved_count} entries, skipped {skipped_count} duplicates'
        }
        
    except Exception as e:
        print(f"[CSV] Error saving multiple entries: {e}")
        return {
            'success': False,
            'message': str(e)
        }

def already_exists(file_path : str , pos_prompt : str , neg_prompt : str) :
        
        try:
            with open(file_path , 'r' , encoding="utf8") as csv_file:

                reader = csv.reader(csv_file , delimiter=DELIMITER)

                for row in reader : 
                    if len(row) > 0 and row[0] == pos_prompt and row[1] == neg_prompt :
                        print("the prompt already exists in the file") 
                        return True
                
                csv_file.close()

                return False
        except FileNotFoundError:
            return False

def get_prompt_list(file_path : str) : 
    
    row_list = []
    
    with open(file_path , 'r' , encoding="utf8") as csv_file:

        reader = csv.reader(csv_file , delimiter=DELIMITER)
        i = 0
        for row in reader : 
           row_list.append(
                {   "id" : i , 
                    "positive" : row[0] if len(row) > 0 and len(row[0]) > 0 else "(EMPTY)" , 
                    "negative" : row[1] if len(row) > 1 and len(row[1]) > 0 else "(EMPTY)",
                    "image_path" : row[2] if len(row) > 2 and len(row[2]) > 0 else ""
                }
           )

           i += 1
        
        csv_file.close()

        return row_list

def show_prompt_list(prompt_list) : 
    for prompt in prompt_list : 
        print("pos: {}\t neg: {}".format(prompt['positive'] , prompt['negative']))

def get_prompt_row(file_path : str , index : int) -> dict[str , str] :

    with open(file_path , "r" , encoding="utf8") as csv_file : 
        
        reader = csv.reader(csv_file , delimiter=DELIMITER)
        
        i = 0
        
        for row in reader : 
            if i == index : 
                return {   
                        "positive" : row[0] if len(row) > 0 and len(row[0]) > 0 else "" , 
                        "negative" : row[1] if len(row) > 1 and len(row[1]) > 0 else "",
                        "image_path" : row[2] if len(row) > 2 and len(row[2]) > 0 else ""
                    }
                
            i+= 1
        return {
            "positive" : "" , 
            "negative" : "",
            "image_path" : ""
        }


# Endpoint personalizado para servir imágenes con soporte de subdirectorios
@server.PromptServer.instance.routes.get("/csv_image_view")
async def csv_image_view(request):
    """
    Endpoint personalizado para el CSV node que soporta subdirectorios.
    Busca imágenes en orden de prioridad:
    1. preview/filename
    2. filename (root)
    3. Búsqueda recursiva en subdirectorios
    """
    filename = request.query.get("filename", "")
    
    if not filename:
        raise web.HTTPNotFound(text="No filename provided")
    
    output_dir = folder_paths.output_directory
    
    # Normalize path separators
    filename = filename.replace("\\", "/")
    
    # Lista de rutas donde buscar (en orden de prioridad)
    search_paths = []
    
    # 1. Si ya incluye subdirectorio, usar tal como está
    if "/" in filename:
        search_paths.append(os.path.join(output_dir, filename))
    else:
        # 2. Si es solo nombre, buscar primero en preview/, luego en root
        search_paths.extend([
            os.path.join(output_dir, "preview", filename),
            os.path.join(output_dir, filename)
        ])
    
    # Buscar la imagen en las rutas definidas
    for path in search_paths:
        if os.path.exists(path) and os.path.isfile(path):
            print(f"[CSV] Serving image: {path}")
            return web.FileResponse(path)
    
    # 3. Si no se encontró, hacer búsqueda recursiva como último recurso
    for root, dirs, files in os.walk(output_dir):
        if os.path.basename(filename) in files:
            full_path = os.path.join(root, os.path.basename(filename))
            print(f"[CSV] Found image recursively: {full_path}")
            return web.FileResponse(full_path)
    
    print(f"[CSV] Image not found: {filename}")
    raise web.HTTPNotFound(text=f"Image not found: {filename}")

# Endpoint para guardar entradas múltiples desde History Scanner
@server.PromptServer.instance.routes.post("/csv_utils/save_to_csv")
async def save_to_csv_endpoint(request):
    """
    Endpoint para guardar múltiples entradas en CSV desde el History Scanner
    Ahora con funcionalidad de mover imágenes a preview folder
    """
    try:
        data = await request.json()
        entries = data.get('entries', [])
        
        if not entries:
            return web.json_response({
                'success': False,
                'message': 'No entries provided'
            })
        
        # Usar la nueva función que mueve imágenes y hardcodea la ubicación
        result = save_multiple_to_csv_with_move(entries)
        
        return web.json_response(result)
        
    except Exception as e:
        print(f"[CSV] Error in save_to_csv_endpoint: {e}")
        return web.json_response({
            'success': False,
            'message': str(e)
        })
     