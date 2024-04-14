project(CC_parseCmdLineArgs)

#All *.c files in current directory built into a static library named "libCC_parseCmdLineArgs.a"
file(GLOB SRC_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.c)
add_library(CC_parseCmdLineArgs STATIC ${SRC_FILES})

#Find gtest's *.h directory saved in GTEST_INCLUDE_DIR, and *.a file saved in GTEST_LIB_DIR
find_path(GTEST_INCLUDE_DIR gtest/gtest.h)
find_library(GTEST_LIB_DIR gtest)

#Each *.cxx file in the test directory is UT and built into an executable with gtest named "UT_<filename>.bin"
file(GLOB TEST_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cxx)
foreach(TEST_FILE ${TEST_FILES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    add_executable(UT_${TEST_NAME}.bin ${TEST_FILE})
    target_include_directories(UT_${TEST_NAME}.bin PRIVATE ${GTEST_INCLUDE_DIR})
    target_link_libraries(UT_${TEST_NAME}.bin CC_parseCmdLineArgs ${GTEST_LIB_DIR})

    #Add test to CMake
    add_test(NAME UT_${TEST_NAME} COMMAND UT_${TEST_NAME}.bin)
endforeach(TEST_FILE)