from abaqus import *
from abaqusConstants import *

# Create a new model
myModel = mdb.Model(name='Model-1')

# Create a sketch for the profile
mySketch = myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
mySketch.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))

# Create a part and base shell on the sketch
myPart = myModel.Part(name='Part-1', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
myPart.BaseShell(sketch=mySketch)

# Create a material and define properties
myMaterial = myModel.Material(name='Material-1')
myMaterial.Diffusivity(table=((0.005, 0.0),))
myMaterial.Solubility(table=((1.0,),))

# Create a section and assign the material
mySection = myModel.HomogeneousSolidSection(material='Material-1', name='Section-1', thickness=None)
region = myPart.Set(faces=myPart.faces.getSequenceFromMask(('[#1 ]',),), name='Set-1')
myPart.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='')

# Define sets for boundary conditions
leftEdge = myPart.edges.findAt((0.0, 0.5, 0.0))
rightEdge = myPart.edges.findAt((1.0, 0.5, 0.0))
myAssembly = myModel.rootAssembly
leftEdgeSet = myAssembly.Set(edges=leftEdge, name='Left_Edge_Set')
rightEdgeSet = myAssembly.Set(edges=rightEdge, name='Right_Edge_Set')

# Apply concentration boundary conditions
myModel.ConcentrationBC(name='Left_BC', createStepName='Step-1', region=leftEdgeSet, 
    distributionType=UNIFORM, concentration=1.0)
myModel.ConcentrationBC(name='Right_BC', createStepName='Step-1', region=rightEdgeSet, 
    distributionType=UNIFORM, concentration=0.0)

# Seed edges for meshing
myAssembly.seedEdgeByNumber(edges=leftEdge, number=100, constraint=FIXED)
myAssembly.seedEdgeByNumber(edges=rightEdge, number=100, constraint=FIXED)

# Generate mesh
myAssembly.generateMesh()

# Assign element type
myAssembly.setElementType(regions=(myPart.faces,), elemTypes=(ElemType(elemCode=DC2D4, elemLibrary=STANDARD), ElemType(elemCode=DC2D3, elemLibrary=STANDARD)))

# Create a step for the analysis
myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE)

# Create a job and submit
myJob = mdb.Job(name='Job-1', model='Model-1')
myJob.submit()

# Create output requests
myModel.FieldOutputRequest(name='F-Output-1', createStepName='Step-1', variables=('MISC', 'CONCENTRATION', 'FLUX'))

# Create monitor points
myAssembly.Monitor(name='Monitor-1', createStepName='Step-1', region=leftEdgeSet, variables=('MISC', 'CONCENTRATION', 'FLUX'))
myAssembly.Monitor(name='Monitor-2', createStepName='Step-1', region=rightEdgeSet, variables=('MISC', 'CONCENTRATION', 'FLUX'))
