# Imports
import maya.cmds as cmds

ZV = 0.00000000001 

#if cmds.window(MyWin, exists=True):
 #  cmds.deleteUI(MyWin, window=True)
 
#
# Primary Function
#

def findIntersect():
    # Make sure items are selected
    selectedShape = cmds.ls(selection=True)
     
    # Check to make sure objects have been selected
    if(len(selectedShape) == 2):
        # Get Sphere vertexes and center
        sphereVertex = getVertices(selectedShape[0])
        sphereCentre = cmds.objectCenter(selectedShape[0], gl=True)
         
        # Loop through all sphere vertexes
        for vertex in sphereVertex:
             
            # Draw lines from center of cube to circle vertexes
            cmds.curve( p=[sphereCentre, vertex] )
                         
            # Now check intersection of each line on the cube
            drawCubes(selectedShape[1], sphereCentre, vertex)
           
             
    # Error handling       
    else:
        print "Please select 2 shapes"
 
#
# Secondary Functions
#
 
# Determines where the line intersects the cube and draws little cube there
def drawCubes(theCube, linePt1, linePt2):
            
    # Ensure to list the relatives of the cube in order to actually find its location, otherwise it will return a non when performing the listR
    cubeShape = cmds.listRelatives(theCube, fullPath=True, shapes=True) 
                       
    # Get number of facets from cube
    facetCount = cmds.polyEvaluate(cubeShape, face=True)
     
    # Fixes local coordinate system to absolute position in world by finding the transform node matrix
    cubeRelatives = cmds.listRelatives(cubeShape,parent=True)
    cubeTransform = cmds.xform(cubeRelatives, query=True, matrix=True, worldSpace=True)
    
     
    for facet in range(0, facetCount):
        # Fetching vertex x,y,z coordinates of each facet
        vertexList = cmds.polyInfo((theCube + ".f[" + str(facet) + "]"), faceToVertex=True)
        vtxIdx = str(vertexList[0]).split()
        vertexA = cmds.getAttr(theCube  + ".vt[" + vtxIdx[2] + "]")
        vertexB = cmds.getAttr(theCube  + ".vt[" + vtxIdx[3] + "]")
        vertexC = cmds.getAttr(theCube  + ".vt[" + vtxIdx[4] + "]")
         
        # Turning the tuple into a list, python is mean, and also converting from local space to world
        newVertexA = mutiplyMatrices(cubeTransform, list(vertexA[0]) )
        newVertexB = mutiplyMatrices(cubeTransform, list(vertexB[0]) )
        newVertexC = mutiplyMatrices(cubeTransform, list(vertexC[0]) )
                 
        planeEq = getPlaneEquation(newVertexA, newVertexB, newVertexC)
        print planeEq 
        
        # Determine if the points are on opposite sides of the plane        
        sValueA = (planeEq[0]*linePt1[0])+(planeEq[1]*linePt1[1])+(planeEq[2]*linePt1[2]) + planeEq[3]
        sValueB = (planeEq[0]*linePt2[0])+(planeEq[1]*linePt2[1])+(planeEq[2]*linePt2[2]) + planeEq[3]
        
        if(((sValueA>0.0) and (sValueB<0.0)) or ((sValueA<0.0) and (sValueB>0.0))):
            t = 0.0
            t = getT(planeEq, linePt1, linePt2)
         
            planePoint = [0.0, 0.0, 0.0]
            planePoint[0] = linePt1[0] + (t * (linePt2[0] - linePt1[0]))
            planePoint[1] = linePt1[1] + (t * (linePt2[1] - linePt1[1]))
            planePoint[2] = linePt1[2] + (t * (linePt2[2] - linePt1[2]))
            cmds.polyCube(width=0.1, height=0.1, depth=0.1)
            cmds.move(planePoint[0], planePoint[1], planePoint[2])
             
             
            # Adding elements to the text scroll list
            ptText = "[" + str(facet) + "] " + str(planePoint[0]) + ", " + str(planePoint[1]) +", " + str(planePoint[2])
            cmds.textScrollList('intersectList', edit=True, append=[ptText])
 
 
     
#                                                                    #
# Tertiary functions (resusable, dot, cross, normal calculations)    #
#                                                                    #
 

# Plane equation!
def getPlaneEquation(VertexA, VertexB, VertexC):
    #planeEq = [0.0, 0.0, 0.0, 0.0]
    #planeEq[0] = (VertexA[1] * (VertexB[2]-VertexC[2])) + (VertexB[1] * (VertexC[2]-VertexA[2])) + (VertexC[1] * (VertexA[2]-VertexB[2]))
    #planeEq[1] = (VertexA[2] * (VertexB[0]-VertexC[0])) + (VertexB[2] * (VertexC[0]-VertexA[0])) + (VertexC[2] * (VertexA[0]-VertexB[0]))
    #planeEq[2] = (VertexA[0] * (VertexB[1]-VertexC[1])) + (VertexB[0] * (VertexC[1]-VertexA[1])) + (VertexC[0] * (VertexA[1]-VertexB[1]))
    #planeEq[3] = (VertexA[0] * ((VertexB[1]*VertexC[2])-(VertexC[1]*VertexB[2]))) + (VertexB[0] * ((VertexC[1]*VertexA[2])-(VertexA[1]*VertexC[2]))) + (VertexC[0] * ((VertexA[1]*VertexB[2])-(VertexB[1]*VertexA[2])))
    #planeEq[3] = -(planeEq[3])
    
    # Plane euation is Ax + By + Cz + D, and ABC is the normal vector
    
    # Create empty array
    normalPoints = [0.0, 0.0, 0.0]
    
    # Need to get ABC, so we need to find the normal
    normalPoints = getNormal(VertexA, VertexB, VertexC)
    
    # Now need to solve for D, as we have ABC now
    valueD = 0.0
    valueD += normalPoints[0] * VertexA[0]
    valueD += normalPoints[1] * VertexA[1]
    valueD += normalPoints[2] * VertexA[2]
    
    # Now create plane equation 
    planeEq = [0.0, 0.0, 0.0, 0.0]
    
    #for i in range(0,2):
    
    planeEq[0] = normalPoints[0]
    planeEq[1] = normalPoints[1]
    planeEq[2] = normalPoints[2]
    
    # Make value negative as we solved for D on the right hand side, Ax + By + Cz = D
    planeEq[3] = -valueD
    
    # Check if they are colinear
    if((abs(planeEq[0]) < ZV) and (abs(planeEq[1]) < ZV) and (abs(planeEq[2]) < ZV)):
        print("Error Points are colinear")
        return False
    return planeEq 


# Gets the normal vector of passed in three points
def getNormal(pointA, pointB, pointC):
    # Need to create lines from the passed in points
    line1 = [0.0, 0.0, 0.0]
    line2 = [0.0, 0.0, 0.0]
    
    line1[0] = pointA[0] - pointC[0]
    line1[1] = pointA[1] - pointC[1]
    line1[2] = pointA[2] - pointC[2]
    
    line2[0] = pointB[0] - pointC[0]
    line2[1] = pointB[1] - pointC[1]
    line2[2] = pointB[2] - pointC[2]
    
    # Now perform cross product on two lines for the perpendicular line (normal)
    normal = getCrossProduct( line1, line2 )
    return normal
 
# Gets the verticies of the selected shape
def getVertices( shapeSelected ):
    # Create array of vertex positions
    vertexWorldPosition = []
    vertexList = cmds.getAttr( shapeSelected + ".vrts", multiIndices=True )
     
    # Loop through all the points
    for point in vertexList :
        curPointPosition = cmds.xform( str( shapeSelected ) + ".pnts[" + str(point) + "]" , query=True, translation=True, worldSpace=True )
        # Put it into an array for accessing
        vertexWorldPosition.append( curPointPosition )
  
    return vertexWorldPosition
 
        
# Cross product, returns the normal vector
def getCrossProduct(point1, point2):
    crossX = ( point1[1] * point2[2]) - (point1[2] - point2[1] )
    crossY = ( point1[2] * point2[0]) - (point1[0] - point2[2] )
    crossZ = ( point1[0] * point2[1]) - (point1[1] - point2[0] )
    return [ crossX, crossY, crossZ ]
 
# Dot product, returns the magnitude
def getDotProduct(normal, pointA):
    dotProduct = [0.0, 0.0, 0.0]
    dotProduct[0] = normal[0] * pointA[0]
    dotProduct[1] = normal[1] * pointA[1]
    dotProduct[2] = normal[2] * pointA[2]
    return dotProduct
 
# Get the t value, or where along the line where the intersection is 
def getT(planeEq, point1, point2): #CHANGEERERE
    denominator = 0.0
    numerator = 0.0
     
    denominator = ( planeEq[0] * (point1[0]-point2[0]) ) + ( planeEq[1] * (point1[1]-point2[1]) ) + (planeEq[2]*(point1[2]-point2[2]))
    # Ensure denominator is not zero
    if( abs(denominator) < 0.00000001 ):
        print "I can't divide by zero silly!"
        return False
     
    numerator = ( planeEq[0] * point1[0] ) + ( planeEq[1] * point1[1] ) + ( planeEq[2] * point1[2] ) + planeEq[3]
    return (numerator/denominator)
     
# Matrix Multiplication for converting to global space, not local
def mutiplyMatrices(transformedMesh, point):
    # Initialize the new global point
    globalPoint = [0.0, 0.0, 0.0, 0.0]
     
    # Convert local point to a homogenous one
    localPoint = [point[0], point[1], point[2], 1]
     
    #for i in range(0, 3):
        #globalPoint[i] = ( transformedMesh[i]*localPoint[0] ) + ( transformedMesh[i + 3]*localPoint[1] ) + ( transformedMesh[i + 8]*localPoint[2] ) + ( transformedMesh[i + 12]*localPoint[3] )
    globalPoint[0] = (transformedMesh[0]*localPoint[0])+(transformedMesh[4]*localPoint[1])+(transformedMesh[8]*localPoint[2])+(transformedMesh[12]*localPoint[3])
    globalPoint[1] = (transformedMesh[1]*localPoint[0])+(transformedMesh[5]*localPoint[1])+(transformedMesh[9]*localPoint[2])+(transformedMesh[13]*localPoint[3])
    globalPoint[2] = (transformedMesh[2]*localPoint[0])+(transformedMesh[6]*localPoint[1])+(transformedMesh[10]*localPoint[2])+(transformedMesh[14]*localPoint[3])
    globalPoint[3] = (transformedMesh[3]*localPoint[0])+(transformedMesh[7]*localPoint[1])+(transformedMesh[11]*localPoint[2])+(transformedMesh[15]*localPoint[3])
    return (globalPoint)     
     
     
 
MyWin = cmds.window(title='My UI', menuBar=False, widthHeight=(500,300))
cmds.columnLayout( columnAttach=('left', 5), rowSpacing=10, columnWidth=500)
cmds.button(label='Find Intersections', command='findIntersect()')
cmds.setParent("..")
 
cmds.paneLayout()
cmds.textScrollList('intersectList', numberOfRows=8, allowMultiSelection=False)
 
cmds.showWindow(MyWin)