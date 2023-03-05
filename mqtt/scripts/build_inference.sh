#!/bin/bash

echo "Running build process..."
cd /inference
mkdir build
cd ./build
cmake -DCMAKE_TOOLCHAIN_FILE=/inference/TC-arm.cmake -DCMAKE_INSTALL_PREFIX=/test/ ..
make
make install