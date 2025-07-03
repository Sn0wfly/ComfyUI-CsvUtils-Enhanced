from .csv_prompt import CSVPromptSave
import subprocess

process = subprocess.Popen("python py/prompt_save.py")

print("[CSV utils] csv server init")

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = { "CSVPromptSave" : CSVPromptSave }

__all__ = ["NODE_CLASS_MAPPINGS" , "NODE_DISPLAY_NAME_MAPPINGS" , "WEB_DIRECTORY"]

