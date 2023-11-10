#include <iostream>
#include <memory>
#include <string>
#include "Eigen/Dense"

#include "session_cache.h"
#include "train.h"
#include "inference.h"
#include "constants.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image_resize2.h"

typedef unsigned char pixel;
template<typename T>
using Matrix_R = Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

Eigen::Matrix<float, img_width, img_height>
    read_mnist_like_img(const std::string& img_name)
{
    int width, height, channels;
    pixel* raw_img = stbi_load(img_name.c_str(), &width, &height, &channels, 1);
    if(raw_img == nullptr){
        exit(-1);
    }
    pixel* res_img = new pixel[img_width*img_height];
    stbir_resize_uint8_srgb(raw_img, width, height, 0,
                            res_img, img_width, img_height, 0,
                            STBIR_1CHANNEL);

    Eigen::Map<Matrix_R<pixel>> img_temp(res_img, img_width, img_height);
    Matrix_R<float> img = 1.0f - img_temp.cast<float>().array() / 255.0f;

    delete[] res_img;
    stbi_image_free(raw_img);
    return img;
}

int main(){
    std::shared_ptr<SessionCache> session_cache = std::make_shared<SessionCache>(
        "../model/checkpoint",
        "../model/training_model.onnx",
        "../model/eval_model.onnx",
        "../model/optimizer_model.onnx",
        "../model/inference.onnx");

    Eigen::Matrix<float, img_width, img_height> img;
    std::string mode;
    bool is_correct;
    int64_t true_label;

    read_mnist_like_img("img.jpg");

    while(true){
        std::cin >> mode;
        if(mode == "quit")
            break;
        img = read_mnist_like_img("img.jpg");
        auto num = classify(session_cache, img.data(), 1);
        std::cout << num << std::endl;
        std::cin >> is_correct;
        if(!is_correct){
            std::cin >> true_label;
            float loss = train_step(session_cache, img.data(), &true_label, 1);
            std::cout << loss << std::endl;

            session_cache->training_session.ExportModelForInferencing(
                session_cache->artifact_paths.inference_model_path.c_str(), {"output"});
            delete session_cache->inference_session;
            session_cache->inference_session =
                std::make_unique<Ort::Session>(
                    session_cache->ort_env,
                    session_cache->artifact_paths.inference_model_path.c_str(),
                    session_cache->session_options).release();
        }
    }

    return 0;
}
