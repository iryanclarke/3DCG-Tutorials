# Imports
import maya.cmds as cmds

# To handle small double values close to zero
ZV = 0.00000000000000000001

# Close window if one already exists
if cmds.window(MyWin, exists=True):
    cmds.deleteUI(MyWin, window=True)

def checkIntersect():
    # Create two lists (objects & locators)
    selectedShapes = cmds.ls(selection=True)
    locatorList = []
    locatorCount = 0
    meshList = []
    for shape in selectedShapes:
        if(cmds.objectType(shape) == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
            if(cmds.objectType(childShape) == 'locator'):
                # Check if count is less than 2, then store them in the list
                if(locatorCount < 2):    locatorList.append(shape)
                else:    print "Too many locators, using two"
                
                # Use this as there is no 'i++' operator in python
                locatorCount += 1
            if(cmds.objectType(childShape) == 'mesh'):
                meshList.append(childShape)
    
    # Check that there are a enough locators, if not, then exit            
    if(locatorCount < 2):
        print "Select more locators, we need 2"
        return False    
    
    PtA = cmds.xform(locatorList[0], query=True, translation=True, worldSpace=True)
    PtB = cmds.xform(locatorList[1], query=True, translation=True, worldSpace=True)
    
    # Add in curve to see the intersection is
    cmds.curve(p =[PtA, PtB])
    
    # Passes in the values to the GUI for the text field groups
    cmds.textFieldGrp("uiPointA", edit=True, text=str(PtA))
    cmds.textFieldGrp("uiPointB", edit=True, text=str(PtB))
    
    # Cycle through each shape, and each facet
    intersectCount=0
    for mesh in meshList:
        facetCount = cmds.polyEvaluate(mesh, face=True)
        
        # This fixes the spheres being generated in the wrong place (local space instead of world)
        meshXNode = cmds.listRelatives(mesh, parent=True)
        meshXForm = cmds.xform(meshXNode, query=True, matrix=True, worldSpace=True)
                
        for face in range(0, facetCount):
            vtxLst = cmds.polyInfo((mesh[0] + ".f[" + str(face) + "]"), faceToVertex=True)
            vtxIdx = str(vtxLst[0]).split()
            vtxA = cmds.getAttr(mesh[0] + ".vt[" + vtxIdx[2] + "]")
            vtxB = cmds.getAttr(mesh[0] + ".vt[" + vtxIdx[3] + "]")
            vtxC = cmds.getAttr(mesh[0] + ".vt[" + vtxIdx[4] + "]")
            
            # This is to continue fixing local to world space
            # vtxNewA = list(vtxA[0])
            # vtxNewB = list(vtxB[0])
            # vtxNewC = list(vtxC[0])
            vtxNewA = matrixMult(meshXForm, list(vtxA[0]))
            vtxNewB = matrixMult(meshXForm, list(vtxB[0]))
            vtxNewC = matrixMult(meshXForm, list(vtxC[0]))
            
            
            planeEq = getPlaneEq(vtxNewA, vtxNewB, vtxNewC)
            sValueA = (planeEq[0]*PtA[0]) + (planeEq[1]*PtA[1]) + (planeEq[2]*PtA[2]) + planeEq[3]
            sValueB = (planeEq[0]*PtB[0]) + (planeEq[1]*PtB[1]) + (planeEq[2]*PtB[2]) + planeEq[3]
            
            # Adds a small where to that intersection point, and moved
            if(((sValueA > 0.0) and (sValueB < 0.0)) or ((sValueA < 0.0) and (sValueB > 0.0))):
                tValue = getTValue(planeEq, PtA, PtB)
                PtI = [0.0, 0.0, 0.0]
                PtI[0] = PtA[0] + (tValue * (PtB[0] - PtA[0])) 
                PtI[1] = PtA[1] + (tValue * (PtB[1] - PtA[1]))
                PtI[2] = PtA[2] + (tValue * (PtB[2] - PtA[2]))
                cmds.polySphere(r=0.1)
                cmds.move(PtI[0], PtI[1], PtI[2])
                
                # Adding elements to the text scroll list
                ptText = "[" + str(intersectCount) + "] " + str(PtI[0]) + ", " + str(PtI[1]) +", " + str(PtI[2])
                cmds.textScrollList('uiPointList', edit=True, append=[ptText])
                intersectCount += 1
                
                                        
# Ze plane equation!
def getPlaneEq(VtxA, VtxB, VtxC):
    planeEq = [0.0, 0.0, 0.0, 0.0]
    planeEq[0] = (VtxA[1] * (VtxB[2]-VtxC[2])) + (VtxB[1] * (VtxC[2]-VtxA[2])) + (VtxC[1] * (VtxA[2]-VtxB[2]))
    planeEq[1] = (VtxA[2] * (VtxB[0]-VtxC[0])) + (VtxB[2] * (VtxC[0]-VtxA[0])) + (VtxC[2] * (VtxA[0]-VtxB[0]))
    planeEq[2] = (VtxA[0] * (VtxB[1]-VtxC[1])) + (VtxB[0] * (VtxC[1]-VtxA[1])) + (VtxC[0] * (VtxA[1]-VtxB[1]))
    planeEq[3] = (VtxA[0] * ((VtxB[1]*VtxC[2])-(VtxC[1]*VtxB[2]))) + (VtxB[0] * ((VtxC[1]*VtxA[2])-(VtxA[1]*VtxC[2]))) + (VtxC[0] * ((VtxA[1]*VtxB[2])-(VtxB[1]*VtxA[2])))
    planeEq[3] = -(planeEq[3])
    
    # Check if they are colinear
    if((abs(planeEq[0]) < ZV) and (abs(planeEq[1]) < ZV) and (abs(planeEq[2]) < ZV)):
        print("Error Points are colinear")
        return False
    
    return planeEq 

# T value is the value (0 to 1) along the line (where there is intersection)
def getTValue(pEq, PtA, PtB):
    # Denominator and numerator
    denEq = 0.0
    nomEq = 0.0
    
    denEq = (pEq[0] * (PtA[0] - PtB[0]))+(pEq[1]*(PtA[1]-PtB[1]))+(pEq[2]*(PtA[2]-PtB[2]))
    if(abs(denEq) < ZV):
        print "Denominator is Zero"
        return False
    
    nomEq = (pEq[0] * PtA[0]) + (pEq[1] * PtA[1]) + (pEq[2] * PtA[2]) + pEq[3]
    return(nomEq/denEq)

# Matrix Multiplication
def matrixMult(Mtx, Pt):
    PtOut = [0.0, 0.0, 0.0, 0.0]
    # Convert to Homogeneous point
    PtIn = [Pt[0], Pt[1], Pt[2], 1]   
    PtOut[0] = (Mtx[0]*PtIn[0])+(Mtx[4]*PtIn[1])+(Mtx[8]*PtIn[2])+(Mtx[12]*PtIn[3])
    PtOut[1] = (Mtx[1]*PtIn[0])+(Mtx[5]*PtIn[1])+(Mtx[9]*PtIn[2])+(Mtx[13]*PtIn[3])
    PtOut[2] = (Mtx[2]*PtIn[0])+(Mtx[6]*PtIn[1])+(Mtx[10]*PtIn[2])+(Mtx[14]*PtIn[3])
    PtOut[3] = (Mtx[3]*PtIn[0])+(Mtx[7]*PtIn[1])+(Mtx[11]*PtIn[2])+(Mtx[15]*PtIn[3])
    return (PtOut)
    
    
    
     
    
# Create basic window        
MyWin = cmds.window(title='My UI', menuBar=True, widthHeight=(500,300))
cmds.columnLayout( columnAttach=('left', 5), rowSpacing=10, columnWidth=500)
cmds.button( label='Check Intersection', command='checkIntersect()')

cmds.textFieldGrp('uiPointA', width=500, label='Point A')
cmds.textFieldGrp('uiPointB', width=500, label='Point B')

cmds.setParent("..")

cmds.paneLayout()
cmds.textScrollList('uiPointList', numberOfRows=8, allowMultiSelection=False)

cmds.showWindow(MyWin)