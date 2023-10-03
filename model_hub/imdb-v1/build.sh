#!/bin/bash

echo "Running build process..."
cd /imdb-v1
mkdir build
cd ./build
cmake -DCMAKE_TOOLCHAIN_FILE=/imdb-v1/TC-arm.cmake -DCMAKE_INSTALL_PREFIX=/imdb-v1/install ..
make
make install
