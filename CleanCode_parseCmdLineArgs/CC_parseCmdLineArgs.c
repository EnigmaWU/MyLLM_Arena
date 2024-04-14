#include "CC_parseCmdLineArgs.h"

#include <stddef.h>  // Include the header file that defines the NULL macro
#include <stdlib.h>

// ImplV1: Use Copilot to generate code to pass the test in CC_parseCmdLineArgsTest_byCopilot.cxx
CC_Result_T CC_parseCmdLineArgs(int argc, char *argv[], CC_CmdLineArgs_T *pCmdLineArgs) {
  // If argc is 0 or argv is null, return fail
  if (argc == 0 || argv == NULL) {
    return CC_FAIL;
  }

  // If pCmdLineArgs is null, return fail
  if (pCmdLineArgs == NULL) {
    return CC_FAIL;
  }

  // Initialize to default values
  pCmdLineArgs->IsLoggingEnabled = false;
  pCmdLineArgs->RecvPort         = 0;
  pCmdLineArgs->pLogSavingDir    = NULL;

  // Parse the arguments
  for (int i = 1; i < argc; i++) {
    if (argv[i][0] != '-') {
      return CC_FAIL;
    }

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

  return CC_SUCCESS;
}