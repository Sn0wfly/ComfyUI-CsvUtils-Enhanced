from server import PromptServer
from aiohttp import web
import os
import folder_paths

print("[CSV utils] Route loaded")
@PromptServer.instance.routes.post("/csv_utils/save_prompt")
async def save_prompt(request) : 
    print("[csv utils] save prompt request" , request)
    pass