from abaqus import *
from abaqusConstants import *

# Create a new model
myModel = mdb.Model(name='MatrixModel')

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

# Set edges for left and right edges
left_edge = [edge for edge in myPart.edges if abs(edge.pointOn[0][0]-0.0) < 1e-6]
right_edge = [edge for edge in myPart.edges if abs(edge.pointOn[0][0]-1.0) < 1e-6]

# Create sets for left and right edges
left_edge_set = myAssembly.Set(edges=left_edge, name='Left_Edge_Set')
right_edge_set = myAssembly.Set(edges=right_edge, name='Right_Edge_Set')

# Apply Concentration BC to left and right edges
myModel.ConcentrationBC(name='Left_BC', createStepName='Step-1', region=left_edge_set, 
    distributionType=UNIFORM, concentration=1.0)
myModel.ConcentrationBC(name='Right_BC', createStepName='Step-1', region=right_edge_set, 
    distributionType=UNIFORM, concentration=0.0)


# Seed edges for meshing
myAssembly.seedEdgeByNumber(edges=myPart.edges, number=10, constraint=FIXED)

# Generate mesh
myAssembly.generateMesh()

# Assign element type
myAssembly.setElementType(regions=(myPart.faces,), elemTypes=(ElemType(elemCode=DC2D4, elemLibrary=STANDARD), ElemType(elemCode=DC2D3, elemLibrary=STANDARD)))

# Create a step for the analysis
myModel.MassDiffusionStep(amplitude=RAMP, name='Step-1', previous='Initial', response=STEADY_STATE)

# Create a job and submit
myJob = mdb.Job(name='Job-1', model='MatrixModel')
myJob.submit()

# Create output requests
myModel.FieldOutputRequest(name='F-Output-1', createStepName='Step-1', variables=('MISC', 'CONCENTRATION', 'FLUX'))

# Create monitor points
myAssembly.Monitor(name='Monitor-1', createStepName='Step-1', region=
    myPart.edges.findAt(((0.0, 0.5, 0.0),)), 
    variables=('MISC', 'CONCENTRATION', 'FLUX'))
myAssembly.Monitor(name='Monitor-2', createStepName='Step-1', region=
    myPart.edges.findAt(((1.0, 0.5, 0.0),)), 
    variables=('MISC', 'CONCENTRATION', 'FLUX'))
