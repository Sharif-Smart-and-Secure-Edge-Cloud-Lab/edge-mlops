# MLOps

**Contents:**

+ [Introduction](#introduction)
+ [Pipeline](#pipeline)
   + [Model and dataset versioning](#model-and-dataset-versioning)
   + [Our choice of tools](#our-choice-of-tools)
+ [Model training](#model-training)
+ [ONNXRuntime cross compiling](#onnxruntime-cross-compiling)
   + [Manual compilation](#1-manual-compilation)
   + [Docker image](#2-docker-image)
+ [How to guides](#how-to-guides)

## Introduction
MLOps is an emerging field of ML research that aims to enable and automate ML models into production. According to [sig-mlops](https://github.com/cdfoundation/sig-mlops) MLOps is defined as:

> the extension of the DevOps methodology to include Machine Learning and Data Science assets as first class citizens within the DevOps ecology

In this repository we won't discuss benfites and limitations of MLOps, but we provide some references for those who are interested in using MLOps.

- [Very detailed tutorial in MLOps](https://ml-ops.org/)
- [The difference between DevOps and MLOps](https://hackernoon.com/why-is-devops-for-machine-learning-so-different-384z32f1)
- [AutoML organization and tools](https://www.automl.org/)

**Note:** AutoML is a technology that targets non-expert ML practitioners to build and deploy ML models. It can be used in conjuction with MLOps. However, it is fairly in early stages and we're not going to discuss it here.

## Pipeline

Based on our research and the requirements of the project, we decided to use the following pipeline:

1. **Model and dataset versioning:** As ML-base software is fundamentally different from traditional software, model and dataset versioning is an issue and cannot be handled just by using git (as the amount of data is too large).
2. **Automatic model training:** We will autmoate the training of a face detection/recognition model.
3. **Automatic build:** The process of packaging will be automated (creation of Docker images, building of Docker containers, etc.).
4. **Automatic deployment:** The Docker images will be deployed to a local server automatically.
5. **Model monitoring:** We will provide simple logging and monitoring tools to monitor the performance of the model.
6. **Metadata gathering:** During whole pipeline execution, some metadata will be gathered and stored in the database.
7. **Triggering mechanisms:** The pipeline execution triggering mechanism will be based on pipeline change and manual triggering.

A discussion of currently available tools for each stage of the pipeline is provided below.

### Model and dataset versioning

As mentioned briefly above, ML-base software is different from traditional software in that it is not enough to only have code, but also one need whole dataset to produce the exact model. Plus, the explicit relationship between input and output is not known. So, it requires special attention to versioning.

Git is widely used in versioning and source control for traditional software. However, it is not suitable for ML-base software. The dataset is too large and it is not feasible to index it in git. Models are binary and switching between different versions of the model is not easy. There are other reasons that git alone is not suitable for ML-base software. You can refer to [this](https://github.com/cdfoundation/sig-mlops/blob/main/roadmap/2022/MLOpsRoadmap2022.md#challenges) for more information.

Tools for versioning ML-base software:

1. **[DVC:](https://dvc.org/)** An open-source git-based version control system for ML projects. It is by far the most popular version control system in the wild.
2. **[dotmesh:](https://dotmesh.com/)** According to [dotmesh](https://github.com/dotmesh-io/dotmesh)
   > dotmesh (dm) is like git for your data volumes (databases, files etc) in Docker and Kubernetes

`dotmesh` doesn't have an active community and the latest release was in 2020. So, `DVC` is the best and pretty the only solution for version control. Some important features of `DVC` are (according to [DVC features](https://dvc.org/features)):

- Git-compatible
- Storage agnostic
- Reproducible
- Low friction branching
- Metric tracking
- ML pipeline framework
- Language and framework agnostic
- Track failures

So, we are considering to use DVC as a version and CI/CD app.

Tools for CI/CD

The other option for us is jenkins. This open-source software can provide us with a pipeline that could be run right after the version-control app but it does not provide any version-control itself unlike Gitlab and DVC.

Other option is docker compose but we have the same problem as jenkins. It does not provide any version-control for us.

We are considering the choice between DVC and gitlab as both of these tools are very useful in our case .

### Our choice of tools
We are focusing on developing MLOps techniques for edge devices. Edge devices are quite versatile and designed by different manufacturers. So, we need to have a tool that is compatible with different edge devices and to be device-agnostic. Another important feature is to be framework-agnostic. In other words, we should be able to use all models that are trained with different frameworks, without any modification. To tackle this two issues, we used the following pipeline:

![pipeline](./images/pipeline.png)

`ONNX` standard helps us to be framework agnostic. Almost all training frameworks support ONNX and one can convert the final model to a `.onnx` format and later use it in inference frameworks that support this format (such as `OpenVINO` and `ONNXRuntime`). For inference side, we are going to use `ONNXRuntime`. It is a cross-platform inference engine that supports multiple frameworks and hardware accelerators. So, it's a great choice for edge devices. 

Plus we are using `Docker` to package our application and it's dependencies. It also helps us to create a CI/CD pipeline which is essential for MLOps. As `Docker` it self could be inefficient for edge devices, we are using `balenaOS` which is a lightweight OS, tailored for each hardware with capabilities to run `Docker` containers. Under the hood, `balenaOS` uses `yocto` to build the image file. As of writing this doc, it supports more than 80 devices. More information about `balenaOS` can be found [here](https://www.balena.io/os/).

## Model Training
For the model in this project, we decided to use the IMDB movie reviews dataset. This dataset contains reviwes from users for movies which are labeled either a positive review or a negative review. The format of each data in this dataset is an array of numbers which represent a word in this dataset's dictionary. </br>
For example the word "film" is indexed as integer 13 in this dataset. 
An example:
```
print(data[0])


[1, 14, 22, 16, 43, 530, 973, 1622, 1385, 65, 458, 4468, 66, 3941, 4, 173, 36, 256, 5, 25, 100, 43, 838, 112, 50, 670, 2, 9, 35, 480, 284, 5, 150, 4, 172, 112, 167, 2, 336, 385, 39, 4, 172, 4536, 1111, 17, 546, 38, 13, 447, 4, 192, 50, 16, 6, 147, 2025, 19, 14, 22, 4, 1920, 4613, 469, 4, 22, 71, 87, 12, 16, 43, 530, 38, 76, 15, 13, 1247, 4, 22, 17, 515, 17, 12, 16, 626, 18, 2, 5, 62, 386, 12, 8, 316, 8, 106, 5, 4, 2223, 5244, 16, 480, 66, 3785, 33, 4, 130, 12, 16, 38, 619, 5, 25, 124, 51, 36, 135, 48, 25, 1415, 33, 6, 22, 12, 215, 28, 77, 52, 5, 14, 407, 16, 82, 2, 8, 4, 107, 117, 5952, 15, 256, 4, 2, 7, 3766, 5, 723, 36, 71, 43, 530, 476, 26, 400, 317, 46, 7, 4, 2, 1029, 13, 104, 88, 4, 381, 15, 297, 98, 32, 2071, 56, 26, 141, 6, 194, 7486, 18, 4, 226, 22, 21, 134, 476, 26, 480, 5, 144, 30, 5535, 18, 51, 36, 28, 224, 92, 25, 104, 4, 226, 65, 16, 38, 1334, 88, 12, 16, 283, 5, 16, 4472, 113, 103, 32, 15, 16, 5345, 19, 178, 32]
```

If we translate the entry above we will get this:
```

# this film was just brilliant casting location scenery story direction everyone's really suited the part they played and you could just imagine being there robert # is an amazing actor and now the same being director # father came from the same scottish island as myself so i loved the fact there was a real connection with this film the witty remarks throughout the film were great it was just brilliant so much that i bought the film as soon as it was released for # and would recommend it to everyone to watch and the fly fishing was amazing really cried at the end it was so sad and you know what they say if you cry at a film it must have been good and this definitely was also # to the two little boy's that played the # of norman and paul they were just brilliant children are often left out of the # list i think because the stars that play them all grown up are such a big profile for the whole film but these children are amazing and should be praised for what they have done don't you think the whole story was so lovely because it was true and was someone's life after all that was shared with us all

```
The "#" characters are the ones that are not available in model's dictionary.


The directory ```saved_model``` contains saved model from tensorflow.</br>
The directory ```convert_model``` contains the onnx model.</br>
To get the onnx output use the command below:
```
$>python -m tf2onnx.convert --saved-model ./saved_model/ --opset 12 --output ./convert_model/output.onnx
```
## ONNXRuntime Cross Compiling
We have cross compiled ORT for armv7 architecture and tested it on Raspberry Pi 400. First, clone onnxruntime repository and a custom protoc version for cross compiling (refer to [ORT](https://onnxruntime.ai/docs/build/inferencing.html#arm) documentation for more details). You can either follow these steps to compile ORT manually or use the Dockerfile provided in this repository. First, manual steps are explained and then using Docker is introduced.
### 1) Manual compilation
I have used the following `tool.cmake` file for cross compiling:

```cmake
SET(CMAKE_SYSTEM_NAME Linux)
SET(CMAKE_SYSTEM_VERSION 1)
SET(CMAKE_SYSTEM_PROCESSOR armv7-a)

SET(CMAKE_SYSROOT <path to sysroot>)

SET(CMAKE_C_COMPILER arm-none-linux-gnueabihf-gcc)
SET(CMAKE_CXX_COMPILER arm-none-linux-gnueabihf-g++)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-psabi")

SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

Make sure that ARM toolchain is accessible from PATH (otherwise provide absolute path). You might want to transfer linker and some exectuables to your `/usr` path (such as `ld-linux-armhf.so.3` to `/usr/arm-linux-gnueabihf/`).

I compiled v1.12.1 of ORT. It seems that v1.13 has some issues with cmake. So, make sure to use v1.12.1:

```bash
$ git checkout v.1.12.1
```

Next, run the following command to cross compile ORT:

```bash
./build.sh --config Release --parallel --arm --update --build --build_shared_lib --cmake_extra_defines ONNX_CUSTOM_PROTOC_EXECUTABLE=<path to bin/protoc> CMAKE_TOOLCHAIN_FILE=<path to tool.cmake>
```

After waiting a long time, dynamic and static libraries will be generated. You can find them in `build/Linux/Release/` directory. Set this path in `CMakeLists.txt` to compile this project. Also set include directory path in `CMakeLists.txt` and change `TC-arm.cmake` accordingly. Finally, build the project (from `build` folder):

```bash
$ cmake -DCMAKE_TOOLCHAIN_FILE=<path to TC-arm.cmake> -DCMAKE_INSTALL_PREFIX=<install prefix> ..
$ make 
$ make install
```
And you're all set!

### 2) Docker image
You can use the Dockerfile provided in this repository to build a Docker image that will cross compile your project with ORT libraries. The final image can be used either manually or as a base image for your project. Image is built on `Ubuntu:22.04` base image. The final image is around 4GB. You can build the image with the following command (make sure that you are in this repository's root directory):

```bash
$ docker build . -t edgemlops:1.0.0
```

Image building process could take about two hours (depending on your machine and internet speed). After building the image, ORT libraries are in `/ORT/onnxruntime/` directory. 

___
## How to guides
We provide documentations on common "How to" questions. You refer to one of the following docs for more information:
+ [How to develope model from scratch?](./doc/develope-model.md)
+ [How to use existing, pretrained models with this pipeline?](./doc/use-existing-models.md)
