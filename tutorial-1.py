# Dis a comment yeee
import maya.cmds as cmds
if cmds.window(MyWin, exists=True) :
   cmds.deleteUI(MyWin, window=True)

MyWin = cmds.window(title='My UI', menuBar=True, widthHeight=(500,300))

cmds.menu( label='File' )
cmds.menuItem( label='New Scene', command=('cmds.file ( force=True, new=True )'))
cmds.menuItem( label='Close', c=('cmds.deleteUI(\"'+MyWin+'\", window=True) '))

cmds.showWindow(MyWin)