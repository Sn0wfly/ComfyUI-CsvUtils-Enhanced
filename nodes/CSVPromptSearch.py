
class CSVPromptSearch : 
    @classmethod
    def INPUT_TYPES(s) : 

        return {
            "required" : {
                "file_path" : ("STRING",) , 
                "search" : ("STRING",{"default" : ""}) , 
            }
        }
    
    CATEGORY = "csv_tools"
    
    #FUNCTION = "execute"
    RETURN_TYPES = ()
    #RETURN_NAMES = ()
    
    OUTPUT_NODE = False
    

    def execute(self , file_path , search) : 
        return {}

