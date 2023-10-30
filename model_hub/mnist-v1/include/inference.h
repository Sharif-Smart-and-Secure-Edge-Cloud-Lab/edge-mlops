#ifndef _INFERENCE_H_
#define _INFERENCE_H_

#include <vector>
#include <string>
#include <memory>
#include "session_cache.h"


std::vector<float> classify(
    std::shared_ptr<SessionCache> session_cache,
    float* img_data, int64_t batch_size);

#endif //_INFERENCE_H_