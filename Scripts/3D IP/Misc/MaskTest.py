from abaqus import *
from abaqusConstants import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import math


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
myModel.sketches['__profile__'].rectangle(point1=(3.65,0.365),point2=(6.35,0.635))
myModel.Part(dimensionality=THREE_D, name='NP', type=DEFORMABLE_BODY)
myModel.parts['NP'].BaseSolidExtrude(depth=2.7, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']

# IP Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0) 
myModel.sketches['__profile__'].rectangle(point1=(3.6,0.36),point2=(6.3,0.63))
myModel.Part(dimensionality=THREE_D, name='IP', type=DEFORMABLE_BODY)
myModel.parts['NP'].BaseSolidExtrude(depth=4.0, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']

#Creating Materials

myModel.Material(name='MatrixMat')
myModel.materials['MatrixMat'].Diffusivity(table=((0.005, 0.0), ))
myModel.materials['MatrixMat'].Solubility(table=((1.0, ), ))

myModel.Material(name='NPMat')
myModel.materials['NPMat'].Diffusivity(table=((0.0, 0.0), ))
myModel.materials['NPMat'].Solubility(table=((1.0, ), ))

myModel.Material(name='IPMat')
myModel.materials['IPMat'].Diffusivity(table=((0.5, 0.0), ))
myModel.materials['IPMat'].Solubility(table=((1.0, ), ))


#Creating Sections for Mat and NP and IP

myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', thickness=None)
myModel.HomogeneousSolidSection(material='IPMat', name='IPSec', thickness=None)