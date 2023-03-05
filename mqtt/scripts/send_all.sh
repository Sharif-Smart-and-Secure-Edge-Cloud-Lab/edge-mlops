#!/bin/bash

echo "Sending inference modules..."
sudo scp ./test/bin/edge-mlops pi@192.168.96.72:~/inference/edgemlops
sudo scp ./test/bin/output.onnx pi@192.168.96.72:~/inference/output.onnx
sudo scp ./test/bin/word_indexes.json pi@192.168.96.72:~/inference/word_indexes.json
echo "Done"
