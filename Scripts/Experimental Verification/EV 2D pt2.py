from abaqus import *
from abaqusConstants import *
import math
import mesh

# Create an analysis job for the model and submit it.

jobName = 'MassDiffusionJob'
myJob = mdb.Job(name=jobName, model='MM', description='MassDiffusionTest')

# Wait for the job to complete.

myJob.submit()
myJob.waitForCompletion()

# Visualisation process
import visualization
myViewport = session.Viewport(name='Viewport1')
myOdb = visualization.openOdb(path=jobName + '.odb')
myViewport.setValues(displayedObject=myOdb)
myViewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
myViewport.odbDisplay.commonOptions.setValues(renderStyle=FILLED)


#PostProcessing Process

#Setting up an Output File with all the information I need

#Reading the Mass Flux output values
from odbAccess import openOdb

#Setting path to find the output database
odb_path = 'MassDiffusionJob.odb'
odb = openOdb(odb_path)


#Setting the output file to read data from the end of the steady state step analysis
field_output = odb.steps['Step-1'].frames[-1].fieldOutputs['MFL']
ivol = odb.steps['Step-1'].frames[-1].fieldOutputs['IVOL']


values_at_integration_points = field_output.values
values_at_integration_pointsB = ivol.values

#Creating a readable output file with all data required from the simulation

output_file_path = 'SingleNPModelOutput.csv'
with open(output_file_path, 'w') as file:
    file.write('Element, Integration_Point, IVOL, Mass_Flux in X, Mass Flux in Y, Vol Averaged MFL \n')
    for i, value in enumerate(values_at_integration_points):
    
        volav = values_at_integration_pointsB[i].data * value.data[1]
        
        outstr = str(value.elementLabel) + ',' + str(value.integrationPoint) + ',' + str(values_at_integration_pointsB[i].data) + ',' + str(value.data[0]) + ',' + str(value.data[1]) + ',' + str(volav) + '\n'
        file.write(outstr)


#Working out average flux across the model

#Setting up values that allow for the average to be calculated
IPTotal = 0
MFLTotal = 0

#Open destination file
with open(output_file_path, 'r') as file:
    next(file)
    
    #Creating for loop that counts up the number of integration points (IPTotal) and sums up all values of flux (MFLTotal)
    for line in file:
        values = line.strip().split(',')
        IPTotal += 1
        MFLX = float(values[-1])
        MFLTotal += MFLX
        
        
print("IPTotal = " + str(IPTotal))
print("Volumetrically Averaged MFL = " + str(MFLTotal))