import Blender
from Blender import Mesh, Object, Window
import os

clearConsole = True




if clearConsole:
    os.system('cls')  # очищає консоль

file = open("vgroup.txt", 'r')  # open file for reading
text = file.read()          # read all content
file.close()                # close the file
print("File loaded successfully!")




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



info_lines = text.split('\n')
print("info_lines:", info_lines[1:])
print("\n")

for line in info_lines[1:]:# skip first line of header
    parsed_line = line.split(':')
    group, weight = parsed_line[0], parsed_line[1]
    weight = float(weight)
    print(type(group))
    print(type(weight))
    print("Group:", group, "Weight:", weight)
    selectedObjectInfo.assignVertsToGroup(group,selectedVertexes, weight,Blender.Mesh.AssignModes.REPLACE)


    

