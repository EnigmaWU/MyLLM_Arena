#include <gtest/gtest.h>

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