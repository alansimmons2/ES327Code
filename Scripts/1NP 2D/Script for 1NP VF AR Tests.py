from abaqus import *
from abaqusConstants import *
import math


# Create a new model
myModel = mdb.Model(name='MM')



#Building Parts from Sketches

# Create Matrix Sketch
mySketch = myModel.ConstrainedSketch(name='MatrixSketch', sheetSize=200.0)
mySketch.rectangle(point1=(0.0, 0.0), point2=(50.0, 1.0))

# Create Matrix Part
myPart = myModel.Part(name='MatrixPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart.BaseShell(sketch=mySketch)

#Create NP Sketch
mySketch2 = myModel.ConstrainedSketch(name='NPSketch', sheetSize=200.0)
mySketch2.rectangle(point1=(20.0,0.45), point2=(30.0,0.55))

#Create NP Part
myPart2 = myModel.Part(name='NPPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart2.BaseShell(sketch=mySketch2)



#Creating Materials

# Create Material for Matrix
MatMaterial = myModel.Material(name='MatrixMat')
MatMaterial.Diffusivity(table=((0.005, 0.0),)) 
MatMaterial.Solubility(table=((1.0,),))

#Create Material for NP
NPMaterial = myModel.Material(name='NPMat')
NPMaterial.Diffusivity(table=((1.0,0.0),))
NPMaterial.Solubility(table=((1.0,),))



#Creating Sections for Mat and NP

# Create a section for the Matrix Part
mySection = myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
Matregion = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1 ]',),), name='Set-1')
myPart.SectionAssignment(region=Matregion, sectionName='MatSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

#Create a section for the NP Part
mySection2 = myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', thickness=None)
NPregion = myPart2.Set(faces=myPart2.faces.getSequenceFromMask(('[#1]',),), name='Set-1')
myPart2.SectionAssignment(region=NPregion, sectionName='NPSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')



# Creating Instances for NP and Matrix

# Instance for Matrix
myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(dependent=OFF, name='MatrixPart-1', part=myPart)

# Instance for NP
myAssembly2 = myModel.rootAssembly
myInstance2 = myAssembly2.Instance(dependent=OFF, name='NPPart-1', part=myPart2)

#Combine Instances to create composite
NanCompMergedInstance = myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myInstance, myInstance2), keepIntersections=ON, name='NanCompSec', originalInstances=SUPPRESS)
myModel.rootAssembly.makeIndependent(instances=(myModel.rootAssembly.instances['NanCompSec-1'], ))



#Setting up the new composite 

#NanCompSec = myModel.parts['NanCompSec']

myModel.parts['NanCompSec'].Set(faces=myModel.parts['NanCompSec'].faces.getSequenceFromMask(('[#2]',),), name='Set-2')
myModel.parts['NanCompSec'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanCompSec'].sets['Set-2'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NanCompSec'].Set(faces=myModel.parts['NanCompSec'].faces.getSequenceFromMask(('[#1]',),), name='Set-3')
myModel.parts['NanCompSec'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanCompSec'].sets['Set-3'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)

myModel.rootAssembly.regenerate()



# Creating the Mass Diffusion Steady-State Step
myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE, timePeriod=1)

myModel.FieldOutputRequest(createStepName='Step-1', name='F-Output-2',variables=('IVOL',))

#Taking Care of Boundary Conditions

# Set edges for boundary conditions
rightEdge = myModel.rootAssembly.instances['NanCompSec-1'].edges.findAt(((50.0, 0.5, 0.0),))
leftEdge = myModel.rootAssembly.instances['NanCompSec-1'].edges.findAt(((0.0, 0.5, 0.0),))
topEdge = myModel.rootAssembly.instances['NanCompSec-1'].edges.findAt(((25.0, 1.0, 0.0),))
bottomEdge = myModel.rootAssembly.instances['NanCompSec-1'].edges.findAt(((25.0, 0.0, 0.0),))


leftEdgeSet = myAssembly.Set(edges=leftEdge, name='Left_Edge_Set')
rightEdgeSet = myAssembly.Set(edges=rightEdge, name='Right_Edge_Set')
topEdgeSet = myAssembly.Set(edges=topEdge, name='Top_Edge_Set')
bottomEdgeSet = myAssembly.Set(edges=bottomEdge, name='Bottom_Edge_Set')

# Applying Boundary Conditions
myModel.ConcentrationBC(name='BC1', createStepName='Step-1', region=topEdgeSet, distributionType=UNIFORM, magnitude=1.0)
myModel.ConcentrationBC(name='BC2', createStepName='Step-1', region=bottomEdgeSet, distributionType=UNIFORM, magnitude=0.0)


#Generate Mesh
myAssembly.seedEdgeByNumber(edges=myPart.edges, number=10, constraint=FIXED)
myModel.rootAssembly.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(myModel.rootAssembly.instances['NanCompSec-1'],), size=0.1)
myModel.rootAssembly.generateMesh(regions=(myModel.rootAssembly.instances['NanCompSec-1'],))

#myModel.rootAssembly.seedEdgeByNumber(constraint=FINER, edges=topEdge, number=25)
#myModel.rootAssembly.seedEdgeByNumber(constraint=FINER, edges=leftEdge,number=10)
#myModel.rootAssembly.generateMesh(regions=(myModel.rootAssembly.instances['NanCompSec-1'],))


# Assign Element Type
import mesh
region_2D4 = myModel.rootAssembly.instances['NanCompSec-1'].sets['Set-1']
elemType_2D4 = mesh.ElemType(elemCode=DC2D4, elemLibrary=STANDARD)
myAssembly.setElementType(regions=region_2D4, elemTypes=(elemType_2D4,))