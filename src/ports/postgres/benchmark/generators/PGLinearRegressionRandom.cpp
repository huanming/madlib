#include <benchmark/generators/LinearRegressionRandom.hpp>
#include <benchmark/generators/PrintArray.hpp>

class PGPolicy {
protected:
    void printCoef(const std::vector<double>& inCoef) {
        std::cout << PrintArray<double>(inCoef, 0, inCoef.size() - 1) << '\n';
    }
    
    void printTableRow(const std::vector<double> &inRow) {
        std::cout << PrintArray<double>(inRow, 0, inRow.size() - 2)
            << '\t' << inRow[inRow.size() - 1] << '\n';
    }
};

int main(int inArgC, char* inArgVec[]) {
    return LinearRegressionRandom<PGPolicy>(inArgC, inArgVec).run();
}
