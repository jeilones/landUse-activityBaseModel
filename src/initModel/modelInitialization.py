from pcraster import *
from pcraster.framework import *

class RandomModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone('../../resources/clone.map')

  def initial(self):
    #Creating basic land use map using the probabilities of the file LandUse, under a uniform distribution
    uni=uniform(1)
    landUses=lookupnominal('../../resources/LandUses.tbl', uni)
    self.report(landUses, '../../src/LandUses')
    
    #Defining Boleean Maps
    
    residential = landUses == 1
    
    industrial = landUses == 2
    
    agricultural = landUses == 3
   
    natural= landUses == 4
   
    
    #Creating starting population and job maps for each type of land use, feel free to change them

    #Obviamente al inicializar los valores en las zonas residenciales existira
    #una poblacion mayor mientras que en la region natural no vive nadie,
    #y hay mos trabajos en la zona residencial
    residentialPopulation = ifthenelse(residential, scalar(1), 0)
    residentialJobs = ifthenelse(residential, scalar(1), 0)

    industrialPopulation = ifthenelse(industrial, scalar(1), 0)
    industrialJobs = ifthenelse(industrial, scalar(1), 0)

    #Agricultural activity has population but no jobs
    #agriculturalPopulation = ifthenelse(agricultural, scalar(1), 0)
    #1 ha to feed 10 people
    #agriculturalJobs = ifthenelse(agricultural, scalar(100), 0)
    
    #Natural es 0 en poblacion y 0 en trabajo por eso se omite este el
    #calculo del mapa boleano para naturaleza
    
    populationMap = residentialPopulation + industrialPopulation #+ agriculturalPopulation
    jobsMap = residentialJobs + industrialJobs #+ agriculturalJobs
    
    self.report(populationMap, '../../src/populationMap')
    self.report(jobsMap, '../../src/jobsMap')
    
    

  def dynamic(self):
    u=uniform(1)
   

nrOfTimeSteps=10
myModel = RandomModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()

