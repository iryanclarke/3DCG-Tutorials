# Imports
import maya.cmds as cmds
import random

cmds.file(force=True, new=True)

testMesh = "wavyMesh"
cmds.polyPlane(w=20.0, h=20.0, sx=30, sy=10, n=testMesh)
cmds.move(0.0, 1.0, 0.0, a=True)

# Deforming the plane using a non linear sine deformer
cmds.nonLinear(type="sine", amplitude=0.05)
cmds.setAttr('sine1.wavelength', 0.2)
cmds.setAttr('sine1Handle.rotateY', 180)
cmds.setAttr('sine1Handle.rotateZ', 90)

cmds.delete(testMesh, ch=True)

# Create the target mesh
targetMesh = "targetMesh"
cmds.polyPlane(w=20.0, h=20.0, sx=1, sy=1, n=targetMesh)
cmds.move(0.0, 0.5, 0.0, a=True)