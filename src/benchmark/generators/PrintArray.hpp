/* -----------------------------------------------------------------------------
 *
 * @file PrintArray.hpp
 *
 * @brief print vector<T> as an array from start to end, each element in a array
 *  is seperated by \t, and the array is wraped by { and }.
 *  
 * -------------------------------------------------------------------------- */

template <typename T>
class PrintArray {
public:
    typedef typename std::vector<T>::size_type size_type;
    
    PrintArray(const std::vector<T>& inVec, size_type inStart, size_type inEnd)
      : vec(inVec), start(inStart), end(inEnd) { }
    
    friend std::ostream& operator<<(std::ostream& inOStream,  
        const PrintArray& inPrintArray) {
        
        std::cout << '{';
        if (inPrintArray.start <= inPrintArray.end)
            std::cout << inPrintArray.vec[inPrintArray.start];
        for (size_type i = inPrintArray.start + 1; i <= inPrintArray.end; i++) {
            std::cout << ',' << inPrintArray.vec[i];
        }
        std::cout << '}';
        return inOStream;
    }
    
protected:
    const std::vector<T> &vec;
    size_type start;
    size_type end;
};
