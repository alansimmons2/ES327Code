from abaqus import *
from abaqusConstants import *

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
mySketch2.rectangle(point1=(0.2,0.45), point2=(0.8,0.55))

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
NPMaterial.Diffusivity(table=((1e-10,0.0),))
NPMaterial.Solubility(table=((1.0,),))



#Creating Sections for Mat and NP

# Create a section for the Matrix Part
mySection = myModel.HomogeneousSolidSection(material='MatrixMat', name='MatSec', thickness=None)
Matregion = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1 ]',),), name='Set-1')
myPart.SectionAssignment(region=Matregion, sectionName='MatSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

#Create a section for the NP Part
mySection2 = myModel.HomogeneousSolidSection(material='NPMat', name='NPSec', thickness=None)
NPregion = myPart2.Set(faces=myPart2.faces.getSequenceFromMask(('[#1]',),), name='Set-2')
myPart2.SectionAssignment(region=NPregion, sectionName='NPSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')



# Creating Instances for NP and Matrix

# Instance for Matrix
myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(dependent=OFF, name='MatrixPart-1', part=myPart)

# Instance for NP
myAssembly2 = myModel.rootAssembly
myInstance2 = myAssembly2.Instance(dependent=OFF, name='NPPart-1', part=myPart2)

#Combine Instances to create composite
myModel.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, instances=(myInstance, myInstance2), keepIntersections=ON, name='NanComp', originalInstances=SUPPRESS)



# Creating Composite Section
# Creating Composite Section for NanComp
nanCompPart = myModel.parts['NanComp']

# Set region for each part in NanComp
regionMatrix = nanCompPart.Set(faces=nanCompPart.instances['MatrixPart-1'].faces.getSequenceFromMask(('[#1]',),), name='Set-4')
regionNP = nanCompPart.Set(faces=nanCompPart.instances['NPPart-1'].faces.getSequenceFromMask(('[#1]',),), name='Set-5')

# Create a composite section for NanComp
myModel.CompositeShellSection(name='NanCompSec',
                              preIntegrate=OFF,
                              idealization=NO_IDEALIZATION,
                              symmetric=OFF,
                              thicknessType=UNIFORM,
                              poissonDefinition=DEFAULT,
                              thicknessModulus=None,
                              temperature=GRADIENT,
                              useDensity=OFF,
                              integrationRule=SIMPSON,
                              numIntPts=5,
                              amplitude=RAMP,
                              alpha=0.0,
                              beta=0.0,
                              compositeDamping=None)

# Assign section to each region
nanCompPart.SectionAssignment(region=regionMatrix,
                              sectionName='MatSec',
                              offset=0.0,
                              offsetType=MIDDLE_SURFACE,
                              offsetField='',
                              thicknessAssignment=FROM_SECTION)

nanCompPart.SectionAssignment(region=regionNP,
                              sectionName='NPSec',
                              offset=0.0,
                              offsetType=MIDDLE_SURFACE,
                              offsetField='',
                              thicknessAssignment=FROM_SECTION)

#NanCompPart = myModel.parts['NanComp']
#NanCompregion = NanCompPart.Set(faces=NanCompPart.faces.getSequenceFromMask(('[#1]',),), name='Set-3')
#NanCompPart.SectionAssignment(region=NanCompregion, sectionName='NanCompSec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')



# Create a step for the analysis
#myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE, timePeriod=1)



#Taking Care of Boundary Conditions

# Set edges for boundary conditions
#rightEdge = myInstance.edges.findAt(((1.0, 0.5, 0.0),))
#leftEdge = myInstance.edges.findAt(((0.0, 0.5, 0.0),))
#topEdge = myInstance.edges.findAt(((0.5, 1.0, 0.0),))

#leftEdgeSet = myAssembly.Set(edges=leftEdge, name='Left_Edge_Set')
#rightEdgeSet = myAssembly.Set(edges=rightEdge, name='Right_Edge_Set')

# Applying Boundary Conditions
#myModel.ConcentrationBC(name='BC1', createStepName='Step-1', region=leftEdgeSet, distributionType=UNIFORM, magnitude=1.0)
#myModel.ConcentrationBC(name='BC2', createStepName='Step-1', region=rightEdgeSet, distributionType=UNIFORM, magnitude=0.0)


# Seed edges for meshing
#myAssembly.seedEdgeByNumber(edges=leftEdge, number=100, constraint=FIXED)
#myAssembly.seedEdgeByNumber(edges=topEdge, number=100, constraint=FIXED)

# Generate mesh
#myAssembly.generateMesh(regions=(myInstance,))

# Assign Element Type
#import mesh
#region_2D4 = myInstance.sets['Set-1']
#elemType_2D4 = mesh.ElemType(elemCode=DC2D4, elemLibrary=STANDARD)
#myAssembly.setElementType(regions=region_2D4, elemTypes=(elemType_2D4,))

# Create an analysis job for the model and submit it.

#jobName = 'MassDiffusionJob'
#myJob = mdb.Job(name=jobName, model='MM', description='MassDiffusionTest')

# Wait for the job to complete.

#myJob.submit()
#myJob.waitForCompletion()

# Visualisation process
#import visualization
#myViewport = session.Viewport(name='Viewport1')
#myOdb = visualization.openOdb(path=jobName + '.odb')
#myViewport.setValues(displayedObject=myOdb)
#myViewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
#myViewport.odbDisplay.commonOptions.setValues(renderStyle=FILLED)