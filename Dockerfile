FROM ubuntu:22.04

# create a volume and download prequisites


# install essential tools
RUN apt-get update && apt-get install -y build-essential \
    cmake \
    make \
    git \
    vim 

RUN apt-get install -y git

# copy and extract toolchain 
WORKDIR /TC 
COPY arm-tc.tar.xz .
RUN tar -xf arm-tc.tar.xz
RUN rm arm-tc.tar.xz

RUN apt-get install wget

# download protoc
WORKDIR /protoc
RUN wget -O protoc.zip https://github.com/protocolbuffers/protobuf/releases/download/v3.18.1/protoc-3.18.1-linux-x86_64.zip
RUN apt-get install unzip
RUN unzip protoc.zip

WORKDIR /ORT
COPY tool.cmake .
ENV PATH="/TC/arm-gnu-toolchain-11.3.rel1-x86_64-arm-none-linux-gnueabihf/bin:${PATH}"

RUN apt-get install -y python3 python3-pip
RUN pip install flatbuffers
# RUN ./build.sh --config Release --parallel --arm --update --build --build_shared_lib --cmake_extra_defines ONNX_CUSTOM_PROTOC_EXECUTABLE=<path to bin/protoc> CMAKE_TOOLCHAIN_FILE=/ORT/onnxruntime/tool.cmake

CMD ["/bin/bash"]
