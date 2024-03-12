from abaqus import *
from abaqusConstants import *
import math

# Create a new model
myModel = mdb.Model(name='MM')

# Create a sketch for the profile
mySketch = myModel.ConstrainedSketch(name='MatrixSketch', sheetSize=200.0)
mySketch.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))

# Create a part and base shell on the sketch
myPart = myModel.Part(name='MatrixPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart.BaseShell(sketch=mySketch)

# Create a material and define properties
myMaterial = myModel.Material(name='MatrixProps')
myMaterial.Diffusivity(table=((0.005, 0.0),))
myMaterial.Solubility(table=((1.0,),))

# Create a section and assign the material
mySection = myModel.HomogeneousSolidSection(material='MatrixProps', name='MatrixSection', thickness=None)
region = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1 ]',),), name='Set-1')
myPart.SectionAssignment(region=region, sectionName='MatrixSection', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

# Create an independent instance for the part
myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(dependent=OFF, name='MatrixPart-1', part=myPart)

# Create a step for the analysis
myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE, timePeriod=1)

myModel.FieldOutputRequest(createStepName='Step-1', name='F-Output-2',variables=('IVOL',))

# Set edges for boundary conditions
rightEdge = myInstance.edges.findAt(((1.0, 0.5, 0.0),))
leftEdge = myInstance.edges.findAt(((0.0, 0.5, 0.0),))
topEdge = myInstance.edges.findAt(((0.5, 1.0, 0.0),))

leftEdgeSet = myAssembly.Set(edges=leftEdge, name='Left_Edge_Set')
rightEdgeSet = myAssembly.Set(edges=rightEdge, name='Right_Edge_Set')

# Applying Boundary Conditions
myModel.ConcentrationBC(name='BC1', createStepName='Step-1', region=leftEdgeSet, distributionType=UNIFORM, magnitude=1.0)
myModel.ConcentrationBC(name='BC2', createStepName='Step-1', region=rightEdgeSet, distributionType=UNIFORM, magnitude=0.0)


# Seed edges for meshing
myAssembly.seedEdgeByNumber(edges=leftEdge, number=5, constraint=FIXED)
myAssembly.seedEdgeByNumber(edges=topEdge, number=5, constraint=FIXED)

# Generate mesh
myAssembly.generateMesh(regions=(myInstance,))

# Assign Element Type
import mesh
region_2D4 = myInstance.sets['Set-1']
elemType_2D4 = mesh.ElemType(elemCode=DC2D4, elemLibrary=STANDARD)
myAssembly.setElementType(regions=region_2D4, elemTypes=(elemType_2D4,))

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

output_file_path = 'MatrixIPs.csv'
with open(output_file_path, 'w') as file:
    file.write('Element, Integration_Point, IVOL, Mass_Flux in X, Mass Flux in Y \n')
    for i, value in enumerate(values_at_integration_points):
    
        volav = values_at_integration_pointsB[i].data * math.sqrt((value.data[0])**2+(value.data[1])**2)
        
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

