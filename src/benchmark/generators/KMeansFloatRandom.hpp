/* -----------------------------------------------------------------------------
 *
 * @file KMeansFloatRandom.cpp
 *
 * @brief Generate random data points
 *
 * -------------------------------------------------------------------------- */

#include <boost/program_options.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <iostream>
#include <vector>

/**
 * @brief Generate random float points
 *
 * The parameters are self-explanatory. See the source code. It is crucial that
 * a seed can be specified in order to make data generation both deterministic
 * (reproducible) and pseudo-random.
 *
 * The d dimension points are generated with k independent normal distribution.
 * r is the row number of the points.
 */
template <class FormatPolicy>
class KMeansFloatRandom : public FormatPolicy {
    using FormatPolicy::printTableRow;

protected:
    class KMeansFloatArgs {
    public:
    	KMeansFloatArgs(int inArgC, char* inArgVec[]) {
            namespace po = boost::program_options;
            try {
                po::options_description desc("Allowed options");
                desc.add_options()
                    ("help,h", "produce help message")
                    ("dimensions,d", po::value(&numDims)->default_value(5),
                        "number of dimensions")
                    ("rows,r", po::value(&numRows)->default_value(100),
                        "number of rows")
                    ("centroids,k", po::value(&numCentroids)->default_value(10),
                        "number of centroids")
                    ("stddev,d", po::value(&stdDev)->default_value(0.1),
                        "standard deviation of noise term for points around centroids ")
                    ("scope,s", po::value(&scope)->default_value(1.),
                        "max scope of mean of each centroid distribution")
                    ("centroid-seed", po::value<>(&centroidSeed)->default_value(1),
                    		"seed for random-number generator for generating centroids")
                    ("table-seed", po::value<>(&tableSeed)->default_value(1),
                        "seed for random-number generator for generating table")
                    ("centroid,c", "generate centroids")
                    ("table,t", "generate table of data points")
                ;

                po::variables_map vm;
                po::store(po::parse_command_line(inArgC, inArgVec, desc), vm);
                po::notify(vm);

                outputIsCentroidOnly = vm.count("centroid") > 0;

                if (vm.count("help") ||
                    vm.count("centroid") + vm.count("table") != 1 ) {
                    
                    std::cout << desc << "\n";
                    exit(EXIT_FAILURE);
                }
            } catch(std::exception& e) {
                std::cerr << "error: " << e.what() << "\n";
                exit(EXIT_FAILURE);
            } catch(...) {
                std::cerr << "Exception of unknown type!\n";
                exit(EXIT_FAILURE);
            }
        }
    
        uint32_t numDims;
        uint32_t numCentroids;
        uint64_t numRows;
        double stdDev;
        double scope;
        uint32_t centroidSeed;
        uint32_t tableSeed;
        bool outputIsCentroidOnly;
    };

    KMeansFloatArgs args;
    boost::mt19937 randomNoGenerator;
    boost::uniform_real<> uniformDist;
    boost::variate_generator<boost::mt19937&, boost::uniform_real<> >
        uniformVariate;
    //centroids is generated as uniform variate
    std::vector< std::vector<double> > centroids;
    //white noise
    boost::normal_distribution<> normalDist;
    boost::variate_generator<boost::mt19937&, boost::normal_distribution<> > 
        whiteNoise;

public:    
    KMeansFloatRandom(int inArgC, char* inArgVec[])
      : args(inArgC, inArgVec),
        randomNoGenerator(args.centroidSeed),
        uniformDist(-args.scope, args.scope),
        uniformVariate(randomNoGenerator, uniformDist),
        normalDist(0, args.stdDev),
        whiteNoise(randomNoGenerator, normalDist){

        for (uint16_t i = 0; i < args.numCentroids; i++){
    	    std::vector<double> centroid(args.numDims);
        	for (uint16_t j = 0; j < args.numDims; j++){
        		centroid[j] = uniformVariate();
        	}
        	centroids.push_back(centroid);
        }
    }

    void printTable() {
        randomNoGenerator.seed(args.tableSeed);
        
        // preallocate vector
        std::vector<double> row(args.numDims);
        
        for (uint64_t i = 0; i < args.numRows; i++) {
            for (uint16_t j = 0; j < args.numDims; j++)
                row[j] = centroids[i%args.numCentroids][j] + whiteNoise() ;
            printTableRow(row);
        }
    }
    
    int run() {
        if (args.outputIsCentroidOnly){
            for (uint16_t i = 0; i < args.numCentroids; i++){
        			printTableRow(centroids[i]);
        		}
    		}
        else
            printTable();

        return EXIT_SUCCESS;
    }
};
