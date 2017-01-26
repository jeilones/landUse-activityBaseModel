from pcraster import *
from pcraster.framework import *

class MyFirstModel(DynamicModel, MonteCarloModel):
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self) 
    setclone('../resources/dem.map')

  def premcloop(self):
    dem = self.readmap('../resources/dem')
    elevationMeteoStation = 2058.1
    self.elevationAboveMeteoStation = dem - elevationMeteoStation
    self.ldd=lddcreate(dem,1e31,1e31,1e31,1e31)
    self.report(self.ldd,'../resources/ldd')

  def initial(self):
    #self.temperatureLapseRate = 0.005
    #self.temperatureCorrection = self.elevationAboveMeteoStation * self.temperatureLapseRate
    #self.report(self.temperatureCorrection,'../resources/tempCor')

    self.snow=0.0
    
    
  def dynamic(self):
    #error = max(1 + mapnormal() / 10, 0.2)
    error = mapnormal() * sqrt(0.04) + 1.0
    precipitationObs = timeinputscalar('../resources/precip.tss',1)
    precipitation = precipitationObs * error
    
    self.report(precipitation,'p')

    #self.temperatureLapseRate = max(0.005 + mapnormal() / 10, 0.001)
    self.temperatureLapseRate = mapnormal() * sqrt(0.000001) + 0.005
    self.temperatureCorrection = self.temperatureLapseRate * self.elevationAboveMeteoStation
    self.report(self.temperatureCorrection,'tempCor')
    
    temperatureObserved = timeinputscalar('../resources/temp.tss',1)
    temperature= temperatureObserved - self.temperatureCorrection
    self.report(temperature,'temp')

    freezing=temperature < 0.0
    snowFall=ifthenelse(freezing,precipitation,0.0)
    rainFall=ifthenelse(pcrnot(freezing),precipitation,0.0)

    self.snow = self.snow+snowFall

    potentialMelt = ifthenelse(pcrnot(freezing),temperature*0.01,0)
    actualMelt = min(self.snow, potentialMelt)

    self.snow = self.snow - actualMelt
    self.report(self.snow,'snow')

    runoffGenerated = actualMelt + rainFall

    discharge=accuflux(self.ldd,runoffGenerated*cellarea())
    self.report(discharge,'q')

  def postmcloop(self):
    names = ['p','snow','q']
    sampleNumbers = range(1,5)
    timeSteps = range(1,10)
    #percentiles = [0.025,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.975]
    percentiles=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    mcaveragevariance(names,sampleNumbers,timeSteps)
    mcpercentiles(names,percentiles,sampleNumbers,timeSteps)

nrOfTimeSteps=10
nrOfSamples=5
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel, nrOfSamples)
# dynamicModel.run()
mcModel.run()
