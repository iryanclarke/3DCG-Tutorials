# Imports
import maya.cmds as cmds

# Makes sure scene is clear and fresh
cmds.file(force=True, new=True)

# Locator function to check if locator exists, and if not, makes one
def createLocator():
    if(cmds.objExists('myRef')):
        print "myRef Exists\n"
        return
    cmds.spaceLocator(n='myRef')
    cmds.move(20, 5, 20)
    print "myRef Created\n"

# Performs adjustments on selected object
def adjustSelected(action, direction):
    # Returns a list of selected objects
    selectedShapes = cmds.ls(selection=True)
    # Loop through all shapes 
    for shape in selectedShapes:
        # Returns the type of a given shape
        shapeType = cmds.objectType(shape)
    
# Create a locator
createLocator()

# Creates poly cube and performs an absolute transform (Dimensions of 5 x 5 x5, and uses a homogeneous matrix (4x4)to transform)
cmds.polyCube(n="myCube", h=5, w=5, d=5)
cmds.xform(a=True, m=(1,0,0,0,0,1,0,0,0,0,1,0,-10,2.5,-10,1))


adjustSelected("extrude", "acute")
# Run through selected shapes