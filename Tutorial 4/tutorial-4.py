import maya.cmds as cmds

def updateCurve():
    selectedShapes = cmds.ls(selection=True)
    for shape in selectedShapes:
        if(cmds.objectType(shape) == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
            print "Found:" + cmds.objectType(childShape)
            if(cmds.objectType(childShape) == 'bezierCurve'):
                print "Editing Curve: " + str(childShape)
                xyzPos = [0.0, 0.0, 0.0]
                xyzPos = cmds.pointOnCurve(childShape, pr=0.0, p=True, top=True)
                print xyzPos
                
                newCurve = cmds.curve(p=xyzPos)
                vVal = cmds.floatSliderGrp("shakeVert", query=True, value=True)
                hVal = cmds.floatSliderGrp("shakeHorz", query=True, value=True)
                fVal = cmds.intSliderGrp("shakeFreq", query=True, value=True)
                
                noiseVec = [0.0, 0.0, 0.0]
                xyzNew = [0.0, 0.0, 0.0]
                
                # Loop over the intermediate points, adding noise to the values in order to create the shake we desire
                for i in range (0, fVal):
                    tVal = float(i) / float(fVal)
                    xyzPos = cmds.pointOnCurve(childShape, pr=tVal, p=True, top=True)
                    # Add noise to the curve (NOT make a new one) using a MEL command
                    noiseVec = maya.mel.eval("noise " + str(i))
                    xyzNew[0] = xyzPos[0] + (vVal * noiseVec)
                    xyzNew[1] = xyzPos[1] + (vVal * noiseVec)
                    xyzNew[2] = xyzPos[2]
                    # 'a' specifies that we are adding points to the curve
                    cmds.curve(newCurve, a=True, p=xyzNew)
                
                # Add final position on the curve so it ends where it originally ended (with no shake)
                xyzPos = cmds.pointOnCurve(childShape, pr=1.0, p=True, top=True)
                cmds.curve(newCurve, a=True, p=xyzNew)
                    

if cmds.window(CamWin, exists=True):
    cmds.deleteUI(CamWin, window=True)
    
CamWin = cmds.window(title='Cameras', widthHeight=(500,300))
    
cmds.columnLayout(columnWidth=500)
cmds.frameLayout(collapsable=True, label="SHaker Attributes", width=500)

cmds.floatSliderGrp("shakeVert", s=0.01, min=0, max=1, v=0.5, label="Vertical Shake", field=True)
cmds.floatSliderGrp("shakeHorz", s=0.01, min=0, max=1, v=0.5, label="Horizontal Shake", field=True)
cmds.intSliderGrp("shakeFreq", s=5, min=5, max=100, v=10, label="Frequency", field=True)


cmds.columnLayout(columnAttach=('left', 5), width=120)
cmds.button(label="Update Curve", command="updateCurve()")

cmds.setParent("..")

cmds.showWindow(CamWin)