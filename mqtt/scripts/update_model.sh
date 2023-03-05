#!/bin/bash

echo "Replacing model"
sudo scp ./convert_model/output.onnx pi@192.168.96.72:~/inference/output.onnx
echo "Done"
