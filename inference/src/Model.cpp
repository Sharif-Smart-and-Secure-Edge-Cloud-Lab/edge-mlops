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
}


std::array<int, MAX_WORDS> Model::convertToIndexes(std::string review){
    std::array<int, MAX_WORDS> vec_input{0};
    std::istringstream iss(review);
    std::string word{};
    int index = 0;
    while(1){
        iss >> word;
        if(iss){
            index = word_indexes[word];
            if(index < MAX_WORDS)
                vec_input[index] = 1;
        } else {
            break;
        }
    }
    return vec_input;
}
