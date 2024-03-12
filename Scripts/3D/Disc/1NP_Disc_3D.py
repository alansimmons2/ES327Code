from abaqus import *
from abaqusConstants import *
import math

diam = 2.64
rad = diam/2
dep = 0.90

# Create a new model
myModel = mdb.Model(name='MM')

# Matrix Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].rectangle(point1=(0.0,0.0),point2=(12.0,12.0))
myModel.Part(dimensionality=THREE_D, name='Matrix', type=DEFORMABLE_BODY)
myModel.parts['Matrix'].BaseSolidExtrude(depth=1.0, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']


# NP Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].CircleByCenterPerimeter(center=(6.0, 0.5), point1=(6+rad, 0.5))
myModel.Part(dimensionality=THREE_D, name='NP', type=DEFORMABLE_BODY)
myModel.parts['NP'].BaseSolidExtrude(depth=dep, sketch=myModel.sketches['__profile__'])
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
myModel.rootAssembly.translate(instanceList=('NP-1', ), vector=(0.0, 6.0-(rad/2), 0.5-(dep/2)))
myModel.rootAssembly.Instance(dependent=ON, name='Matrix-1', part=myModel.parts['Matrix'])
myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myModel.rootAssembly.instances['NP-1'], myModel.rootAssembly.instances['Matrix-1']), keepIntersections=ON, name='NanComp', originalInstances=SUPPRESS)

myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-2')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-2'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)
myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#2 ]', ), ), name='Set-3')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-3'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)
myModel.rootAssembly.regenerate() 

# Setting up Step
myModel.MassDiffusionStep(amplitude=RAMP, name='MassDiffusionStep', previous='Initial', response=STEADY_STATE)

myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#10 ]', ), ), name='Set-1')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=1.0, name='BC-1', region=myModel.rootAssembly.sets['Set-1'])
myModel.rootAssembly.Set(faces=mdb.models['MM'].rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#20 ]', ), ), name='Set-2')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=0.0, name='BC-2', region=mdb.models['MM'].rootAssembly.sets['Set-2'])

myModel.FieldOutputRequest(createStepName='MassDiffusionStep', name='F-Output-2',variables=('IVOL',))
 
# Setting up Mesh
import mesh
myModel.rootAssembly.makeDependent(instances=(myModel.rootAssembly.instances['NanComp-1'], ))
myModel.parts['NanComp'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=0.5)
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