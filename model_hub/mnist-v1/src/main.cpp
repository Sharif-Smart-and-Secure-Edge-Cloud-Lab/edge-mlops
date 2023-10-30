#include <iostream>
#include <memory>

#include "session_cache.h"
#include "train.h"
#include "inference.h"
#include "constants.h"

int main(){
    std::cout << "Initializing session...\n";
    std::shared_ptr<SessionCache> session_cache = std::make_shared<SessionCache>(
        "../model/checkpoint",
        "../model/training_model.onnx",
        "../model/eval_model.onnx",
        "../model/optimizer_model.onnx",
        "../model/inference.onnx");

    constexpr int64_t batch_size{4};
    float* in_img = new float[batch_size * img_size];
    int64_t* labels = new int64_t[batch_size];

    for(int i = 0; i < batch_size*img_size; i++)
        in_img[i] = 0.1;

    labels[0] = 1;
    labels[1] = 1;
    labels[2] = 1;
    labels[3] = 1;

    std::cout << "Train the model...\n";
    float loss = train_step(session_cache, in_img, labels, batch_size);
    std::cout << "Training loss: " << loss << std::endl;

    // Use the trained model
    session_cache->training_session.ExportModelForInferencing(
        session_cache->artifact_paths.inference_model_path.c_str(), {"output"});
    session_cache->inference_session = std::make_unique<Ort::Session>(
        session_cache->ort_env, session_cache->artifact_paths.inference_model_path.c_str(),
        session_cache->session_options).release();

    std::cout << "Inference the model...\n";
    auto logits = classify(session_cache, in_img, batch_size);
    for(auto v : logits)
        std::cout << v << ", ";
    std::cout << std::endl;

    delete[] in_img;
    delete[] labels;

    return 0;
}
