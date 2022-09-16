cmake_minimum_required(VERSION 3.10)

project("edge-mlops")

enable_language(CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-psabi")
message(STATUS "Compiling for armv7 architecture")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
set(ONNXRUNTIME_INCLUDE_DIR "/home/nima/onnxruntime/include/onnxruntime/core/session")
include_directories("${ONNXRUNTIME_INCLUDE_DIR}")

link_directories("${CMAKE_CURRENT_SOURCE_DIR}/ort/lib")

add_executable(${PROJECT_NAME} src/main.cpp src/Model.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/ort/lib")
target_link_libraries(${PROJECT_NAME} onnxruntime 
                                      -static-libgcc 
                                      -static-libstdc++)
                                      
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/ort DESTINATION .)
install(TARGETS ${PROJECT_NAME} DESTINATION bin
        LIBRARY DESTINATION ort/lib)
