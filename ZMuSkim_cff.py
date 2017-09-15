import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.MagneticField_cff import *
### HLT filter
import copy
from HLTrigger.HLTfilters.hltHighLevel_cfi import *
from  SimGeneral.HepPDTESSource.pythiapdt_cfi import *
from TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi import *
from TrackingTools.TrackAssociator.DetIdAssociatorESProducer_cff import *
#from PhysicsTools.RecoAlgos.highPtTracks_cfi import *
from RecoMuon.MuonIsolationProducers.isoDepositProducerIOBlocks_cff import *
#from RecoMuon.MuonIsolationProducers.trackExtractorBlocks_cff import *
from RecoMuon.MuonIsolationProducers.trackExtractorBlocks_cff import MIsoTrackExtractorBlock
from PhysicsTools.PatAlgos.producersLayer1.genericParticleProducer_cfi import patGenericParticles
#from PhysicsTools.PatAlgos.patTemplate_cfg import *
#process.load("PhysicsTools.PatAlgos.producersLayer1.muonProducer_cff")
#patAlgosToolsTask.add(process.makePatMuonsTask)

ZMuHLTFilter = copy.deepcopy(hltHighLevel)
ZMuHLTFilter.throw = cms.bool(False)
ZMuHLTFilter.HLTPaths = ["HLT_Mu*","HLT_IsoMu*","HLT_DoubleMu*"]


### Z -> MuMu candidates
# Get muons of needed quality for Zs

###create a track collection with generic kinematic cuts
looseMuonsForZMuSkim = cms.EDFilter("TrackSelector",
                             src = cms.InputTag("generalTracks"),
                             cut = cms.string('pt > 10 &&  abs(eta)<2.4 &&  (charge!=0)'),
                             filter = cms.bool(True)                                
                             )



###cloning the previous collection into a collection of candidates
ConcretelooseMuonsForZMuSkim = cms.EDProducer("ConcreteChargedCandidateProducer",
                                              src = cms.InputTag("looseMuonsForZMuSkim"),
                                              particleType = cms.string("mu+")
                                              #particleMass = cms.double(0.106)
                                              #particleId = cms.int32(13)
                                              )



###create iso deposits
tkIsoDepositTk = cms.EDProducer("CandIsoDepositProducer",
                                src = cms.InputTag("ConcretelooseMuonsForZMuSkim"),
                                MultipleDepositsFlag = cms.bool(False),
                                trackType = cms.string('candidate'),
                                ExtractorPSet = cms.PSet(
        #MIsoTrackExtractorBlock
        Diff_z = cms.double(0.2),
        inputTrackCollection = cms.InputTag("generalTracks"),
        BeamSpotLabel = cms.InputTag("offlineBeamSpot"),
        ComponentName = cms.string('TrackExtractor'),
        DR_Max = cms.double(0.5),
        Diff_r = cms.double(0.1),
        Chi2Prob_Min = cms.double(-1.0),
        DR_Veto = cms.double(0.01),
        NHits_Min = cms.uint32(0),
        Chi2Ndof_Max = cms.double(1e+64),
        Pt_Min = cms.double(-1.0),
        DepositLabel = cms.untracked.string('tracker'),
        BeamlineOption = cms.string('BeamSpotFromEvent')
        )
                                )

###adding isodeposits to candidate collection
allPatTracks = patGenericParticles.clone(
    src = cms.InputTag("ConcretelooseMuonsForZMuSkim"),
    # isolation configurables
    userIsolation = cms.PSet(
      tracker = cms.PSet(
        veto = cms.double(0.015),
        src = cms.InputTag("tkIsoDepositTk"),
        deltaR = cms.double(0.3),
        #threshold = cms.double(1.5)
      ),
      ),
    isoDeposits = cms.PSet(
      tracker = cms.InputTag("tkIsoDepositTk"),
    ),
)



#tkIsolationLabels = cms.InputTag(cms.InputTag("tkIsoDepositTk"))
#TrackIsolations = cms.EDFilter("MultipleIsoDepositsToValueMaps",
#                               collection   = cms.InputTag("ConcretelooseMuonsForZMuSkim"),
#                               associations = cms.InputTag("tkIsoDepositTk")
#                               )

###create the "probe collection" of isolated tracks 
looseIsoMuonsForZMuSkim = cms.EDFilter("CandViewSelector",
                             #src = cms.InputTag("ConcretelooseMuonsForZMuSkim"),
                             src = cms.InputTag("allPatTracks"), 
                             cut = cms.string('(trackIso/pt)<0.4'),
                             filter = cms.bool(True)
                             )





MyPatMuons = cms.EDProducer("PATMuonProducer",
    muonSource      = cms.InputTag("muons"),
    useParticleFlow =  cms.bool( False ),
    pfMuonSource = cms.InputTag("particleFlow"),
    embedMuonBestTrack = cms.bool(True), 
    embedTunePMuonBestTrack = cms.bool(True),
    forceBestTrackEmbedding = cms.bool(True),
    embedTrack          = cms.bool(True), ## embed in AOD externally stored tracker track
    embedCombinedMuon   = cms.bool(True),  ## embed in AOD externally stored combined muon track
    embedStandAloneMuon = cms.bool(True),  ## embed in AOD externally stored standalone muon track
    embedPickyMuon      = cms.bool(True),  ## embed in AOD externally stored TeV-refit picky muon track
    embedTpfmsMuon      = cms.bool(True),  ## embed in AOD externally stored TeV-refit TPFMS muon track
    embedDytMuon        = cms.bool(True),  ## embed in AOD externally stored TeV-refit DYT muon track
    embedPFCandidate = cms.bool(False), ## embed in AOD externally stored particle flow candidate
    embedCaloMETMuonCorrs = cms.bool(False),
    caloMETMuonCorrs = cms.InputTag("muonMETValueMapProducer"  , "muCorrData"),
    # embedding of muon MET corrections for tcMET
    embedTcMETMuonCorrs   = cms.bool(False), # removed from RECO/AOD!
    tcMETMuonCorrs   = cms.InputTag("muonTCMETValueMapProducer", "muCorrData"),
    embedPfEcalEnergy = cms.bool(False),
    addPuppiIsolation = cms.bool(False),
    addGenMatch   = cms.bool(False),
    embedGenMatch = cms.bool(False),

    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),

    # resolution configurables
    addResolutions  = cms.bool(False),
    resolutions = cms.PSet(),
    # high level selections                                                                                       
    embedHighLevelSelection = cms.bool(True),
    beamLineSrc             = cms.InputTag("offlineBeamSpot"),
    pvSrc                   = cms.InputTag("offlinePrimaryVertices"),

    computeMiniIso = cms.bool(False),
    pfCandsForMiniIso = cms.InputTag("packedPFCandidates"),
    miniIsoParams = cms.vdouble(0.05, 0.2, 10.0, 0.5, 0.0001, 0.01, 0.01, 0.01, 0.0),
)

selectedVertices = cms.EDFilter("VertexSelector",
                                src = cms.InputTag('offlinePrimaryVertices'),
                                cut = cms.string("isValid & ndof >= 4 & chi2 > 0 & tracksSize > 0 & abs(z) < 24 & abs(position.Rho) < 2."),
                                filter = cms.bool(False)
)

selectedFirstPrimaryVertex = cms.EDFilter("PATSingleVertexSelector",
                                          mode = cms.string('firstVertex'),
                                          vertices = cms.InputTag('selectedVertices'),
                                          filter = cms.bool(False)
)

tightMuonsForZMuSkim = cms.EDFilter("PATMuonSelector",
                                    src = cms.InputTag("MyPatMuons"),       
                                    #cut = cms.string('pt > 25 &&  abs(eta)<2.4 && isGlobalMuon = 1 && isTrackerMuon = 1 && abs(innerTrack().dxy)<2.0 && (globalTrack().normalizedChi2() < 10) && (innerTrack().hitPattern().numberOfValidHits() > 10) && (isolationR03().sumPt/pt)<0.4'),
                                    cut = cms.string('(pt > 28) &&  (abs(eta)<2.4) && (isPFMuon>0) && (isGlobalMuon = 1) && (isTrackerMuon=1) && (globalTrack().normalizedChi2() < 10) && (globalTrack().hitPattern().numberOfValidMuonHits())&& (numberOfMatchedStations() > 1)&& (innerTrack().hitPattern().numberOfValidPixelHits() > 0)&& (innerTrack().hitPattern().trackerLayersWithMeasurement() > 5) && (abs(dB)<0.2) && (abs(muonBestTrack().dz)<3) && ((isolationR03().sumPt/pt)<0.4)'),
                                    filter = cms.bool(True)                                
                                    )

#tightMuonsForZMuSkim = cms.EDFilter("PATMuonSelector",
#                                    src = cms.InputTag("MyPatMuons"), 
#                                    cut = cms.string('pt > 28 &&  abs(eta)<2.4 && (muonID(isTightMuon)) && (isolationR03().sumPt/pt)<0.4)'),
#                                    filter = cms.bool(True)                                                         
#)


                                    
# build Z-> MuMu candidates
#dimuonsZMuSkim = cms.EDProducer("CandViewShallowCloneCombiner",
#                         checkCharge = cms.bool(False),
#                         #cut = cms.string('mass > 60 && mass < 120 && charge=0'),
#                         cut = cms.string('mass > 60 &&  charge=0'),
#                         deltaRMin = cms.double(0.3),
#                         decay = cms.string("tightMuonsForZMuSkim looseIsoMuonsForZMuSkim")
#                         )


dimuonsZMuSkim = cms.EDProducer("DeltaRMinCandCombiner",
    decay = cms.string('tightMuonsForZMuSkim looseIsoMuonsForZMuSkim'),
    checkCharge = cms.bool(False),
    cut = cms.string('mass > 60 &&  charge=0 && (abs(daughter(0).vz - daughter(1).vz) < 4)'),
    deltaRMin = cms.double(0.3)
)


# Z filter
dimuonsFilterZMuSkim = cms.EDFilter("CandViewCountFilter",
                             src = cms.InputTag("dimuonsZMuSkim"),
                             minNumber = cms.uint32(1)
                             )


InitialPlots = cms.EDAnalyzer('RecoMuonAnalyzer',
                                   muonsInputTag = cms.InputTag("muons"),)
PlotsAfterTrigger = cms.EDAnalyzer('RecoMuonAnalyzer',
                                   muonsInputTag = cms.InputTag("muons"),)
PlotsAfterLooseMuon = cms.EDAnalyzer('RecoMuonAnalyzer',
                                   muonsInputTag = cms.InputTag("muons"),)
PlotsAfterTightMuon = cms.EDAnalyzer('RecoMuonAnalyzer',
                                   muonsInputTag = cms.InputTag("muons"),)
PlotsAfterDiMuon = cms.EDAnalyzer('RecoMuonAnalyzer',
                                   muonsInputTag = cms.InputTag("muons"),)                                   
TFileService = cms.Service("TFileService",
                                   fileName = cms.string("histoSingleMu_skim.root")
                                   )

TrackHistosBeforeLooseMuon = cms.EDAnalyzer("CandViewHistoAnalyzer",
                                            src = cms.InputTag("allPatTracks"),
                                            histograms = cms.VPSet(
        cms.PSet(
            min = cms.untracked.double(0.0),
            max = cms.untracked.double(200.0),
            nbins = cms.untracked.int32(200),
            description = cms.untracked.string('muon transverse momentum [GeV]'),
            name = cms.untracked.string('trackPt'),
            plotquantity = cms.untracked.string('pt'),
            ),
)
)
TrackHistosAfterLooseMuon = cms.EDAnalyzer("CandViewHistoAnalyzer",
                                            src = cms.InputTag("looseIsoMuonsForZMuSkim"),
                                            histograms = cms.VPSet(
        cms.PSet(
            min = cms.untracked.double(0.0),
            max = cms.untracked.double(200.0),
            nbins = cms.untracked.int32(200),
            description = cms.untracked.string('muon transverse momentum [GeV]'),
            name = cms.untracked.string('trackPt'),
            plotquantity = cms.untracked.string('pt'),
            ),
       # cms.PSet(
       #     min = cms.untracked.double(0.0),
       #     max = cms.untracked.double(50.0),
       #     nbins = cms.untracked.int32(200),
       #     description = cms.untracked.string('track iso'),
       #     name = cms.untracked.string('trackIso'),
       #     plotquantity = cms.untracked.string('userIso'),
            #plotquantity = cms.untracked.string('trackIso'),
       #     ),
)
)


# Z Skim sequence
diMuonSelSeq = cms.Sequence(
                            InitialPlots *
                            ZMuHLTFilter *
                            PlotsAfterTrigger *
                            #selectedVertices *
                            #selectedFirstPrimaryVertex *
                            looseMuonsForZMuSkim *
                            ConcretelooseMuonsForZMuSkim *
                            tkIsoDepositTk *
                            allPatTracks *
                            TrackHistosBeforeLooseMuon *
                            #tkIsolationLabels *
                            #TrackIsolations * 
                            looseIsoMuonsForZMuSkim * 
                            PlotsAfterLooseMuon *
                            TrackHistosAfterLooseMuon *
                            MyPatMuons *
                            tightMuonsForZMuSkim *
                            PlotsAfterTightMuon *
                            dimuonsZMuSkim *
                            dimuonsFilterZMuSkim *
                            PlotsAfterDiMuon
                            )
