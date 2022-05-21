void runAnalysis()
{
  // header location
  gInterpreter->ProcessLine(".include $ROOTSYS/include");
  gInterpreter->ProcessLine(".include $ALICE_ROOT/include");

  // create the analysis manager
  AliAnalysisManager *mgr = new AliAnalysisManager("AnalysisMyTask");
  AliAODInputHandler *aodH = new AliAODInputHandler();
  mgr->SetInputEventHandler(aodH);

  // Dependencies
  // ImproverITS - $ALICE_PHYSICS/PWGHF/vertexingHF/macros/AddTaskImproveITSCVMFS.C
  // #Module.MacroArgs    kFALSE,"","",0
  gInterpreter->ExecuteMacro("$ALICE_PHYSICS/OADB/macros/AddTaskPhysicsSelection.C(1,1)");
  gInterpreter->ExecuteMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C(1)");

  // load the addtask macro and create the task
  // AliAnalysisTaskMyTask *task = reinterpret_cast<AliAnalysisTaskMyTask*>(gInterpreter->ExecuteMacro("AddMyTask.C"));
  AliAnalysisTaskSEHFTreeCreator*  __R_ADDTASK__ = reinterpret_cast<AliAnalysisTaskSEHFTreeCreator*>(gInterpreter->ExecuteMacro("$ALICE_PHYSICS/PWGHF/treeHF/macros/AddTaskHFTreeCreator.C(1, 0, \"HFTreeCreator_pp_kAny\", \"D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root\", 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 9, 1, 0, 0, 0, 0)"));
  //auto task = AddTaskHFTreeCreator(kTRUE, 0, "HFTreeCreator_pp_kAny", "D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root", 0, kTRUE, kTRUE, 1, 1, 0, 0, 0, 1, 0, 0, 0, AliHFTreeHandler::kNsigmaDetAndCombPID, AliHFTreeHandler::kRedSingleTrackVars, kFALSE, kFALSE, 0, kFALSE);
  // 1, 0, \"HFTreeCreator_pp_kAny\", \"D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root\", 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 9, 1, 0, 0, 0, 0
  __R_ADDTASK__->SelectCollisionCandidates(AliVEvent::kINT7);
  __R_ADDTASK__->SetFillJets(kTRUE);
  __R_ADDTASK__->SetDoJetSubstructure(kTRUE);
  __R_ADDTASK__->SetJetSubRadius(0.);
  __R_ADDTASK__->SetSoftDropZCut(0.1);
  __R_ADDTASK__->SetSoftDropBeta(0.);

  // if you want to run locally, we need to define some input
  TChain *chain = new TChain("aodTree");
  chain->Add("286350/0002/AliAOD.root");

  TChain *vtxHF = new TChain("aodTree");
  vtxHF->Add("286350/0002/AliAOD.VertexingHF.root");
  chain->AddFriend(vtxHF);

  // start the analysis locally
  mgr->InitAnalysis();
  mgr->StartAnalysis("local", chain);
}