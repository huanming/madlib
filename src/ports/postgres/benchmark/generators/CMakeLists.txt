set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME OFF)
find_package(Boost 1.46 COMPONENTS program_options)

if(Boost_FOUND)
    add_executable(PGTestLinearRegressionRandom PGLinearRegressionRandom.cpp)
    set_target_properties(PGTestLinearRegressionRandom PROPERTIES
        OUTPUT_NAME LinearRegressionRandom
    )
    target_link_libraries(PGTestLinearRegressionRandom ${Boost_PROGRAM_OPTIONS_LIBRARY})

    add_executable(PGTestLogisticRegressionRandom PGLogisticRegressionRandom.cpp)
    set_target_properties(PGTestLogisticRegressionRandom PROPERTIES
        OUTPUT_NAME LogisticRegressionRandom
    )
    target_link_libraries(PGTestLogisticRegressionRandom ${Boost_PROGRAM_OPTIONS_LIBRARY})
endif()
