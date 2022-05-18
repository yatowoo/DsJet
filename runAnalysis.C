void runAnalysis()
{
  // header location
  gInterpreter->ProcessLine(".include $ROOTSYS/include");
  gInterpreter->ProcessLine(".include $ALICE_ROOT/include");

  // create the analysis manager
  AliAnalysisManager *mgr = new AliAnalysisManager("AnalysisMyTask");
  AliAODInputHandler *aodH = new AliAODInputHandler();
  mgr->SetInputEventHandler(aodH);

  // load the addtask macro and create the task
  auto taskMacro = TString("/PWGHF/treeHF/macros/AddTaskHFTreeCreator.C");
  taskMacro = gSystem->Getenv("ALICE_PHYSICS") + taskMacro;
  gInterpreter->ProcessLine(".L " + taskMacro);

  auto task = AddTaskHFTreeCreator(kTRUE, 0, "HFTreeCreator_pp_kAny", "D0DsDplusDstarLcBplusBsLbCuts_pp_kAny.root", 0, kTRUE, kTRUE, 1, 1, 0, 0, 0, 1, 0, 0, 0, AliHFTreeHandler::kNsigmaDetAndCombPID, AliHFTreeHandler::kRedSingleTrackVars, kFALSE, kFALSE, 0, kFALSE);

  // if you want to run locally, we need to define some input
  TChain *chain = new TChain("aodTree");
  chain->Add("AliAOD.root");

  TChain *vtxHF = new TChain("aodTree");
  vtxHF->Add("AliAOD.VertexingHF.root");
  chain->AddFriend(vtxHF);

  // start the analysis locally
  mgr->InitAnalysis();
  mgr->StartAnalysis("local", chain);

  auto aod = (AliAODEvent*)(task->InputEvent());
  auto mcarray = (TClonesArray*)aod->GetList()->FindObject(AliAODMCParticle::StdBranchName());
  auto candarray = (TClonesArray*)aod->GetList()->FindObject("Charm3Prong");
  
  auto mcpar = (AliAODMCParticle*)(mcarray->UncheckedAt(367));
}