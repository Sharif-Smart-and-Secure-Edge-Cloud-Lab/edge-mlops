#include "train.h"
#include <vector>
#include "constants.h"

float train_step(
    std::shared_ptr<SessionCache> session_cache, float* batches, int64_t* labels,
    int64_t batch_size)
{
    const std::vector<int64_t> input_shape({batch_size, 1, img_width, img_height});
    const std::vector<int64_t> labels_shape({batch_size});

    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    std::vector<Ort::Value> user_inputs;

    user_inputs.emplace_back(
        Ort::Value::CreateTensor(memory_info, batches,
                                 batch_size * img_width * img_height * sizeof(float),
                                 input_shape.data(), input_shape.size(),
                                 ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT));
    user_inputs.emplace_back(
        Ort::Value::CreateTensor(memory_info, labels,
                                 batch_size * sizeof(int64_t),
                                 labels_shape.data(), labels_shape.size(),
                                 ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64));

    float loss = *(session_cache->training_session.TrainStep(user_inputs).front().GetTensorMutableData<float>());

    session_cache->training_session.OptimizerStep();

    session_cache->training_session.LazyResetGrad();

    return loss;
}