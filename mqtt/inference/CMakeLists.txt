cmake_minimum_required(VERSION 3.10)

project("edge-mlops")

enable_language(CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-psabi")
set(ORT_LIB_DIR "/ORT/onnxruntime/build/Linux/Release")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
set(ONNXRUNTIME_INCLUDE_DIR "/ORT/onnxruntime/include/onnxruntime/core/session")
include_directories("${ONNXRUNTIME_INCLUDE_DIR}")

link_directories("${ORT_LIB_DIR}"
                 "${ORT_LIB_DIR}/external/onnx"
                 "${ORT_LIB_DIR}/external/protobuf/cmake"
                 "${ORT_LIB_DIR}/external/re2"
                 "${ORT_LIB_DIR}/external/abseil-cpp/absl/base"
                 "${ORT_LIB_DIR}/external/abseil-cpp/absl/container"
                 "${ORT_LIB_DIR}/external/abseil-cpp/absl/hash"
                 "${ORT_LIB_DIR}/external/nsync/"
                 "${ORT_LIB_DIR}/external/pytorch_cpuinfo/deps/clog"
                 "${ORT_LIB_DIR}/external/pytorch_cpuinfo/")

add_executable(${PROJECT_NAME} src/main.cpp src/Model.cpp)
target_link_libraries(${PROJECT_NAME} -static 
                                      onnxruntime_session
                                      onnxruntime_optimizer
                                      onnxruntime_providers
                                      onnxruntime_util
                                      onnxruntime_framework
                                      onnxruntime_graph
                                      onnxruntime_mlas
                                      onnxruntime_common
                                      onnxruntime_flatbuffers
                                      onnx_test_data_proto
                                      onnx
                                      onnx_proto
                                      protobuf-lite
                                      re2
                                      absl_base
                                      absl_throw_delegate
                                      absl_raw_hash_set
                                      absl_hash
                                      absl_city
                                      absl_low_level_hash
                                      nsync_cpp 
                                      cpuinfo 
                                      clog)

install(TARGETS ${PROJECT_NAME} DESTINATION bin)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/word_indexes.json DESTINATION bin)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../convert_model/output.onnx DESTINATION bin)
