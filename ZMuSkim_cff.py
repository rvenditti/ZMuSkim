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



tightMuonsForZMuSkim = cms.EDFilter("MuonSelector",
                                    src = cms.InputTag("muons"),       
                                    #cut = cms.string('pt > 25 &&  abs(eta)<2.4 && isGlobalMuon = 1 && isTrackerMuon = 1 && abs(innerTrack().dxy)<2.0 && (globalTrack().normalizedChi2() < 10) && (innerTrack().hitPattern().numberOfValidHits() > 10) && (isolationR03().sumPt/pt)<0.4'),
                                    cut = cms.string('(pt > 28) &&  (abs(eta)<2.4) && (isPFMuon>0) && (isGlobalMuon = 1) && (isTrackerMuon=1) && (globalTrack().normalizedChi2() < 10) && (globalTrack().hitPattern().numberOfValidMuonHits())&& (numberOfMatchedStations() > 1)&& (innerTrack().hitPattern().numberOfValidPixelHits() > 0)&& (innerTrack().hitPattern().trackerLayersWithMeasurement() > 5) &&  (abs(muonBestTrack().dxy)<1) && (abs(muonBestTrack().dz)<3) && ((isolationR03().sumPt/pt)<0.4)'),
                                    filter = cms.bool(True)                                
                                    )

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
    cut = cms.string('mass > 60 &&  charge=0'),
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
                            tightMuonsForZMuSkim *
                            PlotsAfterTightMuon *
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
                            dimuonsZMuSkim *
                            dimuonsFilterZMuSkim *
                            PlotsAfterDiMuon
                            )
