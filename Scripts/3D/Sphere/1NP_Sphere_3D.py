from abaqus import *
from abaqusConstants import *
import math

rad = 0.288

# Create a new model
myModel = mdb.Model(name='MM')

# Matrix Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].rectangle(point1=(0.0,0.0),point2=(1.0,1.0))
myModel.Part(dimensionality=THREE_D, name='Matrix', type=DEFORMABLE_BODY)
myModel.parts['Matrix'].BaseSolidExtrude(depth=1.0, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']


# NP Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
myModel.sketches['__profile__'].FixedConstraint(entity=myModel.sketches['__profile__'].geometry[2])
myModel.sketches['__profile__'].ArcByCenterEnds(center=(0.0, 0.0), direction=CLOCKWISE, point1=(0.0, rad), point2=(0.0, -0.184756919741631))
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=False, entity1=myModel.sketches['__profile__'].vertices[2], entity2=myModel.sketches['__profile__'].geometry[2])
myModel.sketches['__profile__'].CoincidentConstraint(addUndoState=False, entity1=myModel.sketches['__profile__'].vertices[1], entity2=myModel.sketches['__profile__'].geometry[2])
myModel.sketches['__profile__'].Line(point1=(0.0, rad), point2=(0.0, -rad))
myModel.sketches['__profile__'].VerticalConstraint(addUndoState=False, entity=myModel.sketches['__profile__'].geometry[4])
myModel.sketches['__profile__'].PerpendicularConstraint(addUndoState=False, entity1=myModel.sketches['__profile__'].geometry[3], entity2=myModel.sketches['__profile__'].geometry[4])
myModel.Part(dimensionality=THREE_D, name='NP', type=DEFORMABLE_BODY)
myModel.parts['NP'].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']


#Creating Materials

# Create Material for Matrix
MatMaterial = myModel.Material(name='MatrixMat')
MatMaterial.Diffusivity(table=((1.0, 0.0),)) 
MatMaterial.Solubility(table=((1.0,),))

#Create Material for NP
NPMaterial = myModel.Material(name='NPMat')
NPMaterial.Diffusivity(table=((0.0,0.0),))
NPMaterial.Solubility(table=((1.0,),))


#Creating Sections for Mat and NP

myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', 
    thickness=None)
myModel.parts['NP'].Set(cells=myModel.parts['NP'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
myModel.parts['NP'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NP'].sets['Set-1'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)
myModel.parts['Matrix'].Set(cells=myModel.parts['Matrix'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
myModel.parts['Matrix'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['Matrix'].sets['Set-1'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)


# Generating Assembly/Instances
myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
myModel.rootAssembly.Instance(dependent=ON, name='NP-1', part=myModel.parts['NP'])
myModel.rootAssembly.translate(instanceList=('NP-1', ), vector=(0.5, 0.5, 0.5))
myModel.rootAssembly.Instance(dependent=ON, name='Matrix-1', part=myModel.parts['Matrix'])
myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myModel.rootAssembly.instances['NP-1'], myModel.rootAssembly.instances['Matrix-1']), keepIntersections=ON, name='NanComp', originalInstances=SUPPRESS)

myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-2')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-2'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)
myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#2 ]', ), ), name='Set-3')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-3'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)
myModel.rootAssembly.regenerate() 

# Setting up Step
myModel.MassDiffusionStep(amplitude=RAMP, name='MassDiffusionStep', previous='Initial', response=STEADY_STATE)

myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#2 ]', ), ), name='Set-3')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=1.0, name='BC-1', region=myModel.rootAssembly.sets['Set-3'])
myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#8 ]', ), ), name='Set-4')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=0.0, name='BC-2', region=myModel.rootAssembly.sets['Set-4'])

myModel.FieldOutputRequest(createStepName='MassDiffusionStep', name='F-Output-2',variables=('IVOL',))
 
# Setting up Mesh
import mesh
myModel.rootAssembly.makeDependent(instances=(myModel.rootAssembly.instances['NanComp-1'], ))
myModel.parts['NanComp'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=0.1)
myModel.parts['NanComp'].generateMesh()
myModel.parts['NanComp'].setMeshControls(elemShape=TET, regions=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#2 ]', ), ), technique=FREE)
myModel.parts['NanComp'].setMeshControls(elemShape=TET, regions=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#3 ]', ), ), technique=FREE)

part = myModel.parts['NanComp']
elemType_DC3D20 = mesh.ElemType(elemCode=DC3D20, elemLibrary=STANDARD)
elemType_DC3D15 = mesh.ElemType(elemCode=DC3D15, elemLibrary=STANDARD)
elemType_DC3D10 = mesh.ElemType(elemCode=DC3D10, elemLibrary=STANDARD)
region_mask = ('[#3 ]',)
region_sequence = part.cells.getSequenceFromMask(region_mask)
part.setElementType(elemTypes=(elemType_DC3D20, elemType_DC3D15, elemType_DC3D10),regions=(region_sequence,),)

myModel.parts['NanComp'].generateMesh()
myModel.rootAssembly.regenerate()