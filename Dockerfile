FROM ubuntu:22.04

# install essential tools and libraries
RUN apt-get update && apt-get install -y build-essential \
    cmake make git vim wget unzip \
    python3 python3-pip
RUN pip install flatbuffers

# create a volume and download prequisites
WORKDIR /protoc
RUN wget -O protoc.zip https://github.com/protocolbuffers/protobuf/releases/download/v3.18.1/protoc-3.18.1-linux-x86_64.zip
RUN unzip protoc.zip

WORKDIR /TC 
COPY arm-tc.tar.xz .
RUN mkdir arm-tc && tar -xf arm-tc.tar.xz -C arm-tc --strip-components 1 && rm arm-tc.tar.xz
ENV PATH="${PATH}:/TC/arm-tc/bin"

WORKDIR /ORT
RUN git clone --recursive https://github.com/Microsoft/onnxruntime.git
COPY tool.cmake ./onnxruntime/tool.cmake

# compile onnxruntime
WORKDIR /ORT/onnxruntime
RUN git checkout v1.12.1
RUN ./build.sh --config Release --parallel --arm --update --build --build_shared_lib --cmake_extra_defines ONNX_CUSTOM_PROTOC_EXECUTABLE=/protoc/bin/protoc CMAKE_TOOLCHAIN_FILE=/ORT/onnxruntime/tool.cmake

CMD ["/bin/bash"]
