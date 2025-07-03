import csv

class CSVPromptSave : 
    @classmethod
    def INPUT_TYPES(s) : 

        return {
            "required" : {
                "file_path" : ("STRING",) , 
                "prompt" : ("STRING",{"default" : ""})
            }
        }
    
    def already_exists(file_path , prompt) :
        with open(file_path , 'r') as csv_file:

            reader = csv.reader(csv_file)

            for row in reader : 
                if row[0] == prompt :
                    print("the prompt already exists in the file") 
                    return True
            csv_file.close()
            return False
    

    CATEGORY = "csv_tools"
    FUNCTION = "save"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    

    def save(self , file_path , prompt) : 
        if CSVPromptSave.already_exists(file_path , prompt) : 
            return {}
        List = [prompt]

        with open(file_path , 'a' , newline='') as csv_file:

            writer_object = csv.writer(csv_file)

            writer_object.writerow(List)

            csv_file.close()

        return {}

