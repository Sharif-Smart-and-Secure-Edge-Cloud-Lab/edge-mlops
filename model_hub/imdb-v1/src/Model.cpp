#include <sstream>
#include <string>
#include "Model.hpp"
#include <iostream>

Model::Model(std::string word_indexes_file_path, std::string model_path){
    std::ifstream word_indexes_file{word_indexes_file_path};
    word_indexes_file >> word_indexes;
    env = std::make_shared<Ort::Env>(ORT_LOGGING_LEVEL_ERROR, "InferenceEnv");
    // session options configurations
    Ort::SessionOptions sess_opts;
    sess_opts.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
    sess_opts.SetInterOpNumThreads(NUM_CPU_THREADS);

    session = std::make_shared<Ort::Session>(*env, model_path.c_str(), sess_opts);

    // get input and output names (used later in running model)
    Ort::AllocatorWithDefaultOptions allocator;
    for(size_t i = 0; i < session->GetInputCount(); i++){
        auto current_input_name = session->GetInputNameAllocated(i, allocator);
        input_names.push_back(current_input_name.get());
    }
    for(size_t i = 0; i < session->GetOutputCount(); i++){
        auto current_output_name = session->GetOutputNameAllocated(i, allocator);
        output_names.push_back(current_output_name.get());
    }
    input_shapes = std::vector<int64_t>{BATCH_SIZE, MAX_WORDS};
    input_tensor_size = BATCH_SIZE * MAX_WORDS;

	//std::cout << "this: " << word_indexes["this"] << std::endl;
}


std::array<float, MAX_WORDS> Model::convertToIndexes(std::string review){
    std::array<float, MAX_WORDS> vec_input{0.0};
    std::istringstream iss(review);
    std::string word{};
    int index = 0;
    while(1){
        iss >> word;
        if(iss){
            index = word_indexes[word];
            if(index < MAX_WORDS)
                vec_input[index] = 1.0;
        } else {
            break;
        }
    }
    return vec_input;
}

std::string Model::inference(std::string review){
    std::array<float, MAX_WORDS> vec_input = convertToIndexes(review);
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(memory_info, vec_input.data(),
                                                               input_tensor_size, input_shapes.data(),
                                                               input_shapes.size());
    assert(input_tensor.IsTensor());
    std::cout << "Yeah, it's a tensor!\n";
    std::vector<Ort::Value> output_tensor = session->Run(Ort::RunOptions{nullptr},
                                                         input_names.data(),
                                                         &input_tensor,
                                                         1,
                                                         output_names.data(),
                                                         output_names.size());
    std::cout << "Finished execution\n";
    // extract data from Ort tensor
    float* raw_output = output_tensor[0].GetTensorMutableData<float>();
    std::cout << raw_output[0] << std::endl;
    size_t output_size = output_tensor[0].GetTensorTypeAndShapeInfo().GetElementCount();
    std::vector<float> output_values(raw_output, raw_output+output_size);
	if(output_values[0] > 0.5)
		return std::string{"positive +"};
	else
		return std::string{"negative -"};
}
