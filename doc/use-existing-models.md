# How to use ONNX model with our pipeline?
In this document, we will discuss how to use your custom model with our pipeline. You have either trained your model and converted to ONNX format (for more information return to [this doc](./develope-model.md)), or have a pretrained ONNX model. In both cases, you can use our pipeline. 

**Contents:**
+ [Limitations and scope](#limitations-and-scope)
+ [Processings in C++](#processings-in-cpp)
+ [Model deployment](#model-deployment)

## Limitations and scope
With our pipeline, you can deploy your model on any device that supports ONNXRuntime framework. As of now, we only support `armv7` architecture. However, `armv8`,  `intel`, and `RiscV` architecture can be supported. This pipeline cross compiles your code and links all dependencies statically. Therefore, you won't need any extra depenedencies in the target environment. The findal product of compilation process can be transferred to the target machine to be executed. Right now we don't support any specific libraries other than ORT itself. However, we're working on supporting OpenCV in our pipeline.
## Processings in Cpp
Probably the most challenging step of using the pipeline is the conversion of pre- and post-processings from Python to C++. Although ONNX bridges the gap between model inference on different devices, languages, and frameworks, but one must convert extra processings, too. For instance, in a face detection model, input image must be resized to `224x224` and normalized to be between [0, 1] so that it can be fed into the model. These are essential pre-processings that must also be done in C++. Furthermore, in many detection models, lots of predicted bounding boxes must be thrown away. This is done by applying `NMS` on the output of the model. These kind of processings are called post-processings.

Therefore, you should convert your extra processings from Python to C++, too. You can either write them from scratch, or use existing libraries. As of now, we don't support any extra libraries other than ORT itself, but we are working on adding OpenCV support to our pipeline. Thus, we **suggest using OpenCV library for computer vision tasks** in Python, so that it can be easily translated to C++ later. 

You should create your processing architecture in C++. Also, you should also compile your code to generate final executable. We suggest **using CMake** as it can be used across various systems. 

We have created a simple example in `inference` directory. It shows ORT API usage and a template `CMakeLists.txt` is provided, too. You can use these codes as an starting point and later read documentations for a more advanced scenarios.
## Model deployment
After creating processing pipeline in C++, it must be compiled and then final executable must be trasnferred to the target environment. To do so, first build the docker image. We explained it in [README.md](./../README.md) file. Then, trasfer your project to the container, and compile it with ORT. Finally, you can trasnfer the generated executable to the target machine to be run.

