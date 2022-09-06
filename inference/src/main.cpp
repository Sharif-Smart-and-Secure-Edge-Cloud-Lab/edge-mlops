#include <iostream>
#include <exception>
#include "Model.hpp"

int main(){
	std::cout << "## IMDB review classifier ##" << std::endl;
	std::cout << "Initializing model...\n";
    Model m{"/home/nima/Documents/l/edge-mlops/inference/word_indexes.json",
            "/home/nima/Documents/l/edge-mlops/convert_model/output.onnx"};
	std::string input_text;
	while(1){
		std::cout << "Enter text (type exit() to exit): ";
		std::getline(std::cin, input_text);
		if(input_text == "exit()"){
			break;	
		}
		else{
			try{
				std::cout << "Result: " << m.inference(input_text) 
						  << "\n===============================\n";
			} catch (const std::exception& e) {
				std::cout << "Unable to handle input, " << e.what() 
						  << "\n===============================\n";
			}
		}
	}
	std::cout << "Farewell...\n";
}

