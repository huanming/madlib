#include <benchmark/generators/KMeansFloatRandom.hpp>
#include <benchmark/generators/PrintArray.hpp>

class PGPolicy {
protected:
    void printTableRow(const std::vector<double> &inRow) {
        std::cout << PrintArray<double>(inRow, 0, inRow.size() - 1) << '\n';
    }
};

int main(int inArgC, char* inArgVec[]) {
    return KMeansFloatRandom<PGPolicy>(inArgC, inArgVec).run();
}
