from abaqus import *
from abaqusConstants import *
import math


# Create a new model
myModel = mdb.Model(name='MM')

# Matrix Creation
myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
myModel.sketches['__profile__'].rectangle(point1=(0.0,0.0),point2=(12.0,12.0))
myModel.Part(dimensionality=THREE_D, name='Matrix', type=DEFORMABLE_BODY)
myModel.parts['Matrix'].BaseSolidExtrude(depth=1.0, sketch=myModel.sketches['__profile__'])
del myModel.sketches['__profile__']


