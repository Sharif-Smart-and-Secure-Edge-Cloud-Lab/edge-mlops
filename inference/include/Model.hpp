#ifndef _AI_MODEL_HPP_
#define _AI_MODEL_HPP_

#include <string>
#include <fstream>
#include <array>
#include <memory>
#include <onnxruntime_cxx_api.h>
#include "json.hpp"

#define MAX_WORDS 1000
#define NUM_CPU_THREADS 1

namespace nl = nlohmann;

// Header-only library that runs model
class Model{
private:
    nl::json word_indexes;
    std::shared_ptr<Ort::Env> env;
    std::shared_ptr<Ort::Session> session;
public:
    std::array<int, MAX_WORDS> convertToIndexes(std::string review);
    Model(std::string word_indexes_file_path,
          std::string model_path);
    // int inference(std::string review);
};

#endif //_AI_MODEL_HPP_
