from pcraster import *
from pcraster.framework import *

class LandUse(DynamicModel, MonteCarloModel):
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self) 
    setclone('LandUses.map')

  def premcloop(self):
    self.landUse = self.readmap('LandUses')
    
  def initial(self):
    self.population = self.readmap('../../src/populationMap')
    self.jobs = self.readmap('../../src/jobsMap')

  def dynamic(self):
    self.population = self.population * 2
    self.jobs = self.jobs * 2

    self.report(self.population, 'pop')
    self.report(self.jobs, 'jobs')

  def postmcloop(self):
##    names = ['p','snow','q']
##    sampleNumbers = range(1,13)
##    timeSteps = range(1,182)
##    #percentiles = [0.025,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.975]
##    percentiles=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
##    mcaveragevariance(names,sampleNumbers,timeSteps)
##    mcpercentiles(names,percentiles,sampleNumbers,timeSteps)
    pass

#nrOfTimeSteps=181
nrOfTimeSteps=10
#nrOfSamples=50
nrOfSamples=5
myModel = LandUse()
dynamicModel = DynamicFramework(myModel, nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel, nrOfSamples)
# dynamicModel.run()
mcModel.run()
