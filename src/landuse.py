from pcraster import *
from pcraster.framework import *

class LandUse(DynamicModel, MonteCarloModel):
  
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self) 
    setclone('LandUses.map')

  def premcloop(self):
    #self.landUse = self.readmap('LandUses')
    #self.population = self.readmap('population')
    #self.jobs = self.readmap('jobs')

    self.agricultural = 1
    self.industrial = 2
    self.residential = 3    
    self.natural = 4
    self.maxPopulationPerTimeStep = 600
    self.maxJobsPerTimeStep = 300
    
  def initial(self):
    #Creating basic land use map using the probabilities of the file LandUse, under a uniform distribution
    uni=uniform(1)
    self.landUses = lookupnominal('LandUses.tbl', uni)
    self.report(self.landUses, '')

    isAgricultural = self.landUses == self.agricultural
    self.agriculture = ifthenelse(isAgricultural, scalar(1), 0)

    uni=uniform(1)
    self.population = lookupscalar('Population.tbl', uni)
    self.report(self.population, 'inipop')
    

    uni=uniform(1)
    self.jobs = lookupscalar('Jobs.tbl', uni)
    self.report(self.jobs, 'inijobs')

    self.x_amount_population = scalar(0)
    self.x_amount_jobs = scalar(0)
    self.agriculturePotential = scalar(0)
    
  def dynamic(self):
    #Defining Boleean Maps
    
    isResidential = self.landUses == self.residential
    isIndustrial = self.landUses == self.industrial
    isAgricultural = self.landUses == self.agricultural
    isNatural = self.landUses == self.natural

    #increment of activities
    self.population = self.population + self.x_amount_population
    self.jobs = self.population + self.x_amount_jobs
    self.agriculture = self.agriculture + self.agriculturePotential
    
    isPopulation = self.population > 0
    isJobs = self.jobs > 0

    self.report(self.population, 'pop')
    self.report(self.jobs, 'jobs')
    self.report(isAgricultural, 'agri')
    
    #population weights
    wPopToPop = self.calculateTotalActityWeights(isPopulation, 30, 0.25, 0.001, 0) #population to population
    self.report(wPopToPop, 'wPPT')
    wPopToJob = self.calculateTotalActityWeights(isJobs, 0.1, 0.4, 0, 0) #population to jobs
    self.report(wPopToJob, 'wPJT')
    wPopToAgri = self.calculateTotalActityWeights(isAgricultural, 0, 3, 0.5, 0.25) #population to agricultural
    self.report(wPopToAgri, 'wPAT')
    #end population weights
    #job weigths
    wJobsToPop = self.calculateTotalActityWeights(isPopulation, 0, 0.5, 0, 0) #job to population
    self.report(wJobsToPop, 'wJPT')
    wJobsToJob = self.calculateTotalActityWeights(isJobs, 20, 0.45, 0, 0) #job to jobs
    self.report(wJobsToJob, 'wJJT')
    wJobsToAgri = self.calculateTotalActityWeights(isAgricultural, 0, 2, 0, 0) #job to agricultural
    self.report(wJobsToAgri, 'wJAT')
    #ends job weigths
                                                                                   
    #agriculture weigths
    wAgriToPop = self.calculateTotalActityWeights(isPopulation, 4, 1.5, 0.2, 0.1) #agriculture to population
    self.report(wAgriToPop, 'wAPT')
    wAgriToJob = self.calculateTotalActityWeights(isJobs, 0, 2, 0, 0) #agriculture to jobs
    self.report(wAgriToJob, 'wAJT')
    wAgriToAgri = self.calculateTotalActityWeights(isAgricultural, 300, 5, 0, 0) #agriculture to agriculture
    self.report(wAgriToAgri, 'wAAT')
    #ends agriculture weigths

    ##TOTAL Weights
    wPopulation = wPopToPop + wPopToJob + wPopToAgri
    self.report(wPopulation, 'callPop')
    wJobs = wJobsToPop + wJobsToJob + wJobsToAgri
    self.report(wJobs, 'callJob')
    wAgriculture = wAgriToPop + wAgriToJob + wAgriToAgri
    self.report(wAgriculture, 'callAgri')

    ##POTENTIAL OF POPULATION ACTIVITY
    populationPotential = self.calculatePotential(wPopulation)
    self.x_amount_population = self.maxPopulationPerTimeStep * populationPotential 
    
    self.report(populationPotential, 'popPot')
    self.report(self.x_amount_population, 'x_pop')
    ##END

    ##POTENTIAL OF JOB ACTIVITY
    jobPotential = self.calculatePotential(wJobs)
    self.x_amount_jobs = self.maxJobsPerTimeStep * jobPotential
    ##END POTENTIAL OF JOB ACTIVITY

    ##POTENTIAL OF AGRICULTURE ACTIVITY
    self.agriculturePotential = self.calculatePotential(wAgriculture)
    self.x_amount_agriculture = self.agriculturePotential
    ##END POTENTIAL OF AGRICULTURE ACTIVITY

    ##WRITE NEW LAND USE
    self.landUses = self.newLandUse(self.population, self.jobs, self.agriculture)    
    self.report(self.landUses, 'LandUses')

  def postmcloop(self):
    pass
  
  def calculatePotential(self, activityWeightMap):
    potential = ifthenelse(activityWeightMap > 3, scalar(0.2),
                                     ifthenelse(activityWeightMap > 10, scalar(0.3),
                                                ifthenelse(activityWeightMap > 40, scalar(0.5), 0)))

    return potential

  def calculateTotalActityWeights(self, booleanActivityMap, level0, level1, level2, level3):
    weight0 = ifthenelse(booleanActivityMap, scalar(level0), 0) #weight itself
    weight1 = self.calculateActityWeight(booleanActivityMap, 3, level1)
    weight2 = self.calculateActityWeight(booleanActivityMap, 5, level2)
    weight3 = self.calculateActityWeight(booleanActivityMap, 7, level3)

    return weight0 + weight1 + weight2 + weight3
  
  def calculateActityWeight(self, booleanActivityMap, distance, weight):
    if(weight == 0):
      return scalar(0)
    
    level = distance - 2 # minus 2 cells

    activityWeight = ifthenelse(booleanActivityMap, scalar(weight), 0)
    
    weightLevel = windowtotal(activityWeight, level)
    weightDistance = windowtotal(activityWeight, distance)
    weightMap = weightDistance - weightLevel
    
    return weightMap

  def newLandUse(self, populationActivityAmount, jobsActivityAmount, agricultureActivityAmount):
    thresholdIndustrial = 0.9 * mapmaximum(populationActivityAmount)
    thresholdResidentialMin = 0.7 * mapmaximum(populationActivityAmount)
    thresholdResidentialMax = thresholdIndustrial
    thresholdAgricultureMin = 0.1 * mapmaximum(populationActivityAmount)
    thresholdAgricultureMax = thresholdResidentialMin

    newLandUse = ifthenelse(populationActivityAmount > thresholdIndustrial,
                            nominal(self.industrial),
                            ifthenelse((populationActivityAmount < thresholdResidentialMax) & (populationActivityAmount > thresholdResidentialMin),
                                       nominal(self.residential),
                                       ifthenelse((populationActivityAmount < thresholdAgricultureMax) & (populationActivityAmount > thresholdAgricultureMin),
                                                  nominal(self.agricultural),
                                                  nominal(self.natural)
                                                  )
                                       )
                            )    
    return newLandUse

  def nonNegativePotential(self, maxIncrement,potMap):
    #noZeros = max(scalar(2) ** potMap, 0.0001)
    #self.report(noZeros, 'noZeros')
    #newMap = self.maxPopulationPerTimeStep * (1 ** ln(scalar(1) + potMap))
    newMap =  self.maxPopulationPerTimeStep * uniform(1)
    return newMap

  def diseconomies(self, totalWeights):
    # -1 < y1 < 0
    # y2 > 1
    y1 = 0.1
    y2 = 1.1
    #diseconomies = y1 * totalWeights #** y2
    random = uniform(1)
    diseconomies = totalWeights * ifthenelse(random < 0.5, random * -1, random)
    
    return diseconomies
  
#nrOfTimeSteps=181
nrOfTimeSteps=50
#nrOfSamples=50
nrOfSamples=1
myModel = LandUse()
dynamicModel = DynamicFramework(myModel, nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel, nrOfSamples)
# dynamicModel.run()
mcModel.run()
