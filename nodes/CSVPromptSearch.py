
class CSVPromptSearch : 
    @classmethod
    def INPUT_TYPES(s) : 

        return {
            "required" : {
                "file_path" : ("STRING", {"default": "output/prompt_history.csv"}), 
            }
        }
    
    CATEGORY = "csv_tools"
    
    #FUNCTION = "execute"
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    
    OUTPUT_NODE = False
    

    def execute(self , file_path) : 
        return {}

