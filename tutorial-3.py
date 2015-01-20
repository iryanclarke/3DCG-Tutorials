# Imports
import maya.cmds as cmds

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
    
    PtA = cmds.xform(locatorList[0], query=True, translation=True, worldSPace=True)
    PtB = cmds.xform(locatorList[1], query=True, translation=True, worldSPace=True)
    
    # Cycle through each shape, and each facet
    intersectCount=0
    for mesh in meshList:
        facetCount = cmds.polyEvaluate(mesh, face=True)
        
MyWin = cmds.window(title='My UI', menuBar=True, widthHeight=(500,300))

# Create basic window
cmds.columnLayout( columnAttach=('left', 5), rowSpacing=10, columnWidth=500)
cmds.button( label='Check Intersection', command='checkIntersect()')

cmds.showWindow(MyWin)