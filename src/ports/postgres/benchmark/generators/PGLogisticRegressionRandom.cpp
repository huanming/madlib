#include <benchmark/generators/LogisticRegressionRandom.hpp>
#include <benchmark/generators/PrintArray.hpp>

class PGPolicy {
protected:
    void printCoef(const std::vector<double>& inCoef) {
        std::cout << PrintArray<double>(inCoef, 0, inCoef.size() - 1) << '\n';
    }

    std::string getBooleanStr(float y){
        std::string t = "\'t\'";
        std::string f = "\'f\'";
        if (abs(y) < 0.0001 )
            return f;
        else
            return t;

    }
    
    void printTableRow(const std::vector<double> &inRow) {
        std::cout << PrintArray<double>(inRow, 0, inRow.size() - 2)
            //<< '\t' << getBooleanStr( inRow[inRow.size() - 1] ) << '\n';
            << '\t' <<  inRow[inRow.size() - 1]  << '\n';
    }
};

int main(int inArgC, char* inArgVec[]) {
    return LogisticRegressionRandom<PGPolicy>(inArgC, inArgVec).run();
}
