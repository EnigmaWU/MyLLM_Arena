#include <gtest/gtest.h>

#include <thread>

#include "CC_parseCmdLineArgs.h"

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//===TEMPLATE OF UT DESIGN===
// We design UT from following aspects/category:
//   FreelyDrafts, Typical, Demo, Boundary, State, Performance, Concurrency, Robust, Fault, Misuse, Others.
//      align to IMPROVE VALUE、AVOID LOST、BALANCE SKILL vs COST.
//---------------------------------------------------------------------------------------------------------------------
//[FreelyDrafts]: Any natural or intuitive idea, first write down here freely and causally as quickly as possible,
//  then refine it, rethink it, refactor it to a category from one a main aspect or category.
//[Typical]: a typical case, used to verify SUT's basic typical usage or call flow examples.
//[Capability]: a capability case, used to verify SUT's MAX or MIN capability, or SUT's buffer LOW or HIGH threshold.
//[Demo]: a demo case, used to verify a complete/full features of a product model or series.
//[Boundary]: a boundary case, used to verify API's argument boundary, such as NULL, MAX, MIN, MAX+1, MIN-1, etc
//[State]: a state case, used to verify FSM of SUT's Objects, such as init, start, stop, pause, resume, exit, etc
//[Performance]: a performance case, used to verify SUT's performance or bottleneck or benchmark,
//  such as how many times of API can be called in 1 second, or each API's time consumption.
//[Concurrency]: a concurrency case, used to verify SUT's concurrent or parallel or data race condition or deadlock,
//  such as many threads call SUT's API at the same time and always related to:
//      ASync/Sync, MayBlock/NonBlock/Timeout, Burst/RaceCondition/Priority/Parallel/Serial/DeadLock/Starvation/...
//[Robust]: a robust case, used to verify SUT's robustness, stability, reliability, availability, or fault tolerance,
//  such as repeatly reach SUT's max capacity, let its buffer full then empty.
//[Fault]: a fault injection case, used to verify SUT's fault injection or exception handling,
//  such as one process crash or kill by OS, then it auto restarted.
//[Misuse]: a misuse case, used to verify SUT's security, or misuse, or abuse, or negative cases,
//  such as call API in wrong order, or call API with wrong arguments.
//[Compatibility]: a compatibility case, used to verify SUT's API compatibility or dependency layer's API,
//  such as call API in different version of SUT, or call API in different OS.
//[Others]: any other cases, not have clear category, but still has value to verify.
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//===TEMPLATE OF UT CASE===
/**
 * @[Name]: ${verifyBehivorX_byDoABC}
 * @[Purpose]: ${according to what in SPEC/UserStory, and why to verify in this way}
 * @[Steps]: ${how to do}
 *   1) do ..., with ..., as SETUP
 *   2) do ..., with ..., as BEHAVIOR
 *   3) do ..., with ..., as VERIFY
 *   4) do ..., with ..., as CLEANUP
 * @[Expect]: ${how to verify} as KeyVerifyPoint
 * @[Notes]:
 */
TEST(UT_NameOfCategory, CaseNN_verifyBehivorX_byDoABC) {
  //===SETUP===
  // 1. ...

  //===BEHAVIOR===
  //@VerifyPoint xN(each case MAY have many 'ASSERT_XYZ' check points)

  //===VERIFY===
  //@KeyVerifyPoint<=3(each case SHOULD has less than 3 key 'ASSERT_XYZ' verify points)

  //===CLEANUP===
}
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
 CC_parseCmdLineArgs is SUT, #file:CC_parseCmdLineArgsTest_byCopilot.cxx #file:CC_parseCmdLineArgsTest_byCopilotChat.cxx
 is already exist UT, read TEMPLATE OF UT DESIGN and TEMPLATE OF UT CASE in
 #file:CC_parseCmdLineArgsTest_byCopilotChat_withMyPromptUT.cxx ,
 first think what UT exist, then think what missing UT
 */
//---------------------------------------------------------------------------------------------------------------------
/*
 The existing unit tests for the `CC_parseCmdLineArgs` function are:

1. NullCmdLineArgs: Tests the function with argc as 0 and argv as NULL. (Typical)
2. NullCmdLineArgsPtr: Tests the function with argc as 0, argv as NULL, and pCmdLineArgs as NULL. (Boundary)
3. NoArgs: Tests the function with no command line arguments. (Typical)
4. LoggingEnabled: Tests the function with the logging enabled argument -l. (Typical)
5. RecvPort: Tests the function with the receive port argument -p and a value. (Typical)
6. LogSavingDir: Tests the function with the log saving directory argument -d and a value. (Typical)
7. InvalidArgs: Tests the function with invalid arguments that do not start with -. (Misuse)
8. MissingValueForPort: Tests the function with the -p argument but without a value following it. (Boundary)
9. MissingValueForDir: Tests the function with the -d argument but without a value following it. (Boundary)
10. NonNumericPort: Tests the function with a non-numeric value for the -p argument. (Misuse)
11. MultipleSameArgs: Tests the function with multiple instances of the same argument. (Misuse)
12. ArgsInDifferentOrder: Tests the function with all possible arguments in a different order. (Typical)

The missing unit tests could be:

1. AllArgs: Tests the function with all possible arguments. (Typical)
2. InvalidPort: Tests the function with an invalid port number
    (e.g., negative, zero, or greater than 65535). (Boundary)
3. InvalidDir: Tests the function with an invalid directory
    (e.g., a directory that does not exist or cannot be accessed).(Boundary)
4. NoValueAfterFlag: Tests the function with a flag (e.g., -p or -d) that is the last argument,
    i.e., there is no value after the flag. (Boundary)
5. UnexpectedArgAfterFlag: Tests the function with an unexpected argument after a flag
    (e.g., another flag instead of a value).(Misuse)
6. NullArgv: Tests the function with a NULL argv, but argc is not 0. (Fault)
7. Performance: Tests the function's performance by parsing a large number of arguments. (Performance)
8. Concurrency: Tests the function's behavior when called concurrently from multiple threads. (Concurrency)
*/

// 1. AllArgs
TEST(CC_parseCmdLineArgsTest, AllArgs) {
  // Setup
  int argc                  = 5;
  const char* argv[]        = {"program", "-l", "-p", "8080", "-d", "/tmp/logs"};
  CC_CmdLineArgs_T expected = {true, 8080, "/tmp/logs"};

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_EQ(result, 0);
  // ASSERT_EQ(actual, expected);
  ASSERT_EQ(actual.IsLoggingEnabled, expected.IsLoggingEnabled);
  ASSERT_EQ(actual.RecvPort, expected.RecvPort);
  ASSERT_STREQ(actual.pLogSavingDir, expected.pLogSavingDir);
}

// 2. InvalidPort
TEST(CC_parseCmdLineArgsTest, InvalidPort) {
  // Setup
  int argc           = 3;
  const char* argv[] = {"program", "-p", "70000"};

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_NE(result, 0);
}

// 3. InvalidDir
TEST(CC_parseCmdLineArgsTest, InvalidDir) {
  // Setup
  int argc           = 3;
  const char* argv[] = {"program", "-d", "/non/existent/directory"};

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_NE(result, 0);
}

// 4. NoValueAfterFlag
TEST(CC_parseCmdLineArgsTest, NoValueAfterFlag) {
  // Setup
  int argc           = 2;
  const char* argv[] = {"program", "-p"};

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_NE(result, 0);
}

// 5. UnexpectedArgAfterFlag
TEST(CC_parseCmdLineArgsTest, UnexpectedArgAfterFlag) {
  // Setup
  int argc           = 3;
  const char* argv[] = {"program", "-p", "-d"};

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_NE(result, 0);
}

// 6. NullArgv
TEST(CC_parseCmdLineArgsTest, NullArgv) {
  // Setup
  int argc          = 1;
  const char** argv = NULL;

  // Exercise
  CC_CmdLineArgs_T actual;
  int result = CC_parseCmdLineArgs(argc, argv, &actual);

  // Verify
  ASSERT_NE(result, 0);
}

// 7. Performance
TEST(CC_parseCmdLineArgsTest, Performance) {
  // Setup
  int argc = 10000;
  const char* argv[argc];
  for (int i = 0; i < argc; i++) {
    argv[i] = "arg";
  }

  // Exercise
  CC_CmdLineArgs_T actual;
  auto start = std::chrono::high_resolution_clock::now();
  int result = CC_parseCmdLineArgs(argc, argv, &actual);
  auto end   = std::chrono::high_resolution_clock::now();

  // Verify
  ASSERT_EQ(result, 0);
  std::cout << "Time taken: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << "ms\n";
}

#if 0
// 8. Concurrency
TEST(CC_parseCmdLineArgsTest, Concurrency) {
  // Setup
  int argc           = 3;
  const char* argv[] = {"program", "-p", "8080"};

  // Exercise
  std::vector<std::thread> threads;
  for (int i = 0; i < 10; i++) {
    threads.push_back(std::thread([argc, argv]() {
      CC_CmdLineArgs_T actual;
      int result = CC_parseCmdLineArgs(argc, argv, &actual);
      ASSERT_EQ(result, 0);
    }));
  }

  // Wait for all threads to finish
  for (auto& t : threads) {
    t.join();
  }
}
#endif
