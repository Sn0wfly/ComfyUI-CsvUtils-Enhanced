from .nodes.CSVPromptSaver import CSVPromptSave
from .nodes.CSVPromptSearch import CSVPromptSearch

from .py.csv_utils import *

from server import PromptServer

from aiohttp import web

from aiohttp import web



@PromptServer.instance.routes.post("/csv_utils/save_prompt")
async def save_prompt(request) : 

    json_data : dict[str , str]= await request.json()

    
    #print("[csv utils server] data to save : " , json_data)
    
    if "positive_prompt" in json_data and "negative_prompt" in json_data and "file_path" in json_data :

        for _ ,val in json_data.items() : 
            if len(val) == 0 :
                return web.json_response({"status" : False , "message" : "empty inputs are not allowed"})

        if not save_to_csv(json_data["file_path"] , json_data["positive_prompt"] , json_data["negative_prompt"]) : 
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
        
        show_prompt_list(prompt_list)

        return web.json_response({"prompt_list" : prompt_list})
    

print("[CSV utils] csv server routes init")

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = { 
    "CSVPromptSave" : CSVPromptSave ,
    "CSVPromptSearch" : CSVPromptSearch                        
}

__all__ = ["NODE_CLASS_MAPPINGS" , "WEB_DIRECTORY"]

