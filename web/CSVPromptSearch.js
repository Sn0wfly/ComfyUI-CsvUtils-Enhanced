import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";









async function getPromptList(file_path) {
	
	//try {

		const response = await api.fetchApi("/csv_utils/get_prompts" , {
			method : "POST" , 
			headers : {"Content-Type" : "application/json"} , 
			body : JSON.stringify({
				file_path : file_path
			})
		})

		// if(response.status != 200) {
		// 	throw new Error("error while searching querying prompts")
		// }

		const data = await response.json()
		// console.log(data.prompt_list)
		return data.prompt_list
		
	//}
	// catch(err) {
	// 	app.extensionManager.toast.add({
	// 			severity : "error" , 
	// 			summary : "Internal Error" , 
	// 			detail : err , 
	// 			life : 5000
	// 		})
	// }


}

function create_prompt_div(pos , neg) 
{
	return ` 
		<div class="csv-u-prompt-container">
			<span class="csv-u-prompt-span csv-u-pos-span"> 
				${pos}\t
			</span>

			<span class="csv-u-prompt-span csv-u-neg-span">
				${neg}
			</span>
		</div>
	`
}

function filter_data(prompt_list , search) {
	return prompt_list.filter((prompt)=> prompt.positive.includes(search) || prompt.negative.includes(search))
}



function createResultWidget() {
	
	let result_container = document.createElement("div")
		result_container.style.overflow = "clip"
		result_container.style.display = "flex"
		result_container.style.flexDirection = "column"

		// result_container.style.height = "100%"
		let header = document.createElement("h1")
			result_container.appendChild(header)
			header.innerText = "Search List" 
			
		let search_bar = document.createElement("input")
			search_bar.type = "text"
			search_bar.className = "csv-u-search-bar"
			result_container.appendChild(search_bar)
		
		let result_list = document.createElement("div")
			result_list.style.overflow = "scroll"
			result_list.style.height = "100%"
			result_container.appendChild(result_list)

		let prompt_list = document.createElement("div")
			result_list.appendChild(prompt_list)
			prompt_list.className = "csv-u-prompt-list"
		


	return {result_container : result_container,  result_list : result_list , search_bar : search_bar}
}



//----------------------------------------------------------------------------------------------



app.registerExtension({ 
	name: "CSV-UTILS-SEARCH",
	
	async loadedGraphNode() {
		let style = document.createElement("style") 
		
		style.innerHTML = `
				h1 {
					text-align : center;
				}
				.csv-u-search-bar {
					background-color : white;
					color : black;
				}
				.csv-u-prompt-span {
					outline : solid;
					outline-width : 2px;
					padding : 4px;
					cursor : pointer;
					flex-grow : 0.5;
					width : 50%;
					font-size : 12px;
				}
				.csv-u-prompt-span:hover {
					cursor : cell
				}

				.csv-u-pos-span {
					color : rgb(118, 199, 60);
				}

				.csv-u-neg-span {
					color : rgb(199, 52, 57);
				}

				.csv-u-prompt-container {
					display : flex;
					background-color : rgb(255, 255, 255);
					padding : 6px;
					margin-top : 6px;
					margin-bottom : 6px;
					gap : 6px;
				}

				.csv-u-search-bar {
					width : 100%;
				}
		`

		document.body.appendChild(style)
	},

	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		
		
	} ,

	async setup() { 
		console.log("[CSV tools] extension setup complete")
	},

	async nodeCreated(node) {
	
		if(node.comfyClass == "CSVPromptSearch") 
		{	
			console.log(node.widgets)
			
			let widgets = createResultWidget()
			
			node.addDOMWidget("list-results" , "list" , widgets.result_container)

			let search_bar = widgets.search_bar

			console.log(widgets.result_container)
			
			search_bar.addEventListener("input" , async (e)=> {
				
				const prompt_list = await getPromptList(node.widgets[0].value)
				
				const filtered_list = filter_data(prompt_list , search_bar.value)
				
				widgets.result_list.innerHTML = ""

				for( let i = 0 ; i < filtered_list.length ; i++) {
					let div = document.createElement("div")
					
					div.innerHTML = create_prompt_div(filtered_list[i].positive , filtered_list[i].negative)
					
					widgets.result_list.appendChild(div)
				}

				const span_list = Array.from(document.getElementsByClassName("csv-u-prompt-span"))
				
				span_list.forEach(element => {
					element.addEventListener("click" , (e)=> {
							navigator.clipboard.writeText(e.target.innerText)
							app.extensionManager.toast.add({
							severity : "success" , 
							summary : "prompt search" , 
							detail : "Prompt copied !" , 
							life : 2000
						})
					}) 	
				});

				}
			)
			
			
		}
	} , 
	
	async init() {
		


	} ,

	async setup()
	{
		
	} 
	
	
})