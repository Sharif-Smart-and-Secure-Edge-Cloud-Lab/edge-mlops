cmake_minimum_required(VERSION 3.10)

project("edge-mlops")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
# ONNX Runtime include and library paths
include_directories("/home/nima/local-libs/onnxGPU/include")
link_directories("/home/nima/local-libs/onnxGPU/lib")

add_executable(${PROJECT_NAME} src/main.cpp src/Model.cpp)
target_link_libraries(${PROJECT_NAME} onnxruntime)