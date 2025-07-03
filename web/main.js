import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";


app.registerExtension({ 
	name: "CSVUtils",
	
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if(nodeType.comfyClass=="CSVPromptSave") {			
		}
	} ,

	async setup() { 
		console.log("[CSV tools] extension setup complete")
	},

	async nodeCreated(node) {
	
		if(node.comfyClass == "CSVPromptSave") 
		{	
			console.log("csv prompt save node : ", node.type)
			
			node.addWidget("button" , "click" , 0 , async ()=>{

				console.log("prompt save request")

				let prompt_label = node.widgets[1].value
				let file_path_label = node.widgets[0].value

				try {

					const response = await api.fetchApi("/csv_utils/save_prompt" , {
						method : "POST" , 
						body : JSON.stringify({
							prompt : prompt_label ,
							file_path : file_path_label
						})
					})
					
					if(response.status != 200) {
						throw new Error("error while saving prompt")
					}

					const data = await response.json()
					console.log(data)
				}
				catch(error) {
					alert(error)
				}

				console.log("prompt : " , prompt_label , "\nfile path : " , file_path_label)
			})
		}
	} , 
	
	async init() {
	}
})