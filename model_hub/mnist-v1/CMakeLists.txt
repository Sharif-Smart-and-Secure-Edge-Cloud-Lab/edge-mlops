cmake_minimum_required(VERSION 3.10)

project("mnist-v1")

enable_language(CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-psabi")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O2")

set(EIGEN_ROOT "/home/nima/lib-local/eigen-3.4.0/")
set(ORT_ROOT "/home/nima/lib-local/ort/onnxruntime/")
set(ORT_LIB_DIR "${ORT_ROOT}build/Release")
set(ORT_INCLUDE_DIR "${ORT_ROOT}include/onnxruntime/core/session"
                    "${ORT_ROOT}orttraining/orttraining/training_api/include")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

include_directories("${ORT_INCLUDE_DIR}"
                    "${EIGEN_ROOT}"
                    "${CMAKE_SOURCE_DIR}/Thirdparty")

link_directories("${ORT_LIB_DIR}"
                 "${ORT_LIB_DIR}/_deps/onnx-build"
                 "${ORT_LIB_DIR}/_deps/protobuf-build"
                 "${ORT_LIB_DIR}/_deps/re2-build"
                 "${ORT_LIB_DIR}/_deps/abseil_cpp-build/absl/base"
                 "${ORT_LIB_DIR}/_deps/abseil_cpp-build/absl/container"
                 "${ORT_LIB_DIR}/_deps/abseil_cpp-build/absl/hash"
                 "${ORT_LIB_DIR}/_deps/google_nsync-build/"
                 "${ORT_LIB_DIR}/_deps/pytorch_cpuinfo-build/deps/clog"
                 "${ORT_LIB_DIR}/_deps/pytorch_cpuinfo-build/")

add_executable(${PROJECT_NAME} src/main.cpp src/train.cpp src/inference.cpp)
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
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/main.py DESTINATION bin
              PERMISSIONS
                OWNER_READ OWNER_WRITE GROUP_READ
                GROUP_WRITE WORLD_READ WORLD_WRITE
                OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/model/checkpoint DESTINATION model
              PERMISSIONS OWNER_READ GROUP_READ WORLD_READ)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/model/eval_model.onnx DESTINATION model
              PERMISSIONS OWNER_READ GROUP_READ WORLD_READ)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/model/optimizer_model.onnx DESTINATION model
              PERMISSIONS OWNER_READ GROUP_READ WORLD_READ)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/model/training_model.onnx DESTINATION model
              PERMISSIONS OWNER_READ GROUP_READ WORLD_READ)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/model/inference.onnx DESTINATION model
              PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ GROUP_WRITE WORLD_READ WORLD_WRITE)
