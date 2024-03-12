from abaqus import *
from abaqusConstants import *
import math

Dep = 0.368
Len = 3.68
HalDep = Dep/2
HalLen = Len/2
IPT = Dep/4
IPES = IPT/2
TranslatorNP = 5.0 - HalLen
TranslatorIP = TranslatorNP - IPES

# Create a new model
myModel = mdb.Model(name='MM')

# Matrix Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].rectangle(point1=(0.0,0.0),point2=(10.0,1.0))
myModel.Part(dimensionality=THREE_D, name='Matrix', type=DEFORMABLE_BODY)
myModel.parts['Matrix'].BaseSolidExtrude(depth=10.0, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']


# NP Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0) 
myModel.sketches['__profile__'].rectangle(point1=(0.5-HalLen,0.5-HalDep),point2=(0.5+HalLen,0.5+HalDep))
myModel.Part(dimensionality=THREE_D, name='NP', type=DEFORMABLE_BODY)
myModel.parts['NP'].BaseSolidExtrude(depth=Len, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']

# IP Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0) 
myModel.sketches['__profile__'].rectangle(point1=((0.5-HalLen)-IPES,(0.5-HalDep)-IPES),point2=((0.5+HalLen)+IPES,(0.5+HalDep)+IPES))
myModel.Part(dimensionality=THREE_D, name='IP', type=DEFORMABLE_BODY)
myModel.parts['IP'].BaseSolidExtrude(depth=Len+IPT, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']

#Creating Materials

myModel.Material(name='MatrixMat')
myModel.materials['MatrixMat'].Diffusivity(table=((1.0, 0.0), ))
myModel.materials['MatrixMat'].Solubility(table=((1.0, ), ))

myModel.Material(name='NPMat')
myModel.materials['NPMat'].Diffusivity(table=((0.0, 0.0), ))
myModel.materials['NPMat'].Solubility(table=((1.0, ), ))

myModel.Material(name='IPMat')
myModel.materials['IPMat'].Diffusivity(table=((0.000001, 0.0), ))
myModel.materials['IPMat'].Solubility(table=((1.0, ), ))


#Creating Sections for Mat and NP and IP

myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', thickness=None)
myModel.HomogeneousSolidSection(material='IPMat', name='IPSec', thickness=None)

myModel.parts['IP'].Set(cells=myModel.parts['IP'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
myModel.parts['IP'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['IP'].sets['Set-1'], sectionName='IPSec', thicknessAssignment=FROM_SECTION)

myModel.parts['Matrix'].Set(cells=myModel.parts['Matrix'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
myModel.parts['Matrix'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['Matrix'].sets['Set-1'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NP'].Set(cells=myModel.parts['NP'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
myModel.parts['NP'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NP'].sets['Set-1'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)


# Generating Assembly/Instances
myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)

myModel.rootAssembly.Instance(dependent=ON, name='NP-1', part=myModel.parts['NP'])
myModel.rootAssembly.translate(instanceList=('NP-1', ), vector=(5.0-Dep, 0.0, TranslatorNP))

myModel.rootAssembly.Instance(dependent=ON, name='IP-1', part=myModel.parts['IP'])
myModel.rootAssembly.translate(instanceList=('IP-1', ), vector=(5.0-Dep, 0.0, TranslatorIP))

myModel.rootAssembly.Instance(dependent=ON, name='Matrix-1', part=myModel.parts['Matrix'])
myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myModel.rootAssembly.instances['NP-1'], myModel.rootAssembly.instances['IP-1'], myModel.rootAssembly.instances['Matrix-1']), keepIntersections=ON, name='NanComp', originalInstances=SUPPRESS)


myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#4 ]', ), ), name='Set-2')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-2'], sectionName='MatSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#2 ]', ), ), name='Set-3')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-3'], sectionName='IPSec', thicknessAssignment=FROM_SECTION)

myModel.parts['NanComp'].Set(cells=myModel.parts['NanComp'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Set-4')
myModel.parts['NanComp'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=myModel.parts['NanComp'].sets['Set-4'], sectionName='NPSec', thicknessAssignment=FROM_SECTION)

myModel.rootAssembly.regenerate() 

# Setting up Step
myModel.MassDiffusionStep(amplitude=RAMP, name='MassDiffusionStep', previous='Initial', response=STEADY_STATE)

myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#2 ]', ), ), name='Set-1')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=1.0, name='BC-1', region=myModel.rootAssembly.sets['Set-1'])
myModel.rootAssembly.Set(faces=myModel.rootAssembly.instances['NanComp-1'].faces.getSequenceFromMask(('[#8 ]', ), ), name='Set-2')
myModel.ConcentrationBC(amplitude=UNSET, createStepName='MassDiffusionStep', distributionType=UNIFORM, fieldName='', fixed=OFF, magnitude=0.0, name='BC-2', region=myModel.rootAssembly.sets['Set-2'])

myModel.FieldOutputRequest(createStepName='MassDiffusionStep', name='F-Output-2',variables=('IVOL',))
 
# Setting up Mesh
import mesh
