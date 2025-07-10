from .nodes.CSVPromptSaver import CSVPromptSaver
from .nodes.CSVPromptSearch import CSVPromptSearch
from .nodes.CSVHistoryScanner import CSVHistoryScanner

# Importación condicional de Cloud Sync
try:
    from .nodes.CSVCloudSync import CSVCloudSync
    CLOUD_SYNC_AVAILABLE = True
    print("[CSV Utils] Cloud Sync functionality available")
except ImportError as e:
    print(f"[CSV Utils] Cloud Sync not available: {e}")
    print("[CSV Utils] To enable: pip install -r requirements-cloud.txt")
    CLOUD_SYNC_AVAILABLE = False

from .py.csv_utils import *

from server import PromptServer

from aiohttp import web



@PromptServer.instance.routes.post("/csv_utils/save_prompt")
async def save_prompt(request) : 

    json_data : dict[str , str]= await request.json()

    #print("[csv utils server] data to save : " , json_data)
    
    if "positive_prompt" in json_data and "negative_prompt" in json_data and "file_path" in json_data :

        for key, val in json_data.items() : 
            if key != "image_path" and len(val) == 0 :
                return web.json_response({"status" : False , "message" : "empty inputs are not allowed"})

        image_path = json_data.get("image_path", "")
        
        if not save_to_csv(json_data["file_path"].strip() , json_data["positive_prompt"].strip() , json_data["negative_prompt"].strip(), image_path.strip()): 
            return web.json_response({"status" : False , "message" : "the prompt already exists in the csv file"})

        return web.json_response({"status" : True , "message" : "prompt saved ! "})


@PromptServer.instance.routes.post("/csv_utils/get_prompts")
async def get_prompts_list(request) :
    json_data : dict[str : str] = await request.json()
    print(json_data)
    if "file_path" in json_data : 
        
        prompt_list = get_prompt_list(json_data["file_path"])
        
        if len(prompt_list) == 0 : 
            return web.Response(text="The file is empty" , status=404)
        
        #show_prompt_list(prompt_list)

        return web.json_response({"prompt_list" : prompt_list})
    

print("[CSV utils] csv server routes init")

WEB_DIRECTORY = "./web"

# Nodos básicos (siempre disponibles)
NODE_CLASS_MAPPINGS = { 
    # Nombres nuevos (recomendados)
    "CSVPromptSaver": CSVPromptSaver,
    "CSVPromptSearch": CSVPromptSearch,
    "CSVHistoryScanner": CSVHistoryScanner,
    
    # Compatibilidad hacia atrás (nombres viejos)
    "CSVPromptSave": CSVPromptSaver,  # Mapear nombre viejo al nuevo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Nombres nuevos
    "CSVPromptSaver": "CSV Prompt Saver",
    "CSVPromptSearch": "CSV Prompt Search", 
    "CSVHistoryScanner": "CSV History Scanner",
    
    # Compatibilidad hacia atrás
    "CSVPromptSave": "CSV Prompt Saver (Legacy)",
}

# Agregar Cloud Sync si está disponible
if CLOUD_SYNC_AVAILABLE:
    NODE_CLASS_MAPPINGS.update({
        "CSVCloudSync": CSVCloudSync,
    })
    
    NODE_DISPLAY_NAME_MAPPINGS.update({
        "CSVCloudSync": "CSV Cloud Sync",
    })

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

