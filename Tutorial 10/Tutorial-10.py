# Imports
import maya.cmds as cmds
import random

cmds.file(force=True, new=True)

testMash = "perturbedMesh"
cmds.polyPlane(w=20.0, h=20.0, sx=40, sy=40, n=testMesh)
cmds.move(0.0, 1.0, 0.0, a=True)

vCount = cmds.polyEvaluate(v=True)

# Loop through all of the points
for i in xrange(0, vCount, 2):
    vtxNum = str(i)
    cmds.select(testMesh+".vtx["+vtxNum+"]")
    # Displace the point by a certain point
    tmpValue = random.uniform(-0.5, 0.5)
    cmds.move(0.0, tmpValue, 0.0, r=True)