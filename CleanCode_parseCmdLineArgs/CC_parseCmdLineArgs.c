#include "CC_parseCmdLineArgs.h"

#include <stddef.h>  // Include the header file that defines the NULL macro
#include <stdlib.h>

// ImplV1: Use Copilot to generate code to pass the test in CC_parseCmdLineArgsTest_byCopilot.cxx
CC_Result_T CC_parseCmdLineArgs(int argc, char *argv[], CC_CmdLineArgs_T *pCmdLineArgs) {
  // Initialize to default values
  pCmdLineArgs->IsLoggingEnabled = false;
  pCmdLineArgs->RecvPort         = 0;
  pCmdLineArgs->pLogSavingDir    = NULL;

  // If there are no arguments (except for the program name), return success
  if (argc == 1) {
    return CC_SUCCESS;
  }

  // If there are not enough arguments, return fail
  if (argc < 7) {
    return CC_FAIL;
  }

  // Parse the arguments
  for (int i = 1; i < argc; i++) {
    if (argv[i][0] == '-') {
      switch (argv[i][1]) {
        case 'l':
          pCmdLineArgs->IsLoggingEnabled = true;
          break;
        case 'p':
          if (i + 1 < argc) {
            pCmdLineArgs->RecvPort = atoi(argv[i + 1]);
            i++;
          } else {
            return CC_FAIL;
          }
          break;
        case 'd':
          if (i + 1 < argc) {
            pCmdLineArgs->pLogSavingDir = argv[i + 1];
            i++;
          } else {
            return CC_FAIL;
          }
          break;
        default:
          return CC_FAIL;
      }
    }
  }

  return CC_SUCCESS;
}