# Activity-Base Model to simulate the Land Use

Initializing the map:

Open the windows console and type: `mapattr new.map`

![Alt text](images/createNewMap.png?raw=true "Default values boundaries and cell size")

You can define the size of the map and the also the cell size among others attributes.


Base on the table rule (see src/initModel/LandUses.tbl):

[0,0.05> 1
[0.05,0.1> 2 
[0.1,0.2> 3
[0.2,1.0] 4

Where:

1 referes to Agricultural land use
2 to Industrial land use
3 to Residential land use and
4 to Natural 

We create our initial map call LandUse.map (see src/initModel/modelInitialization.py). As this  initial map is nominal, we need to add the legen label by typing the comand: `legend new.map`

![Alt text](images/addLegendsToNominalMap.png?raw=true "Adding legends")

# Running the model

To run the model you have to open your console and navigate to your program folder and type:

`aguila --timesteps=[1,999,1] --scenarios='{1,2,3}' --multi=2x2 pop jobs LandUses`

![Alt text](images/running-the-model.png?raw=true "Command to run the model")