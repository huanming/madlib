#include <benchmark/generators/LogisticRegressionRandom.hpp>

template <typename T>
class Slice {
public:
    typedef typename std::vector<T>::size_type size_type;
    
    Slice(const std::vector<T>& inVec, size_type inStart, size_type inEnd)
      : vec(inVec), start(inStart), end(inEnd) { }
    
    friend std::ostream& operator<<(std::ostream& inOStream,  
        const Slice& inSlice) {
        
        std::cout << '{';
        if (inSlice.start <= inSlice.end)
            std::cout << inSlice.vec[inSlice.start];
        for (size_type i = inSlice.start + 1; i <= inSlice.end; i++) {
            std::cout << ',' << inSlice.vec[i];
        }
        std::cout << '}';
        return inOStream;
    }
    
protected:
    const std::vector<T> &vec;
    size_type start;
    size_type end;
};

class PGPolicy {
protected:
    void printCoef(const std::vector<double>& inCoef) {
        std::cout << Slice<double>(inCoef, 0, inCoef.size() - 1) << '\n';
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
        std::cout << Slice<double>(inRow, 0, inRow.size() - 2)
            //<< '\t' << getBooleanStr( inRow[inRow.size() - 1] ) << '\n';
            << '\t' <<  inRow[inRow.size() - 1]  << '\n';
    }
};

int main(int inArgC, char* inArgVec[]) {
    return LogisticRegressionRandom<PGPolicy>(inArgC, inArgVec).run();
}
