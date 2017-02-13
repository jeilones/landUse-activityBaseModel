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
    self.maxJobsPerTimeStep = self.maxPopulationPerTimeStep / 3
    self.maxAgriculturePerTimeStep = self.maxPopulationPerTimeStep / 10
    
  def initial(self):
    #Creating basic land use map using the probabilities of the file LandUse, under a uniform distribution
    uni=uniform(1)
    self.landUses = lookupnominal('LandUses.tbl', uni)
    self.report(self.landUses, 'LandUses')

    isAgricultural = self.landUses == self.agricultural
    isResidential = self.landUses == self.residential
    isIndustrial = self.landUses == self.industrial

    #Initialization for agriculture activity
    self.agriculture = ifthenelse(isAgricultural, scalar(1), 0)

    #Initialization for population activity
    uni=uniform(1)
    self.population = lookupscalar('Population.tbl', uni)
    self.report(self.population, 'inipop')
    
    #Initialization of jobs activity
    uni=uniform(1)
    self.jobs = lookupscalar('Jobs.tbl', uni)
    self.report(self.jobs, 'inijobs')

    #Define the default value for the increment of each activity, this will be calculated at the end of each dinamic time step
    self.x_amount_population = scalar(0)
    self.x_amount_jobs = scalar(0)
    self.x_amount_agriculture = scalar(0)
    
  def dynamic(self):
    #Defining Boleean Maps for land use
    isResidential = self.landUses == self.residential
    isIndustrial = self.landUses == self.industrial
    isAgricultural = self.landUses == self.agricultural
    isNatural = self.landUses == self.natural

    #Increment of activities 
    self.population = self.population + self.x_amount_population
    self.jobs = self.jobs + self.x_amount_jobs
    self.agriculture = self.agriculture + self.x_amount_agriculture
    self.agriculture = ifthenelse(isAgricultural, scalar(1), 0)

    #Create boolean maps that distinguish which kind of activitiy exist in each cell
    isPopulation = self.population > 0
    isJobs = self.jobs > 0
    isAgricultural = self.agriculture > 0

    self.report(self.population, 'pop')
    self.report(self.jobs, 'jobs')
    self.report(self.agriculture, 'agri')

    #CALCULATE ACTIVITY ATTRACTION BASED ON ACTIVITY WEIGHTS
    #population weights
    wPopToPop = self.calculateTotalActityWeights(isPopulation, 30, 0.25, 0.001, 0) #population attract population
    wPopToJob = self.calculateTotalActityWeights(isPopulation, 0.1, 0.4, 0, 0) #population attract jobs
    wPopToAgri = self.calculateTotalActityWeights(isPopulation, 0, 3, 0.5, 0.25) #population attract agricultural
    #end population weights
    #job weigths
    wJobsToPop = self.calculateTotalActityWeights(isJobs, 0, 0.5, 0, 0) #job attract population
    wJobsToJob = self.calculateTotalActityWeights(isJobs, 20, 0.45, 0, 0) #job attract jobs
    wJobsToAgri = self.calculateTotalActityWeights(isJobs, 0, 2, 0, 0) #job attract agricultural
    #ends job weigths
    #agriculture weigths
    wAgriToPop = self.calculateTotalActityWeights(isAgricultural, 4, 1.5, 0.2, 0.1) #agriculture attract population
    wAgriToJob = self.calculateTotalActityWeights(isAgricultural, 0, 2, 0, 0) #agriculture attract jobs
    wAgriToAgri = self.calculateTotalActityWeights(isAgricultural, 300, 5, 0, 0) #agriculture attract agriculture
    #ends agriculture weigths

    ##TOTAL Activity Weights
    wPopulation = wPopToPop + wJobsToPop + wAgriToPop
    wJobs = wPopToJob + wJobsToJob + wAgriToJob
    wAgriculture = wPopToAgri + wJobsToAgri + wAgriToAgri
    
    self.report(wPopulation, 'callPop')
    self.report(wJobs, 'callJob')
    self.report(wAgriculture, 'callAgri')
    
    ##CALCULATE POTENTIAL        
    populationPotential = self.calculatePotential(wPopulation) #OF POPULATION ACTIVITY
    jobPotential = self.calculatePotential(wJobs) #OF JOB ACTIVITY
    self.agriculturePotential = self.calculatePotential(wAgriculture) #OF AGRICULTURE ACTIVITY

    #Calculate the activity increment for the next time step
    self.x_amount_population = self.maxPopulationPerTimeStep * populationPotential
    self.x_amount_jobs = self.maxJobsPerTimeStep * jobPotential
    self.x_amount_agriculture = self.maxAgriculturePerTimeStep * self.agriculturePotential
    ##END POTENTIAL

    ##CREATE NEW LAND USE
    self.landUses = self.createNewLandUseMap(self.population, self.jobs, self.agriculture)    
    self.report(self.landUses, 'LandUses')

  def postmcloop(self):
    pass

  #Calulate the potential value given the activity weight that exceed a threshold
  def calculatePotential(self, activityWeightMap):
    potential = ifthenelse(activityWeightMap > 3, scalar(0.2),
                                     ifthenelse(activityWeightMap > 10, scalar(0.3),
                                                ifthenelse(activityWeightMap > 40, scalar(0.5), 0)))

    ##Define SUITABILITY, ZONING and ACCESIBILITY stochastic factors
    self.suitability = max(uniform(1), 0)
    self.zooning = max(uniform(1), 0)
    self.accessibility = max(uniform(1), 0)
    
    potential = potential * self.suitability * self.zooning * self.accessibility
    return potential

  #Given a boolean map indicating the existante of X activity in each cell, this function is use to 
  def calculateTotalActityWeights(self, booleanActivityMap, level0, level1, level2, level3):
    weight0 = ifthenelse(booleanActivityMap, scalar(level0), 0) #weight itself
    weight1 = self.calculateActityWeight(booleanActivityMap, 3, level1)
    weight2 = self.calculateActityWeight(booleanActivityMap, 5, level2)
    weight3 = self.calculateActityWeight(booleanActivityMap, 7, level3)

    return weight0 + weight1 + weight2 + weight3

  #This function is used to calculate the neighbourhood effect for the real distance, this means, the 'ring' over that distance but not contained cells
  def calculateActityWeight(self, booleanActivityMap, distance, weight):
    if(weight == 0):
      return scalar(0)
    
    level = distance - 2 # minus 2 hectares

    activityWeight = ifthenelse(booleanActivityMap, scalar(weight), 0)
    
    weightLevel = windowtotal(activityWeight, level)
    weightDistance = windowtotal(activityWeight, distance)
    weightMap = weightDistance - weightLevel
    
    return weightMap

  #Create the new land use based on the total activity that exist in each cell, if the activity exceeds the predefined threshold, the cell change for the matching land use 
  def createNewLandUseMap(self, populationActivityAmount, jobsActivityAmount, agricultureActivityAmount):
    thresholdIndustrial = 0.9 * mapmaximum(populationActivityAmount)
    thresholdResidentialMin = 0.8 * mapmaximum(populationActivityAmount)
    thresholdResidentialMax = thresholdIndustrial
    thresholdAgricultureMin = 0.55 * mapmaximum(populationActivityAmount)
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
  
nrOfTimeSteps=999
nrOfSamples=3
myModel = LandUse()
dynamicModel = DynamicFramework(myModel, nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel, nrOfSamples)
# dynamicModel.run()
mcModel.run()
