# Imports
import maya.cmds as cmds
import random

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
    
    for shape in selectedShapes:
        # Returns the type of a given shape
        shapeType = cmds.objectType(shape)
        # If it is a transform, we need to get the children
        if(shapeType == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
            # If it is not a mesh, go to the beginning of the loop again
            if(cmds.objectType(childShape) != 'mesh'):    continue
            adjustSelectedObject(action, direction, shape)

def adjustSelectedObject(action, direction, object):
    # Polyevaluate counts the number of faces here
    facetCount = cmds.polyEvaluate(object, face=True)
    
    # Both of these return 3 values: x,y,z, and is finding the location of the object (cube) and space locator (myRef)
    posShape = cmds.xform(object, query=True, translation=True, worldSpace=True)
    posRef = cmds.xform('myRef', query=True, translation=True, worldSpace=True)
    
    # This calculates the vector between reference & shape
    objVec = [0,0,0]
    objVec[0] = posShape[0] - posRef[0]
    objVec[1] = posShape[1] - posRef[1]
    objVec[2] = posShape[2] - posRef[2]
    
    updateFace = False
    # polyInfo is returning the vertex indices only, not xyz
    for face in range(0, facetCount):
        # F is the face, and you are extracting the vertices of that face
        vtxLst = cmds.polyInfo(object + ".f[" + str(face) + "]", faceToVertex=True)
                
        # Convert vtxLst to a string, and then split into a proper array
        vtxIdx = str(vtxLst[0]).split()
        vtxA = cmds.getAttr(object + ".vt[" + vtxIdx[2] + "]") 
        vtxB = cmds.getAttr(object + ".vt[" + vtxIdx[3] + "]") 
        vtxC = cmds.getAttr(object + ".vt[" + vtxIdx[4] + "]")
        
        # [u'FACE      0:      0      1      3      2 \n']
        # We don't use the last number because we already have 3 verticies, and thats all we need
        
        # We need to convert it to a list, as Maya returns a tuple(), and that ISNT NICE DUDE
        fN = getNormal(vertexA=list(vtxA[0]), vertexB=list(vtxB[0]), vertexC=list(vtxC[0]))
        dP = getDotProduct(fN, objVec)
        
        # Multiply your normal vector by a random number
        fN[0] = fN[0] * random.random()
        fN[1] = fN[1] * random.random()
        fN[2] = fN[2] * random.random()
       
        # IF YOU EVER SEE -0.0, its because of how floats work
        
        updateFace = False
        if(direction == "acute" and dP < 0.0):    updateFace = True
        if(direction == "obtuse" and dP > 0.0):    updateFace = True
        if(direction == "right" and dP == 0.0):    updateFace = True
        if(direction == "all"):    updateFace = True
        
        # Extrudes faces that face the locator
        if(updateFace == True):
            theFace = object + ".f[" + str(face) + "]"
            if(action == "del"):
                cmds.polyDelFacet(theFace)
            if(action == "extrude"):
                cmds.polyExtrudeFacet(theFace, t=[fN[0], fN[1], fN[2]])

def getNormal(vertexA, vertexB, vertexC):
    vecA = [0,0,0]
    vecB = [0,0,0]
    
    # Getting vector A
    vecA[0] = vertexB[0] - vertexA[0]    
    vecA[1] = vertexB[1] - vertexA[1]
    vecA[2] = vertexB[2] - vertexA[2]   
    # Getting vector B
    vecB[0] = vertexC[0] - vertexA[0]    
    vecB[1] = vertexC[1] - vertexA[1]
    vecB[2] = vertexC[2] - vertexA[2]     
    
    # Cross product
    nrmVec = [0,0,0]
    nrmVec[0] = (vecA[1] * vecB[2]) - (vecA[2] * vecB[1])  
    nrmVec[1] = (vecA[2] * vecB[0]) - (vecA[0] * vecB[2]) 
    nrmVec[2] = (vecA[0] * vecB[1]) - (vecA[1] * vecB[0]) 
    
    # '**' means to the power of, so '** 0.5' is square root
    nrmMag = ((nrmVec[0] ** 2) + (nrmVec[1] ** 2) + (nrmVec[2] ** 2)) ** 0.5
    
    # To get normal vector, vectors are divided by vector magnitude
    nrmVec[0] = nrmVec[0] / nrmMag
    nrmVec[1] = nrmVec[1] / nrmMag
    nrmVec[2] = nrmVec[2] / nrmMag
    
    return nrmVec

def getDotProduct(vtxA, vtxB):
    result = (vtxA[0] * vtxB[0]) + (vtxA[1] * vtxB[1]) + (vtxA[2] *vtxB[2])
    return result    
        
                
                                
                                                                
# Create a locator
createLocator()

# Creates poly cube and performs an absolute transform (Dimensions of 5 x 5 x5, and uses a homogeneous matrix (4x4)to transform)
# cmds.polyCube(n="myCube", h=5, w=5, d=5)
cmds.polySphere(n="mySphere", r=10)
cmds.xform(a=True, m=(1,0,0,0,0,1,0,0,0,0,1,0,-10,2.5,-10,1))


adjustSelected("extrude", "all")
## adjustSelected("del", "obtuse")
