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
    
    
  def initial(self):
    #Creating basic land use map using the probabilities of the file LandUse, under a uniform distribution
    uni=uniform(1)
    self.landUses = lookupnominal('LandUses.tbl', uni)
    self.report(self.landUses, '')

    isAgricultural = self.landUses == self.agricultural
    self.agriculture = ifthenelse(isAgricultural, scalar(1), 0)

    uni=uniform(1)
    self.population = lookupscalar('Population.tbl', uni)
    #isPopulation = pop == 1
    #self.population = ifthenelse(isPopulation, scalar(1), 0)
    self.report(self.population, 'inipop')
    

    uni=uniform(1)
    self.jobs = lookupscalar('Jobs.tbl', uni)
    self.report(self.jobs, 'inijobs')
    
    #self.population = ifthenelse(residential, scalar(1), 0)
    #popArea = maptotal(populationMap) #sum the total population
    #self.report(popArea, 'popArea') 
    
    #self.jobs = ifthenelse(industrial, scalar(1), 0)
    #jobArea = maptotal(jobsMap) #sum the total jobs
    #self.report(jobArea, 'jobArea')
    
    #self.report(self.population, 'population')
    #self.report(self.jobs, 'jobs')

    #x_activity_amount = self.population + self.jobs + self.agriculture

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
    
    #population to population weight
    weight0 = ifthenelse(isPopulation, scalar(30), 0) #weight itself
    weight1 = self.calculateActityWeight(isPopulation, 3, 0.25)
    weight2 = self.calculateActityWeight(isPopulation, 5, 0.001)

    wPopToPop = (weight0 + weight1 + weight2) * self.population
    self.report(wPopToPop, 'wPPT')

    popToPop = ifthenelse(isPopulation, wPopToPop, 0)
    self.report(popToPop, 'wPPR')
    #end population weight
    
    #population to jobs weight
    weight0 = ifthenelse(isJobs, scalar(0.1), 0) #weight itself
    weight1 = self.calculateActityWeight(isJobs, 3, 0.4)

    wPopToJob = (weight0 + weight1) * self.jobs
    self.report(wPopToJob, 'wPJT')

    popToJob = ifthenelse(isPopulation, wPopToJob, 0)
    self.report(popToJob, 'wPJR')
    #end population to jobs weight
    
    #population to agriculture weight    
    weight0 = scalar(0)
    weight1 = self.calculateActityWeight(isAgricultural, 3, 3)
    weight2 = self.calculateActityWeight(isAgricultural, 5, 0.5)
    weight3 = self.calculateActityWeight(isAgricultural, 7, 0.25)

    wPopToAgri = (weight0 + weight1 + weight2 + weight3) * self.agriculture
    self.report(wPopToAgri, 'wPAT')

    popToAgri = ifthenelse(isPopulation, wPopToAgri, 0)
    self.report(popToAgri, 'wPAR')
    #end population to agriculture weight

    #jobs(activity weight) to population(map to be) weigth
    weight0 = ifthenelse(isPopulation, scalar(0), 0) #weight itself
    weight1 = self.calculateActityWeight(isPopulation, 3, 0.5)
    
    wJobsToPop = (weight0 + weight1) * self.population
    self.report(wJobsToPop, 'wJPT')

    jobsToPop = ifthenelse(isJobs, wJobsToPop, 0)
    self.report(jobsToPop, 'wJPR')
    #ends jobs to population weigth
    #jobs(activity weight) to jobs(map to be) weigth
    weight0 = ifthenelse(isJobs, scalar(20), 0) #weight itself
    weight1 = self.calculateActityWeight(isJobs, 3, 0.45)

    wJobsToJob = (weight0 + weight1) * self.jobs
    self.report(wJobsToJob, 'wJJT')

    jobsToJob = ifthenelse(isJobs, wJobsToJob, 0)
    self.report(jobsToJob, 'wJJR')
    #end jobs(activity weight) to jobs(map to be) weigth

    #jobs(activity weight) to agriculture(map to be) weigth
    weight0 = ifthenelse(isAgricultural, scalar(0), 0) #weight itself
    weight1 = self.calculateActityWeight(isAgricultural, 3, 2)

    wJobsToAgri = (weight0 + weight1) * self.agriculture
    self.report(wJobsToAgri, 'wJAT')

    jobsToAgri = ifthenelse(isJobs, wJobsToAgri, 0)
    self.report(jobsToAgri, 'wJAR')
    #ends jobs(activity weight) to jobs(map to be) weigth
                                                                                   
    #agriculture(activity weight) to population(map to be) weigth
    weight0 = ifthenelse(isPopulation, scalar(4), 0) #weight itself
    weight1 = self.calculateActityWeight(isPopulation, 3, 1.5)
    weight2 = self.calculateActityWeight(isPopulation, 5, 0.2)
    weight3 = self.calculateActityWeight(isPopulation, 7, 0.1)

    wAgriToPop = (weight0 + weight1 + weight2 + weight3) * self.population
    self.report(wAgriToPop, 'wAPT')

    agriToPop = ifthenelse(isAgricultural, wAgriToPop, 0)
    self.report(agriToPop, 'wAPR')
    #ends agriculture(activity weight) to population(map to be) weigth

    #agriculture(activity weight) to jobs(map to be) weigth
    weight0 = scalar(0)
    weight1 = self.calculateActityWeight(isJobs, 3, 2)

    wAgriToJob = (weight0 + weight1) * self.jobs
    self.report(wAgriToJob, 'wAJT')

    agriToJob = ifthenelse(isAgricultural, wAgriToJob, 0)
    self.report(agriToJob, 'wAJR')
    #ends agriculture(activity weight) to jobs(map to be) weigth

    #agriculture(activity weight) to agriculture(map to be) weigth
    weight0 = ifthenelse(isAgricultural, scalar(300), 0) #weight itself
    self.report(weight0, 'wAA0')

    weight1 = self.calculateActityWeight(isAgricultural, 3, 5)
    self.report(weight1, 'wAA1')

    wAgriToAgri = (weight0 + weight1) * self.agriculture
    self.report(wAgriToAgri, 'wAAT')

    agriToAgri = ifthenelse(isAgricultural, wAgriToAgri, 0)
    self.report(agriToAgri, 'wAAR')
    #ends agriculture(activity weight) to agriculture(map to be) weigth

    ##TOTAL Weights
    wPopulation = wPopToPop + wPopToJob + wPopToAgri
    wJobs = wJobsToPop + wJobsToJob + wJobsToAgri
    wAgriculture = wAgriToPop + wAgriToJob + wAgriToAgri
    ##

    ########################################################
    c_populationToNatural = ifthenelse(isNatural, scalar(0.6), 0)
    c_populationToResidential = ifthenelse(isResidential, scalar(1.0), 0)
    c_populationToIndustrial = ifthenelse(isIndustrial, scalar(0.4), 0)
    c_populationToAgricultural = ifthenelse(isAgricultural, scalar(0.7), 0)


    c_jobsToNatural = ifthenelse(isNatural, scalar(0.5), 0)
    c_jobsToResidential = ifthenelse(isResidential, scalar(0.7), 0)
    c_jobsToIndustrial = ifthenelse(isIndustrial, scalar(1.0), 0)
    c_jobsToAgricultural = ifthenelse(isAgricultural, scalar(0.7), 0)
    ########################################################

    ##POTENTIAL OF POPULATION ACTIVITY
    e_pop_diseconomies = self.diseconomies(wPopulation)
    c_population = c_populationToNatural + c_populationToResidential + c_populationToIndustrial + c_populationToAgricultural
    
    populationPotential = c_population * self.nonNegativePotential(wPopulation + e_pop_diseconomies)

      #self.x_amount_population = (populationPotential / windowtotal(populationPotential, 7))
    self.x_amount_population = populationPotential
    
    self.report(populationPotential, 'popPot')
    self.report(self.x_amount_population, 'x_pop')
    ##END

    ##POTENTIAL OF JOB ACTIVITY
    e_job_diseconomies = self.diseconomies(wJobs)
    c_jobs = c_jobsToNatural + c_jobsToResidential + c_jobsToIndustrial + c_jobsToAgricultural
    
    jobsPotential = c_jobs * self.nonNegativePotential(wJobs + e_job_diseconomies)

      #self.x_amount_jobs = (jobsPotential / windowtotal(jobsPotential, 7))
    self.x_amount_jobs = jobsPotential
    
    self.report(jobsPotential, 'jobPot')
    self.report(self.x_amount_jobs, 'x_job')
    ##END OF POTENTIAL OF JOB ACTIVITY

    ##POTENTIAL OF AGRICULTURE ACTIVITY
    self.agriculturePotential = self.nonNegativePotential(wAgriculture)
    
    self.report(self.agriculturePotential, 'agriPot')
    ##END OF POTENTIAL OF AGRICULTURE ACTIVITY
    

    #naturalCoeficient = ifthenelse(self.land)

##    self.residential = 3
##    self.industrial = 2
##    self.agricultural = 1
##    self.natural = 4 

    self.landUses = self.newLandUse(self.population, self.jobs, self.agriculture)    
    self.report(self.landUses, 'LandUses')

    #increase activities
    self.population = ifthenelse(isPopulation, self.population + 1, 0)
    self.jobs = ifthenelse(isJobs, self.jobs + 1, 0)

  def postmcloop(self):
##    names = ['p','snow','q']
##    sampleNumbers = range(1,13)
##    timeSteps = range(1,182)
##    #percentiles = [0.025,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.975]
##    percentiles=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
##    mcaveragevariance(names,sampleNumbers,timeSteps)
##    mcpercentiles(names,percentiles,sampleNumbers,timeSteps)
    pass

  def calculateActityWeight(self, booleanActivityMap, distance, weight):
    level = distance - 2 # minus 2 cells

    activityWeight = ifthenelse(booleanActivityMap, scalar(weight), 0)
    
    weightLevel = windowtotal(activityWeight, level)
    weightDistance = windowtotal(activityWeight, distance)
    weightMap = weightDistance - weightLevel
    
    return weightMap

  def newLandUse(self, populationActivityAmount, jobsActivityAmount, agricultureActivityAmount):
    threshold = 20
    newLandUse = ifthenelse(populationActivityAmount > jobsActivityAmount, 
		ifthenelse(populationActivityAmount > agricultureActivityAmount, 
			ifthenelse(populationActivityAmount > threshold,
					nominal(self.residential),
					nominal(self.natural) ), 
			ifthenelse(agricultureActivityAmount > threshold,
					nominal(self.agricultural),
					nominal(self.natural))
		), 
		ifthenelse(jobsActivityAmount > agricultureActivityAmount, 
			ifthenelse(jobsActivityAmount > threshold,
					nominal(self.industrial),
					nominal(self.natural) 
			), 
			ifthenelse(populationActivityAmount > agricultureActivityAmount, 
				ifthenelse(populationActivityAmount > threshold,
						nominal(self.residential),
						nominal(self.natural) 
				), 
				ifthenelse(agricultureActivityAmount > threshold,
						nominal(self.agricultural),
						nominal(self.natural)
				)
			)
		)
	)

    isResidential = (newLandUse == self.residential) | (self.landUses == self.residential)
    isIndustrial = (newLandUse == self.industrial) | (self.landUses == self.industrial)
    isAgricultural = (newLandUse == self.agricultural) | (self.landUses == self.agricultural)
    isNatural = (newLandUse == self.natural) | (self.landUses == self.natural)

    otracosa = (newLandUse == self.industrial) | (newLandUse == self.agricultural) | (newLandUse == self.natural)
    isResidential = (newLandUse == self.residential) | ((self.landUses == self.residential) & pcrnot(otracosa))
    otracosa = (newLandUse == self.residential) | (newLandUse == self.agricultural) | (newLandUse == self.natural)
    isIndustrial = (newLandUse == self.industrial) | ((self.landUses == self.industrial) & pcrnot(otracosa))
    otracosa = (newLandUse == self.residential) | (newLandUse == self.industrial) | (newLandUse == self.natural)
    isAgricultural = (newLandUse == self.agricultural) | ((self.landUses == self.agricultural) & pcrnot(otracosa))
    otracosa = (newLandUse == self.residential) | (newLandUse == self.industrial) | (newLandUse == self.agricultural)
    isNatural = (newLandUse == self.natural) | ((self.landUses == self.natural) & pcrnot(otracosa))
    

##    isResidential = (newLandUse == self.residential) & pcrnot((self.landUses == self.industrial) | (self.landUses == self.natural) | (self.landUses == self.agricultural))
##    isIndustrial = (newLandUse == self.industrial) & pcrnot((self.landUses == self.residential) | (self.landUses == self.natural) | (self.landUses == self.agricultural))
##    isAgricultural = (newLandUse == self.agricultural) & pcrnot((self.landUses == self.residential) | (self.landUses == self.natural) | (self.landUses == self.industrial))
##    isNatural = (newLandUse == self.natural) & pcrnot((self.landUses == self.residential) | (self.landUses == self.agricultural) | (self.landUses == self.industrial))

    #newLandUse = ifthenelse(self.landUses != newLandUse, newLandUse, self.landUses)

    newLandUse = nominal(ifthenelse(isResidential, scalar(self.residential), 0) + ifthenelse(isIndustrial, scalar(self.industrial), 0) + ifthenelse(isAgricultural, scalar(self.agricultural), 0) + ifthenelse(isNatural, scalar(self.natural), 0))
    
    return newLandUse

  def nonNegativePotential(self, potMap):
    newMap = ln(scalar(1) + scalar(2) ** potMap)
    return newMap

  def diseconomies(self, totalWeights):
    # -1 < y1 < 0
    # y2 > 1
    y1 = -1
    y2 = 1.1
    diseconomies = y1 * totalWeights ** y2
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
