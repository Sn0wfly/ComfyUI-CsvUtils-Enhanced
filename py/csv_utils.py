import csv
import os
from aiohttp import web
import server
import folder_paths


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
     