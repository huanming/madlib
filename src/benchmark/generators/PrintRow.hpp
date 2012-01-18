/* -----------------------------------------------------------------------------
 *
 * @file PrintRow.hpp
 *
 * @brief print vector<T> as a row from start to end, each element in a row is 
 *  seperated by \t.
 *
 * -------------------------------------------------------------------------- */


template <typename T>
class PrintRow {
public:
    typedef typename std::vector<T>::size_type size_type;
    
    PrintRow(const std::vector<T>& inVec, size_type inStart, size_type inEnd)
      : vec(inVec), start(inStart), end(inEnd) { }
    
    friend std::ostream& operator<<(std::ostream& inOStream,  
        const PrintRow& inPrintRow) {
        
        if (inPrintRow.start <= inPrintRow.end)
            std::cout << inPrintRow.vec[inPrintRow.start];
        for (size_type i = inPrintRow.start + 1; i <= inPrintRow.end; i++) {
            std::cout << '\t' << inPrintRow.vec[i];
        }
        return inOStream;
    }
    
protected:
    const std::vector<T> &vec;
    size_type start;
    size_type end;
};
