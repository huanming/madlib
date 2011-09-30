# ------------------------------------------------------------------------------
# benchmark framework source files
# ------------------------------------------------------------------------------


# -- 1. Copy all *.py files ----------------------------------------------------

file(GLOB_RECURSE BENCHMARK_FILES
    RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
    "*.py"
)
add_files(BENCHMARK_TARGET_FILES . "${CMAKE_CURRENT_BINARY_DIR}"
    ${BENCHMARK_FILES})
add_custom_target(benchmarkFiles ALL DEPENDS ${BENCHMARK_TARGET_FILES})


# -- 2. Install benchmark files to $MADLIB_ROOT/benchmark, set executable flags
#       for benchmark.py -------------------------------------------------------

install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    DESTINATION .
    USE_SOURCE_PERMISSIONS
    COMPONENT benchmark
    FILES_MATCHING
    PATTERN "*.py"
    PATTERN ".DS_Store" EXCLUDE
)
