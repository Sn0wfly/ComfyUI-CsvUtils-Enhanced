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
        
        print(f"[CSV DEBUG] Processing {len(entries)} entries")
        print(f"[CSV DEBUG] Output dir: {output_dir}")
        print(f"[CSV DEBUG] Preview dir: {preview_dir}")
        print(f"[CSV DEBUG] CSV file: {csv_file_path}")
        
        with open(csv_file_path, 'a', newline='', encoding="utf8") as csv_file:
            writer_object = csv.writer(csv_file, delimiter=DELIMITER)
            
            for i, entry in enumerate(entries):
                print(f"\n[CSV DEBUG] --- Processing entry {i+1}/{len(entries)} ---")
                pos_prompt = entry.get('positive_prompt', '').strip()
                neg_prompt = entry.get('negative_prompt', '').strip()
                original_image_path = entry.get('image_path', '').strip()
                
                print(f"[CSV DEBUG] Entry data:")
                print(f"[CSV DEBUG]   - positive: {pos_prompt[:50]}...")
                print(f"[CSV DEBUG]   - negative: {neg_prompt[:50]}...")
                print(f"[CSV DEBUG]   - image_path: {original_image_path}")
                
                if not original_image_path:
                    print(f"[CSV DEBUG] Skipping - no image path")
                    continue
                
                # Si image_path contiene múltiples archivos separados por ';', procesarlos uno por uno
                image_paths = original_image_path.split(';')
                print(f"[CSV DEBUG] Split paths: {image_paths}")
                
                # Usar la primera imagen para el CSV (las demás se mueven pero no se registran)
                first_image_path = image_paths[0].strip()
                
                # Construir rutas completas
                source_path = os.path.join(output_dir, first_image_path)
                filename = os.path.basename(first_image_path)
                dest_path = os.path.join(preview_dir, filename)
                preview_relative_path = f"preview/{filename}"
                
                print(f"[CSV DEBUG] Path calculations:")
                print(f"[CSV DEBUG]   - source_path: {source_path}")
                print(f"[CSV DEBUG]   - dest_path: {dest_path}")
                print(f"[CSV DEBUG]   - filename: {filename}")
                print(f"[CSV DEBUG]   - preview_relative_path: {preview_relative_path}")
                print(f"[CSV DEBUG]   - source exists: {os.path.exists(source_path)}")
                print(f"[CSV DEBUG]   - source == dest: {source_path == dest_path}")
                
                # Verificar si ya existe el prompt (con la nueva ruta)
                prompt_exists = already_exists(csv_file_path, pos_prompt, neg_prompt)
                print(f"[CSV DEBUG] Prompt already exists: {prompt_exists}")
                
                if not prompt_exists:
                    try:
                        # Procesar todas las imágenes de este prompt group
                        images_moved_for_group = 0
                        moved_image_paths = []  # Lista para acumular todas las rutas movidas
                        
                        for img_path in image_paths:
                            img_path = img_path.strip()
                            if not img_path:
                                continue
                                
                            img_source_path = os.path.join(output_dir, img_path)
                            img_filename = os.path.basename(img_path)
                            img_dest_path = os.path.join(preview_dir, img_filename)
                            
                            print(f"[CSV DEBUG] Moving image: {img_path}")
                            print(f"[CSV DEBUG]   - img_source_path: {img_source_path}")
                            print(f"[CSV DEBUG]   - img_dest_path: {img_dest_path}")
                            print(f"[CSV DEBUG]   - source exists: {os.path.exists(img_source_path)}")
                            
                            # Mover imagen a preview folder (solo si no está ya ahí)
                            if os.path.exists(img_source_path) and img_source_path != img_dest_path:
                                final_dest_filename = img_filename
                                if os.path.exists(img_dest_path):
                                    # Si ya existe en destino, generar nombre único con timestamp
                                    import time
                                    base_name, ext = os.path.splitext(img_filename)
                                    timestamp = int(time.time() * 1000)  # timestamp en milliseconds para unicidad
                                    final_dest_filename = f"{base_name}_{timestamp}{ext}"
                                    img_dest_path = os.path.join(preview_dir, final_dest_filename)
                                    print(f"[CSV DEBUG] Destination existed, using timestamp name: {final_dest_filename}")
                                
                                print(f"[CSV DEBUG] Attempting to move: {img_source_path} -> {img_dest_path}")
                                
                                # Intentar el movimiento
                                import shutil
                                shutil.move(img_source_path, img_dest_path)
                                images_moved_for_group += 1
                                
                                # Agregar la ruta final a la lista
                                moved_image_paths.append(f"preview/{final_dest_filename}")
                                print(f"[CSV DEBUG] ✅ Successfully moved: {img_path} -> {final_dest_filename}")
                                
                            else:
                                if not os.path.exists(img_source_path):
                                    print(f"[CSV DEBUG] ❌ Source file doesn't exist: {img_source_path}")
                                else:
                                    print(f"[CSV DEBUG] ⏭️ Source == destination, skipping: {img_path}")
                                    # Si ya está en preview, agregarlo a la lista de todos modos
                                    moved_image_paths.append(f"preview/{img_filename}")
                        
                        moved_count += images_moved_for_group
                        print(f"[CSV DEBUG] Moved {images_moved_for_group} images for this prompt group")
                        
                        # Crear la ruta final para el CSV con TODAS las imágenes
                        if moved_image_paths:
                            final_csv_path = ";".join(moved_image_paths)
                        else:
                            # Fallback si no se movió nada
                            final_csv_path = preview_relative_path
                        
                        print(f"[CSV DEBUG] Final CSV path: {final_csv_path}")
                        
                        # Guardar en CSV con TODAS las rutas en preview
                        writer_object.writerow([pos_prompt, neg_prompt, final_csv_path])
                        saved_count += 1
                        print(f"[CSV DEBUG] ✅ Saved to CSV: {pos_prompt[:50]}...")
                        
                    except Exception as e:
                        print(f"[CSV DEBUG] ❌ Error moving images for entry {i+1}: {e}")
                        import traceback
                        print(f"[CSV DEBUG] Traceback: {traceback.format_exc()}")
                        # Si falla el movimiento, guardar con ruta original
                        writer_object.writerow([pos_prompt, neg_prompt, first_image_path])
                        saved_count += 1
                else:
                    skipped_count += 1
                    print(f"[CSV DEBUG] ⏭️ Skipped duplicate: {pos_prompt[:50]}...")
        
        print(f"\n[CSV DEBUG] === FINAL SUMMARY ===")
        print(f"[CSV DEBUG] Saved: {saved_count}")
        print(f"[CSV DEBUG] Skipped: {skipped_count}") 
        print(f"[CSV DEBUG] Moved: {moved_count}")
        
        return {
            'success': True,
            'saved': saved_count,
            'skipped': skipped_count,
            'moved': moved_count,
            'csv_path': csv_file_path,
            'message': f'Saved {saved_count} prompts, moved {moved_count} images to preview folder. Skipped {skipped_count} duplicates.'
        }
        
    except Exception as e:
        print(f"[CSV DEBUG] ❌ Fatal error in save_multiple_to_csv_with_move: {e}")
        import traceback
        print(f"[CSV DEBUG] Traceback: {traceback.format_exc()}")
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
     