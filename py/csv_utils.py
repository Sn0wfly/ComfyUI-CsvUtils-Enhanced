import csv


DELIMITER = ","

def save_to_csv(file_path : str , pos_prompt :str , neg_prompt :str) : 
        
        if already_exists(file_path , pos_prompt , neg_prompt) : 
            return False
                
        with open(file_path , 'a' , newline='' , encoding="utf8") as csv_file:

            writer_object = csv.writer(csv_file , delimiter=DELIMITER)

            print("prompt put in the row :" , pos_prompt)
            writer_object.writerow([pos_prompt , neg_prompt])

            csv_file.close()

        return True

def already_exists(file_path : str , pos_prompt : str , neg_prompt : str) :
        
        with open(file_path , 'r' , encoding="utf8") as csv_file:

            reader = csv.reader(csv_file , delimiter=DELIMITER)

            for row in reader : 
                if len(row) > 0 and row[0] == pos_prompt and row[1] == neg_prompt :
                    print("the prompt already exists in the file") 
                    return True
            
            csv_file.close()

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
                    "negative" : row[1] if len(row) > 1 and len(row[1]) > 0 else "(EMPTY)"
                }
           )

           i += 1
        
        csv_file.close()

        return row_list

def show_prompt_list(prompt_list) : 
    for prompt in prompt_list : 
        print(f"pos: {prompt["positive"]}\t neg: {prompt["negative"]}")

def get_prompt_row(file_path : str , index : int) -> dict[str , str] :

    with open(file_path , "r" , encoding="utf8") as csv_file : 
        
        reader = csv.reader(csv_file , delimiter=DELIMITER)
        
        i = 0
        
        for row in reader : 
            if i == index : 
                return {   
                        "positive" : row[0] if len(row) > 0 and len(row[0]) > 0 else "" , 
                        "negative" : row[1] if len(row) > 1 and len(row[1]) > 0 else ""
                    }
                
            i+= 1
        return {
            "positive" : "" , 
            "negative" : ""
        }
     