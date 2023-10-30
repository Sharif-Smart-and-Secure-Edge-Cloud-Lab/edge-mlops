#ifndef _TRAIN_H_
#define _TRAIN_H_

#include <memory>
#include "onnxruntime_training_cxx_api.h"
#include "session_cache.h"

float train_step(
    std::shared_ptr<SessionCache> session_cache, float* batches, int64_t* labels,
    int64_t batch_size);

#endif //_TRAIN_H_