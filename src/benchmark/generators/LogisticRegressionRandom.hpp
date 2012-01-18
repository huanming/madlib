/* -----------------------------------------------------------------------------
 *
 * @file LogisticRegressionRandom.hpp
 *
 * @brief Generate random coefficients and training data points
 *
 * -------------------------------------------------------------------------- */

#include <boost/program_options.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>
#include <iostream>

/**
 * @brief Generate random coefficients and training data points
 *
 * The parameters are self-explanatory. See the source code. It is crucial that
 * a seed can be specified in order to make data generation both deterministic
 * (reproducible) and pseudo-random.
 *
 * Coefficients \f$ c_i \f$ are generated uniformly at random in the interval
 * \f$ [-1,1] \f$. The independent variables \f$ x_i \f$ of each training data
 * point \f$ (\vec x, y) \f$ are generated likewise. 
 *
 * The dependent variable \f$ y \f$ is a binomimal random variate with.
 */
template <class FormatPolicy>
class LogisticRegressionRandom : public FormatPolicy {
    using FormatPolicy::printCoef;
    using FormatPolicy::printTableRow;

protected:
    class LogisticRegressionArgs {
        public:
    			LogisticRegressionArgs(int inArgC, char* inArgVec[]) {
    				namespace po = boost::program_options;
				try {
					po::options_description desc("Allowed options");
					desc.add_options()
						("help,h", "produce help message")
						("ivariables,i", po::value(&numIndVars)->default_value(5),
							"number of independent variables")
						("rows,r", po::value(&numRows)->default_value(100),
							"number of rows")
						("stddev,d", po::value(&stdDev)->default_value(1.),
							"standard deviation of noise term")
						("coef-seed", po::value<>(&coefSeed)->default_value(0),
							"seed for random-number generator for generating coefficients")
						("table-seed", po::value<>(&tableSeed)->default_value(1),
							"seed for random-number generator for generating table")
						("coef,c", "generate coefficients")
						("table,t", "generate table of data points")
					;

					po::variables_map vm;
					po::store(po::parse_command_line(inArgC, inArgVec, desc), vm);
					po::notify(vm);

					outputIsCoefOnly = vm.count("coef") > 0;

					if (vm.count("help") ||
						vm.count("coef") + vm.count("table") != 1) {

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

    		    uint32_t numIndVars;
    		    uint64_t numRows;
    		    double stdDev;
    		    uint32_t coefSeed;
    		    uint32_t tableSeed;
    		    bool outputIsCoefOnly;
        };


    LogisticRegressionArgs args;
    boost::uniform_real<> uniformDist;
    boost::uniform_real<> uniform01Dist;
    boost::normal_distribution<> normalDist;
    boost::mt19937 randomNoGenerator;
    boost::variate_generator<boost::mt19937&, boost::uniform_real<> >
        uniformVariate;
    boost::variate_generator<boost::mt19937&, boost::uniform_real<> >
        uniform01Variate;
    boost::variate_generator<boost::mt19937&, boost::normal_distribution<> >
        normalVariate;

public:
    
    std::vector<double> coef;

    LogisticRegressionRandom(int inArgC, char* inArgVec[])
      : args(inArgC, inArgVec),
        uniformDist(-1, 1),
        uniform01Dist(0, 1),
        normalDist(0, args.stdDev),
        uniformVariate(randomNoGenerator, uniformDist),
        uniform01Variate(randomNoGenerator, uniform01Dist),
        normalVariate(randomNoGenerator, normalDist) {
        

        
        randomNoGenerator.seed(args.coefSeed);
        for (uint16_t i = 0; i < args.numIndVars; i++)
            coef.push_back(uniformVariate());
    }

    double logisticFunc(double x){
        return 1/(1+exp(-x));
    }	

    void printTable() {
        randomNoGenerator.seed(args.tableSeed);
        
        // preallocate vector
        std::vector<double> row(args.numIndVars + 1);
        
        for (uint64_t i = 0; i < args.numRows; i++) {
            double dotProduct = 0;
            
            for (uint16_t j = 0; j < args.numIndVars; j++) {
                row[j] = uniformVariate();
                dotProduct += coef[j] * row[j];
            }
            row[args.numIndVars] = ( uniform01Variate() < logisticFunc( -1*dotProduct + normalVariate() ) );
            printTableRow(row);
        }
    }
    
    int run() {
        if (args.outputIsCoefOnly)
            printCoef(coef);
        else
            printTable();

        return EXIT_SUCCESS;
    }
};
