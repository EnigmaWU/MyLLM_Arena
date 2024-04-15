#include <gtest/gtest.h>

#include "CC_parseCmdLineArgs.h"

// Chat with Copilot, Q by EnigmaWU:
// #file:CC_parseCmdLineArgs.c #file:CC_parseCmdLineArgsTest_byCopilot.cxx
//      what UT already written and what UT is missed?
// A from Copilot:
/**
The unit tests that are already written for the CC_parseCmdLineArgs function
    in the CC_parseCmdLineArgsTest_byCopilot.cxx file are:

NullCmdLineArgs: Tests the function with argc as 0 and argv as NULL.
NullCmdLineArgsPtr: Tests the function with argc as 0, argv as NULL, and pCmdLineArgs as NULL.
NoArgs: Tests the function with no command line arguments.
LoggingEnabled: Tests the function with the logging enabled argument -l.
RecvPort: Tests the function with the receive port argument -p and a value.
LogSavingDir: Tests the function with the log saving directory argument -d and a value.
AllArgs: Tests the function with all possible arguments.


The unit tests that are missing could be:

InvalidArgs: Tests the function with invalid arguments that do not start with -.
MissingValueForPort: Tests the function with the -p argument but without a value following it.
MissingValueForDir: Tests the function with the -d argument but without a value following it.
NonNumericPort: Tests the function with a non-numeric value for the -p argument.
MultipleSameArgs: Tests the function with multiple instances of the same argument.
ArgsInDifferentOrder: Tests the function with all possible arguments in a different order.
 **/

// Q by EnigmaWU: generate could missing ut code for me
// A from Copilot:
// TEST(CC_parseCmdLineArgs, LogSavingDir) {
//   CC_CmdLineArgs_T CmdLineArgs;
//   char *argv[] = {(char *)"test", (char *)"-d", (char *)"/path/to/log"};
//   EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(3, argv, &CmdLineArgs));
//   EXPECT_FALSE(CmdLineArgs.IsLoggingEnabled);
//   EXPECT_EQ(0, CmdLineArgs.RecvPort);
//   EXPECT_STREQ("/path/to/log", CmdLineArgs.pLogSavingDir);
// }

TEST(CC_parseCmdLineArgs, InvalidArgs) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"invalid"};
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(2, argv, &CmdLineArgs));
}

TEST(CC_parseCmdLineArgs, MissingValueForPort) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"-p"};
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(2, argv, &CmdLineArgs));
}

TEST(CC_parseCmdLineArgs, MissingValueForDir) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"-d"};
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(2, argv, &CmdLineArgs));
}

TEST(CC_parseCmdLineArgs, NonNumericPort) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"-p", (char *)"nonnumeric"};
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(3, argv, &CmdLineArgs));
}

TEST(CC_parseCmdLineArgs, MultipleSameArgs) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"-l", (char *)"-l"};
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(3, argv, &CmdLineArgs));
  EXPECT_TRUE(CmdLineArgs.IsLoggingEnabled);
}

TEST(CC_parseCmdLineArgs, ArgsInDifferentOrder) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = {(char *)"test", (char *)"-p", (char *)"1234", (char *)"-l", (char *)"-d", (char *)"/path/to/log"};
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(6, argv, &CmdLineArgs));
  EXPECT_TRUE(CmdLineArgs.IsLoggingEnabled);
  EXPECT_EQ(1234, CmdLineArgs.RecvPort);
  EXPECT_STREQ("/path/to/log", CmdLineArgs.pLogSavingDir);
}