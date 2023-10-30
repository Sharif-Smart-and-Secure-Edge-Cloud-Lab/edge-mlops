#include "inference.h"
#include "constants.h"
#include <iostream>

std::vector<float> classify(
    std::shared_ptr<SessionCache> session_cache,
    float* img_data, int64_t batch_size)
{
    std::vector<const char*> input_names{"input"};
    constexpr size_t input_count{1};
    std::vector<const char*> output_names{"output"};
    constexpr size_t output_count{1};

    std::vector<int64_t> input_shape({batch_size, img_size});
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    std::vector<Ort::Value> input_values;
    input_values.emplace_back(
        Ort::Value::CreateTensor(memory_info, img_data,
                                 batch_size * img_size * sizeof(float),
                                 input_shape.data(), input_shape.size(),
                                 ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT));
    std::vector<Ort::Value> output_values;
    output_values.emplace_back(nullptr);
    std::cout << "\tRunning the model...\n";
    session_cache->inference_session->Run(Ort::RunOptions(), input_names.data(), input_values.data(),
                                          input_count, output_names.data(), output_values.data(), output_count);
    std::cout << "\tExecuted successfully!\n";
    float* output = output_values.front().GetTensorMutableData<float>();
    std::vector<float> output_vec(output, output+batch_size*10);
    return output_vec;
}
