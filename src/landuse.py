from pcraster import *
from pcraster.framework import *

class LandUse(DynamicModel, MonteCarloModel):
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self) 
    setclone('LandUses.map')

  def premcloop(self):
    self.landUse = self.readmap('LandUses')
    self.population = self.readmap('populationMap')
    self.jobs = self.readmap('jobsMap')
    
  def initial(self):
    #Creating basic land use map using the probabilities of the file LandUse, under a uniform distribution
    uni=uniform(1)
    landUses=lookupnominal('LandUses.tbl', uni)
    self.report(landUses, 'LandUses')
    
    #Defining Boleean Maps
    
    residential = landUses == 3
    
    industrial = landUses == 2
    
    agricultural = landUses == 1
   
    natural= landUses == 4

    self.population = ifthenelse(residential, scalar(1), 0)
    #popArea = maptotal(populationMap) #sum the total population
    #self.report(popArea, 'popArea') 
    
    self.jobs = ifthenelse(industrial, scalar(1), 0)
    #jobArea = maptotal(jobsMap) #sum the total jobs
    #self.report(jobArea, 'jobArea')
    
    self.report(self.population, 'population')
    self.report(self.jobs, 'jobs')

    
    x_activity_amount = self.population + self.jobs + ifthenelse(self.landUse == 1, scalar(1), 0)
  
  def dynamic(self):
    x_activity_amount = self.population + self.jobs + ifthenelse(self.landUse == 1, scalar(1), 0)
    #w_weight_atract_repulsion = 
    
    potential = x_activity_amount

    self.report(x_activity_amount, 'x')
    self.report(potential, 'potent')
    
    self.report(self.population, 'pop')
    self.report(self.jobs, 'jobs')

    isPopulation = self.population > 0
    isJobs = self.jobs > 0

    areaPop = windowtotal(scalar(isPopulation),3)
    self.report(areaPop, 'areaPop')

    weightPop = ifthenelse(isPopulation, areaPop, 0)
    self.report(weightPop, 'w3Pop')

    pop_to_jobs = isPopulation & isJobs #each cell has jobs and population activity
    pop_to_jobs = scalar(pop_to_jobs)

    self.report(pop_to_jobs, 'popjobs')

    #increase activities
    self.population = self.population * 2
    self.jobs = self.jobs * 2

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
