class CSVPromptSave : 
    @classmethod
    def INPUT_TYPES(s) : 

        return {
            "required" : {
                "file_path" : ("STRING",) , 
                "positive_prompt" : ("STRING",{"default" : "" , "multiline" : True}) ,
                "negative_prompt" : ("STRING",{"default" : "" , "multiline" : True}),
                "image_path" : ("STRING",{"default" : ""}) 
            }
        }
    
    CATEGORY = "csv_tools"
    
    FUNCTION = "execute"
    
    RETURN_TYPES = ("STRING" , "STRING", "STRING")
    
    RETURN_NAMES = ("positive prompt" , "negative prompt", "image path")
    
    OUTPUT_NODE = False
    

    def execute(self , file_path , positive_prompt , negative_prompt, image_path) : 
    
        return (positive_prompt , negative_prompt, image_path)

