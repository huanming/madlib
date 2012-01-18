# ------------------------------------------------------------------------------
# Linux-specific files
# ------------------------------------------------------------------------------


# -- 1. Copy all benchmark files -----------------------------------------------

    file(GLOB_RECURSE BENCHMARK_FILES_LINUX
        RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
        "benchmark/*.py"
        "__init__.py"
    )
    add_files(BENCHMARK_TARGET_FILES_LINUX . "${CMAKE_CURRENT_BINARY_DIR}"
        ${BENCHMARK_FILES_LINUX})
    add_custom_target(benchmarkFiles_linux ALL
        DEPENDS ${BENCHMARK_TARGET_FILES_LINUX})


# -- 2. Install all Benchmark Python files -------------------------------------

    install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DESTINATION port/linux
        USE_SOURCE_PERMISSIONS
        COMPONENT benchmark
        FILES_MATCHING
        PATTERN "benchmark/*.py"
        PATTERN ".DS_Store" EXCLUDE
    )
