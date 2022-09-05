#include <iostream>
#include <array>
#include "Model.hpp"

int main(){
    Model m{"/home/nima/Documents/l/edge-mlops/inference/word_indexes.json"};
    std::array<int, 1000> v = m.convertToIndexes("this film was just brilliant");
}
