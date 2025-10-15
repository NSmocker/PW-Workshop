import Blender
from Blender import Mesh, Object, Window
import os

clearConsole = True




if clearConsole:
    os.system('cls')  # очищає консоль


# Get the active object
selectedObject = Object.GetSelected()[0]
selectedObjectInfo = selectedObject.getData(mesh=1)

# Update the 3D view
Window.EditMode(0)

print("-----------------------")
print("Info about Vertexes")
# Get selected vertices
selectedVertexes = [v.index for v in selectedObjectInfo.verts if v.sel]
print("Selected Vertexes:", selectedVertexes)

firstSelectedVertexInflances = selectedObjectInfo.getVertexInfluences(selectedVertexes[0])
print("firstSelectedVertexInflances:", firstSelectedVertexInflances)


textForSerialization = "Group:Width"
for group, weight in firstSelectedVertexInflances:
    textForSerialization += "\n"+group+":"+str(weight)

try:
    file = open("vgroup.txt", 'w')  # open file for writing
    file.write(textForSerialization)            # write the text
    file.close()                # close the file
    print("File saved successfully!")
except IOError:
    print("Error: could not write the file.")
print("Groups serialized")
print("-----------------------")
Window.EditMode(1)
