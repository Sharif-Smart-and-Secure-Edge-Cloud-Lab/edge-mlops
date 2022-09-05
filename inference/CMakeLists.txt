cmake_minimum_required(VERSION 3.10)

project("edge-mlops")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(${PROJECT_NAME} src/main.cpp src/Model.cpp)
