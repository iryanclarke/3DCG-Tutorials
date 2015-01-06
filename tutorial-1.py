# Imports
import maya.cmds as cmds

# Defining a function
def createSphere() :
    # Query values from the float and int slider for sphere creation
    rValue = cmds.floatSliderGrp(sphereRadius, query=True, value=True)
    sValue = cmds.intSliderGrp(sphereSubDivs, query=True, value=True)
    # Creating Sphere from above variables
    cmds.polySphere(r=rValue, sx=sValue, sy=sValue)
    cmds.scale(1, 1, 4)

# Close window if it exisits    
if cmds.window(MyWin, exists=True) :
   cmds.deleteUI(MyWin, window=True)

# Creates a new window object with title My UI
MyWin = cmds.window(title='My UI', menuBar=True, widthHeight=(500,300))

# Creates a menu with two options
cmds.menu( label='File' )
cmds.menuItem( label='New Scene', command=('cmds.file ( force=True, new=True )'))
cmds.menuItem( label='Close', c=('cmds.deleteUI(\"' + MyWin + '\", window=True) '))

cmds.columnLayout( columnAttach=('right', 5), rowSpacing=10, columnWidth=400)

# Adds in a float and int slider for Radius and Subdivisions
sphereRadius = cmds.floatSliderGrp( label='Radius', field=True, minValue=0.0, maxValue=10.0, value=1.0)
sphereSubDivs = cmds.intSliderGrp( label='Subdivisions', field=True, minValue=10, maxValue=100, value=10)

# Creates buttons to perform the label actions
cmds.button( label='Create Sphere', command='createSphere()')
cmds.button( label='Clear Scene', command=('cmds.file( force=True, new=True ) ') )
cmds.button( label='Close', command=('cmds.deleteUI(\"' + MyWin + '\", window=True) '))

cmds.setParent("..")

# Creates the window object
cmds.showWindow(MyWin)