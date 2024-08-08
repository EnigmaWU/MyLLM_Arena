//[FROM] <<Clean Code>> by Robert C. Martin (Chapter 14: Successive Refinement)
// Code written by EnigmaWU
#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  CC_SUCCESS = 0,
  CC_FAIL    = 1,
} CC_Result_T;

#include <stdbool.h>  // Include the necessary header file for the bool type

typedef struct {
  bool IsLoggingEnabled;  //-l
  int RecvPort;           //-p <port>
  const char *pLogSavingDir;  //-d <dir>
} CC_CmdLineArgs_T;

/**
 * @brief: Use CC_parseCmdLineArgs to parse command line arguments and save them in CC_CmdLingArgs_T.
 *
 * @param argc same as main
 * @param argv same as main
 * @param pCmdLineArgs pointer to CC_CmdLineArgs_T
 * @return CC_SUCCESS if successful, CC_FAIL otherwise in CC_Result_T
 */
CC_Result_T CC_parseCmdLineArgs(int argc, const char *argv[], CC_CmdLineArgs_T *pCmdLineArgs);

#ifdef __cplusplus
}
#endif