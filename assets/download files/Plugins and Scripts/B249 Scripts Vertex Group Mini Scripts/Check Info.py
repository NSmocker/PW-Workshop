import Blender
from Blender import Mesh, Object, Window
import os

clearConsole = True




if clearConsole:
    os.system('cls')  # очищає консоль



# Get the active object
obj = Object.GetSelected()[0]
me = obj.getData(mesh=1)

# Update the 3D view
Window.EditMode(0)

print("-----------------------")
print("Info about Vertexes")
# Get selected vertices
selected_verts = [v.index for v in me.verts if v.sel]
count = 0
if not selected_verts:
    print("No vertices selected.")
else:
    for i in selected_verts:
        influences = me.getVertexInfluences(i)
        print("Vertex #%d:" % i)

        if influences:
            for group, weight in influences:
                print("  Group: %s, Weight: %.3f" % (group, weight))
        else:
            print("  No group (influences)")
print("End of Info")
print("-----------------------")
Window.EditMode(1)
