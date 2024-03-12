from abaqus import *
from abaqusConstants import *
import math
import mesh
import visualization


# Create a new model
myModel = mdb.Model(name='MM')

#Building Parts from Sketches

# Create Matrix Sketch
mySketch = myModel.ConstrainedSketch(name='MatrixSketch', sheetSize=200.0)
mySketch.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))

# Create Matrix Part
myPart = myModel.Part(name='MatrixPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart.BaseShell(sketch=mySketch)

#Create NP Sketch
mySketch2 = myModel.ConstrainedSketch(name='NPSketch', sheetSize=200.0)
mySketch2.rectangle(point1=(0.14645,0.46464), point2=(0.85355,0.5355))

#Create NP Part
myPart2 = myModel.Part(name='NPPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart2.BaseShell(sketch=mySketch2)

#Create IP Sketch
mySketch3 = myModel.ConstrainedSketch(name='IPSketch', sheetSize=200.0)
mySketch3.rectangle(point1=(0.1375925,0.4557825), point2=(0.8624075,0.5443575))

#Create IP Part
myPart3 = myModel.Part(name='IPPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart3.BaseShell(sketch=mySketch3)


#Creating Materials

# Create Material for Matrix
MatMaterial = myModel.Material(name='MatrixMat')
MatMaterial.Diffusivity(table=((0.005, 0.0),)) 
MatMaterial.Solubility(table=((1.0,),))

#Create Material for NP
NPMaterial = myModel.Material(name='NPMat')
NPMaterial.Diffusivity(table=((0.0,0.0),))
NPMaterial.Solubility(table=((1.0,),))

#Create Material for IP
IPMaterial = myModel.Material(name='IPMat')
IPMaterial.Diffusivity(table=((0.0,0.0),))
IPMaterial.Solubility(table=((1.0,),))


#Creating Sections for Mat, NP and IP

# Create a section for the Matrix Part
mySection = myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
Matregion = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1 ]',),), name='Set-1')
myPart.SectionAssignment(region=Matregion, sectionName='MatSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

#Create a section for the NP Part
mySection2 = myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', thickness=None)
NPregion = myPart2.Set(faces=myPart2.faces.getSequenceFromMask(('[#1]',),), name='Set-1')
myPart2.SectionAssignment(region=NPregion, sectionName='NPSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

#Create a section for the IP Part
mySection3 = myModel.HomogeneousSolidSection(material='IPMat', name='IPSec', thickness=None)
IPregion = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1]',),), name='Set-1')
myPart3.SectionAssignment(region=IPregion, sectionName='IPSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')


# Creating Instances for NP and Matrix

# Instance for Matrix
myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(dependent=OFF, name='MatrixPart-1', part=myPart)

# Instance for NP
myAssembly2 = myModel.rootAssembly
myInstance2 = myAssembly2.Instance(dependent=OFF, name='NPPart-1', part=myPart2)

# Instance for IP
myAssembly3 = myModel.rootAssembly
myInstance3 = myAssembly3.Instance(dependent=OFF, name='IPPart-1', part=myPart3)

#Combine Instances to create composite
NanCompMergedInstance = myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myInstance, myInstance2, myInstance3), keepIntersections=ON, name='NCPI', originalInstances=SUPPRESS)
myModel.rootAssembly.makeIndependent(instances=(myModel.rootAssembly.instances['NCPI-1'], ))


#Setting up the new composite 

#NanCompSec = myModel.parts['NanCompSec']

myModel.parts['NCPI'].Set(faces=myModel.parts['NCPI'].faces.getSequenceFromMask(('[#2]',),), name='Set-2')
myModel.parts['NCPI'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NCPI'].sets['Set-2'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NCPI'].Set(faces=myModel.parts['NCPI'].faces.getSequenceFromMask(('[#1]',),), name='Set-3')
myModel.parts['NCPI'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NCPI'].sets['Set-3'], sectionName='IPSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NCPI'].Set(faces=myModel.parts['NCPI'].faces.getSequenceFromMask(('[#4]',),), name='Set-4')
myModel.parts['NCPI'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NCPI'].sets['Set-4'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)

myModel.rootAssembly.regenerate()



# Creating the Mass Diffusion Steady-State Step
myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE, timePeriod=1)

myModel.FieldOutputRequest(createStepName='Step-1', name='F-Output-2',variables=('IVOL',))

#Taking Care of Boundary Conditions

# Set edges for boundary conditions
rightEdge = myModel.rootAssembly.instances['NCPI-1'].edges.findAt(((1.0, 0.5, 0.0),))
leftEdge = myModel.rootAssembly.instances['NCPI-1'].edges.findAt(((0.0, 0.5, 0.0),))
topEdge = myModel.rootAssembly.instances['NCPI-1'].edges.findAt(((0.5, 1.0, 0.0),))
bottomEdge = myModel.rootAssembly.instances['NCPI-1'].edges.findAt(((0.5, 0.0, 0.0),))


leftEdgeSet = myAssembly.Set(edges=leftEdge, name='Left_Edge_Set')
rightEdgeSet = myAssembly.Set(edges=rightEdge, name='Right_Edge_Set')
topEdgeSet = myAssembly.Set(edges=topEdge, name='Top_Edge_Set')
bottomEdgeSet = myAssembly.Set(edges=bottomEdge, name='Bottom_Edge_Set')

# Applying Boundary Conditions
myModel.ConcentrationBC(name='BC1', createStepName='Step-1', region=topEdgeSet, distributionType=UNIFORM, magnitude=1.0)
myModel.ConcentrationBC(name='BC2', createStepName='Step-1', region=bottomEdgeSet, distributionType=UNIFORM, magnitude=0.0)

myModel.rootAssembly.makeIndependent(instances=(myModel.rootAssembly.instances['NCPI-1'],))


#Create Mesh Partitions to ensure square mesh generation + Generate Mesh

myModel.rootAssembly.makeIndependent(instances=(
    myModel.rootAssembly.instances['NCPI-1'], ))


myModel.ConstrainedSketch(gridSpacing=0.07, name='__profile__', 
    sheetSize=2.82, transform=
    myModel.rootAssembly.MakeSketchTransform(
    sketchPlane=myModel.rootAssembly.instances['NCPI-1'].faces[2], 
    sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.5, 0.499995, 
    0.0)))
myModel.rootAssembly.projectReferencesOntoSketch(filter=COPLANAR_EDGES
    , sketch=myModel.sketches['__profile__'])
myModel.sketches['__profile__'].Line(point1=(-0.3624075, 0.0443625), 
    point2=(-0.5, 0.0443625))
	
myModel.sketches['__profile__'].HorizontalConstraint(addUndoState=
    False, entity=myModel.sketches['__profile__'].geometry[22])
myModel.sketches['__profile__'].ParallelConstraint(addUndoState=False, 
    entity1=myModel.sketches['__profile__'].geometry[8], entity2=
    myModel.sketches['__profile__'].geometry[22])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[12], 
    entity2=myModel.sketches['__profile__'].geometry[21])
myModel.sketches['__profile__'].Line(point1=(-0.3624075, -0.0442125), 
    point2=(-0.5, -0.0442125))
	
myModel.sketches['__profile__'].HorizontalConstraint(addUndoState=
    False, entity=myModel.sketches['__profile__'].geometry[23])
	
myModel.sketches['__profile__'].ParallelConstraint(addUndoState=False, 
    entity1=myModel.sketches['__profile__'].geometry[6], entity2=
    myModel.sketches['__profile__'].geometry[23])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[13], 
    entity2=myModel.sketches['__profile__'].geometry[21])
	
myModel.sketches['__profile__'].Line(point1=(0.3624075, 0.0443625), 
    point2=(0.5, 0.0443625))
	
myModel.sketches['__profile__'].HorizontalConstraint(addUndoState=
    False, entity=myModel.sketches['__profile__'].geometry[24])
	
myModel.sketches['__profile__'].PerpendicularConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].geometry[7], 
    entity2=myModel.sketches['__profile__'].geometry[24])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[14], 
    entity2=myModel.sketches['__profile__'].geometry[19])
	
myModel.sketches['__profile__'].Line(point1=(0.3624075, -0.0442125), 
    point2=(0.5, -0.0442125))
myModel.sketches['__profile__'].HorizontalConstraint(addUndoState=
    False, entity=myModel.sketches['__profile__'].geometry[25])
	
myModel.sketches['__profile__'].ParallelConstraint(addUndoState=False, 
    entity1=myModel.sketches['__profile__'].geometry[6], entity2=
    myModel.sketches['__profile__'].geometry[25])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[15], 
    entity2=myModel.sketches['__profile__'].geometry[19])
	
myModel.rootAssembly.PartitionFaceBySketch(faces=
    myModel.rootAssembly.instances['NCPI-1'].faces.getSequenceFromMask(
    ('[#4 ]', ), ), sketch=myModel.sketches['__profile__'])
	
del myModel.sketches['__profile__']

myModel.ConstrainedSketch(gridSpacing=0.07, name='__profile__', 
    sheetSize=2.82, transform=
    myModel.rootAssembly.MakeSketchTransform(
    sketchPlane=myModel.rootAssembly.instances['NCPI-1'].faces[3], 
    sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.5, 0.50007, 
    0.0)))
	
myModel.rootAssembly.projectReferencesOntoSketch(filter=COPLANAR_EDGES
    , sketch=myModel.sketches['__profile__'])
	
myModel.sketches['__profile__'].Line(point1=(-0.35355, 0.03543), 
    point2=(-0.351299732923508, 0.0442875))
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[16], 
    entity2=myModel.sketches['__profile__'].geometry[22])
	
myModel.sketches['__profile__'].undo()

myModel.sketches['__profile__'].Line(point1=(-0.35355, 0.03543), 
    point2=(-0.35355, 0.0442874999858439))
	
myModel.sketches['__profile__'].VerticalConstraint(addUndoState=False, 
    entity=myModel.sketches['__profile__'].geometry[34])
	
myModel.sketches['__profile__'].ParallelConstraint(addUndoState=False, 
    entity1=myModel.sketches['__profile__'].geometry[17], entity2=
    myModel.sketches['__profile__'].geometry[34])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[16], 
    entity2=myModel.sketches['__profile__'].geometry[22])
	
myModel.sketches['__profile__'].Line(point1=(-0.35355, -0.03543), 
    point2=(-0.35355, -0.0442874999858439))
	
myModel.sketches['__profile__'].VerticalConstraint(addUndoState=False, 
    entity=myModel.sketches['__profile__'].geometry[35])
	
myModel.sketches['__profile__'].PerpendicularConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].geometry[16], 
    entity2=myModel.sketches['__profile__'].geometry[35])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[17], 
    entity2=myModel.sketches['__profile__'].geometry[7])
	
myModel.sketches['__profile__'].Line(point1=(0.35355, 0.03543), 
    point2=(0.35355, 0.0442874999858439))
	
myModel.sketches['__profile__'].VerticalConstraint(addUndoState=False, 
    entity=myModel.sketches['__profile__'].geometry[36])
	
myModel.sketches['__profile__'].PerpendicularConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].geometry[18], 
    entity2=myModel.sketches['__profile__'].geometry[36])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[18], 
    entity2=myModel.sketches['__profile__'].geometry[22])
	
myModel.sketches['__profile__'].Line(point1=(0.35355, -0.03543), 
    point2=(0.35355, -0.0442874999858439))
	
myModel.sketches['__profile__'].VerticalConstraint(addUndoState=False, 
    entity=myModel.sketches['__profile__'].geometry[37])
	
myModel.sketches['__profile__'].PerpendicularConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].geometry[16], 
    entity2=myModel.sketches['__profile__'].geometry[37])
	
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=
    False, entity1=myModel.sketches['__profile__'].vertices[19], 
    entity2=myModel.sketches['__profile__'].geometry[7])
	
myModel.rootAssembly.PartitionFaceBySketch(faces=
    myModel.rootAssembly.instances['NCPI-1'].faces.getSequenceFromMask(
    ('[#8 ]', ), ), sketch=myModel.sketches['__profile__'])
	
del myModel.sketches['__profile__']

myModel.rootAssembly.setMeshControls(regions=
    myModel.rootAssembly.instances['NCPI-1'].faces.getSequenceFromMask(
    ('[#1ff ]', ), ), technique=STRUCTURED)
	
myModel.rootAssembly.deleteSeeds(regions=(
    myModel.rootAssembly.instances['NCPI-1'], ))
	
myModel.rootAssembly.seedEdgeBySize(constraint=FINER, deviationFactor=
    0.1, edges=
    myModel.rootAssembly.instances['NCPI-1'].edges.getSequenceFromMask(
    ('[#4000000 ]', ), ), size=0.05)
	
myModel.rootAssembly.seedEdgeBySize(constraint=FINER, deviationFactor=
    0.1, edges=
    myModel.rootAssembly.instances['NCPI-1'].edges.getSequenceFromMask(
    ('[#4000000 ]', ), ), size=0.01)
	
myModel.rootAssembly.seedEdgeBySize(constraint=FINER, deviationFactor=
    0.1, edges=
    myModel.rootAssembly.instances['NCPI-1'].edges.getSequenceFromMask(
    ('[#8108000 ]', ), ), size=0.01)
	
myModel.rootAssembly.generateMesh(regions=(
    myModel.rootAssembly.instances['NCPI-1'], ))


#Mesh Generation

#myModel.rootAssembly.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(myModel.rootAssembly.instances['NCPI-1'],), size=0.05)
#myModel.rootAssembly.generateMesh(regions=(myModel.rootAssembly.instances['NCPI-1'],))

# Assign Element Type

import mesh
region_2D4 = myModel.rootAssembly.instances['NCPI-1'].sets['Set-1']
elemType_2D4 = mesh.ElemType(elemCode=DC2D4, elemLibrary=STANDARD)
myAssembly.setElementType(regions=region_2D4, elemTypes=(elemType_2D4,))








