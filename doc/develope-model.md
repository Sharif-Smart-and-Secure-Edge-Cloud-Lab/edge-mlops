# How to develope a model from scratch?
This document provides best ways to develope a deep learning model from scratch to be used with our pipeline. We tried to answer this question very generally. Feel free to contribute to this guide!

## Choosing framework
You can use any framework that is compatible with ONNX. The final product of model training must be converted to an ONNX model. Later this model is loaded to be run. Almost all major frameworks support conversion to ONNX model. The following figures shows the list of supported framework (from [ONNX website](https://onnx.ai/supported-tools.html#buildModel)):
![supported frameworks](../images/supported-frameworks.png)

Our suggestion is to use **PyTorch** for training. However, we have tested both PyTorch and TensorFlow.
## Training model
After choosing your framework, training procedure begins. The only limitation you should consider is that some operations are not supported in ONNX and ONNXRuntime (ORT). To show which version of ORT and ONNX support what operations, the concept of "opset" is defined. Each ONNX version corresponds to an opset version. For more information on opset you can refer to [this document](https://github.com/onnx/onnx/blob/main/docs/Versioning.md). Also all supported operations of ONNXRuntime are specified with a opset version that could be found in [this document](https://github.com/microsoft/onnxruntime/blob/main/docs/OperatorKernels.md). In our experience, we found out that most operations of computer vision models are supported and there might be some limitation in NLP tasks. As a rule of thumb, most common operations are supported. However, if you found a model proposed in 2022 and uses a new operation, probably it's not supported. 
## Conversion to ONNX
Now you have trained your model in your favorite pipeline and saved your best model. In this step, you should convert it to ONNX format. 
## Processings in C++

## Deploying model
