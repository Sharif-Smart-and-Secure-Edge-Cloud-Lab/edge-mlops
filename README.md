# MLOps

MLOps is an emerging field of ML research that aims to enable and automate ML models into production. According to [sig-mlops](https://github.com/cdfoundation/sig-mlops) MLOps is defined as:
> the extension of the DevOps methodology to include Machine Learning and Data Science assets as first class citizens within the DevOps ecology

In this repository we won't discuss benfites and limitations of MLOps, but we provide some references for those who are interested in using MLOps.

+ [Very detailed tutorial in MLOps](https://ml-ops.org/)
+ [The difference between DevOps and MLOps](https://hackernoon.com/why-is-devops-for-machine-learning-so-different-384z32f1)
+ [AutoML organization and tools](https://www.automl.org/)

**Note:** AutoML is a technology that targets non-expert ML practitioners to build and deploy ML models. It can be used in conjuction with MLOps. However, it is fairly in early stages and we're not going to discuss it here.

## Pipeline
Based on our research and the requirements of the project, we decided to use the following pipeline:

1. **Automatic model training:** We will autmoate the training of a face detection/recognition model.
2. **Automatic build:** The process of packaging will be automated (creation of Docker images, building of Docker containers, etc.).
3. **Automatic deployment:** The Docker images will be deployed to a local server automatically.
4. **Model monitoring:** We will provide simple logging and monitoring tools to monitor the performance of the model.
5. **Metadata gathering:** During whole pipeline execution, some metadata will be gathered and stored in the database.
6. **Triggering mechanisms:** The pipeline execution triggering mechanism will be based on pipeline change and manual triggering.

