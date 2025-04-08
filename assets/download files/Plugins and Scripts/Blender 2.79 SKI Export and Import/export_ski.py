import os
import sys
import struct
import bpy.utils
import time
#from shutil import copyfile
from bpy_extras.io_utils import ExportHelper

from bpy.props import StringProperty, BoolProperty, EnumProperty ,IntProperty
from bpy.types import Operator
from bpy_extras.io_utils import create_derived_objects, free_derived_objects

ERROR = False ;

def Grups (self,mesh,Slovar,Slovar_bone,ob,j,B):
    Weight = {}
    Grup = {}
    
    #Стандартна вигрузка костей
    if self.download_bones == "Complete_bones" :
        Weight =[0,0,0,0]
        Grup = [0,0,0,0]
        for s in range(len(mesh.vertices[j].groups)) :
            bone_num = Slovar[B][str(mesh.vertices[j].groups[s].group)]
            Weight[bone_num] = (mesh.vertices[j].groups[s].weight )
            Grup[bone_num] = ( Slovar_bone[Slovar[B][mesh.vertices[j].groups[s].group]] ) 
             
    #Повна вигрузка костей _ Можливо неправельно
    if self.download_bones == "Experement_bones" :
        if len(mesh.vertices[j].groups) == 0 :
                Weight = (0,0,0,0)
                Grup = (0,0,0,0)
        if len(mesh.vertices[j].groups) == 1 :
                Weight = (mesh.vertices[j].groups[0].weight,0,0,0)
                Grup = (Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[0].group].name],0,0,0)
                
        if len(mesh.vertices[j].groups) == 2 :
                Weight = (mesh.vertices[j].groups[0].weight, mesh.vertices[j].groups[1].weight,0,0)
                Grup = (Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[0].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[1].group].name],0,0)
        
        if len(mesh.vertices[j].groups) == 3 :
                Weight = (mesh.vertices[j].groups[0].weight,mesh.vertices[j].groups[1].weight,mesh.vertices[j].groups[2].weight,0)
                Grup = (Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[0].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[1].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[2].group].name],0)
        
        if len(mesh.vertices[j].groups) == 4 :
                Weight = (mesh.vertices[j].groups[0].weight, mesh.vertices[j].groups[1].weight, mesh.vertices[j].groups[2].weight ,mesh.vertices[j].groups[3].weight)
                Grup = (Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[0].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[1].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[2].group].name], Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[3].group].name] )
        
        if len(mesh.vertices[j].groups) > 4 :
                #Weight = (mesh.vertices[j].groups[0].weight, mesh.vertices[j].groups[1].weight, mesh.vertices[j].groups[2].weight ,mesh.vertices[j].groups[3].weight)
                #Grup = (Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[0].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[1].group].name],Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[2].group].name], Slovar_bone[ob.vertex_groups[mesh.vertices[j].groups[3].group].name] )
                
                Weight = (0,0,0,0)
                Grup = (0,0,0,0)
                for ObjectGroup in mesh.vertices[j].groups:
                    if Weight[3] < ObjectGroup.weight :
                        if Weight[2] < ObjectGroup.weight :
                            if Weight[1] < ObjectGroup.weight :
                                if Weight[0] < ObjectGroup.weight :
                                    Weight= (ObjectGroup.weight,Weight[0],Weight[1],Weight[2])
                                    Grup = (Slovar_bone[ob.vertex_groups[ObjectGroup.group].name],Grup[0],Grup[1],Grup[2])
                                else:
                                    Weight= (Weight[0],ObjectGroup.weight,Weight[1],Weight[2])
                                    Grup = (Grup[0],Slovar_bone[ob.vertex_groups[ObjectGroup.group].name],Grup[1],Grup[2])
                            else:
                                Weight= (Weight[0],Weight[1],ObjectGroup.weight,Weight[2])
                                Grup = (Grup[0],Grup[1],Slovar_bone[ob.vertex_groups[ObjectGroup.group].name],Grup[2])
                        else:
                            Weight= (Weight[0],Weight[1],Weight[2],ObjectGroup.weight)
                            Grup = (Grup[0],Grup[1],Grup[2],Slovar_bone[ob.vertex_groups[ObjectGroup.group].name])
                
        #Виставлення по порядку
        if   (Weight[0]>=Weight[1]) and (Weight[0]>=Weight[2]) and (Weight[0]>=Weight[3]) :
            #0
            if   (Weight[1]>=Weight[2]) and (Weight[1]>=Weight[3]) :
                #1
                if (Weight[2]>=Weight[3]):
                    #2-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[1],Weights[2],Weights[3])
                    Grup   = (Grups[0],Grups[1],Grups[2],Grups[3])
                elif (Weight[3]>=Weight[2]):
                    #3-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[1],Weights[3],Weights[2])
                    Grup   = (Grups[0],Grups[1],Grups[3],Grups[2])
            elif (Weight[2]>=Weight[1]) and (Weight[2]>=Weight[3]) :
                #2
                if (Weight[1]>=Weight[3]):
                    #1-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[2],Weights[1],Weights[3])
                    Grup   = (Grups[0],Grups[2],Grups[1],Grups[3])
                elif (Weight[3]>=Weight[1]):
                    #3-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[2],Weights[3],Weights[1])
                    Grup   = (Grups[0],Grups[2],Grups[3],Grups[1])
            elif (Weight[3]>=Weight[1]) and (Weight[3]>=Weight[2]) :
                #3
                if (Weight[1]>=Weight[2]):
                    #1-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[3],Weights[1],Weights[2])
                    Grup   = (Grups[0],Grups[3],Grups[1],Grups[2])
                elif (Weight[2]>=Weight[1]):
                    #2-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[0],Weights[3],Weights[2],Weights[1])
                    Grup   = (Grups[0],Grups[3],Grups[2],Grups[1])
        elif (Weight[1]>=Weight[0]) and (Weight[1]>=Weight[2]) and (Weight[1]>=Weight[3]) :
            #1
            if   (Weight[0]>=Weight[2]) and (Weight[0]>=Weight[3]) :
                #0
                if (Weight[2]>=Weight[3]):
                    #2-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[0],Weights[2],Weights[3])
                    Grup   = (Grups[1],Grups[0],Grups[2],Grups[3])
                elif (Weight[3]>=Weight[2]):
                    #3-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[0],Weights[3],Weights[2])
                    Grup   = (Grups[1],Grups[0],Grups[3],Grups[2])
            elif (Weight[2]>=Weight[0]) and (Weight[2]>=Weight[3]) :
                #2
                if (Weight[0]>=Weight[3]):
                    #0-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[2],Weights[0],Weights[3])
                    Grup   = (Grups[1],Grups[2],Grups[0],Grups[3])
                elif (Weight[3]>=Weight[0]):
                    #3-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[2],Weights[3],Weights[0])
                    Grup   = (Grups[1],Grups[2],Grups[3],Grups[0])
            elif (Weight[3]>=Weight[0]) and (Weight[3]>=Weight[2]) :
                #3
                if (Weight[0]>=Weight[2]):
                    #0-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[3],Weights[0],Weights[2])
                    Grup   = (Grups[1],Grups[3],Grups[0],Grups[2])
                elif (Weight[2]>=Weight[0]):
                    #2-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[1],Weights[3],Weights[2],Weights[0])
                    Grup   = (Grups[1],Grups[3],Grups[2],Grups[0])
        elif (Weight[2]>=Weight[0]) and (Weight[2]>=Weight[1]) and (Weight[2]>=Weight[3]) :
            #2
            if   (Weight[0]>=Weight[1]) and (Weight[0]>=Weight[3]) :
                #0
                if (Weight[1]>=Weight[3]):
                    #1-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[0],Weights[1],Weights[3])
                    Grup   = (Grups[2],Grups[0],Grups[1],Grups[3])
                elif (Weight[3]>=Weight[1]):
                    #3-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[0],Weights[3],Weights[1])
                    Grup   = (Grups[2],Grups[0],Grups[3],Grups[1])
            elif (Weight[1]>=Weight[0]) and (Weight[1]>=Weight[3]) :
                #1
                if (Weight[0]>=Weight[3]):
                    #0-3
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[1],Weights[0],Weights[3])
                    Grup   = (Grups[2],Grups[1],Grups[0],Grups[3])
                elif (Weight[3]>=Weight[0]):
                    #3-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[1],Weights[3],Weights[0])
                    Grup   = (Grups[2],Grups[1],Grups[3],Grups[0])
            elif (Weight[3]>=Weight[0]) and (Weight[3]>=Weight[1]) :
                #3
                if (Weight[0]>=Weight[1]):
                    #0-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[3],Weights[0],Weights[1])
                    Grup   = (Grups[2],Grups[3],Grups[0],Grups[1])
                elif (Weight[1]>=Weight[0]):
                    #1-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[2],Weights[3],Weights[1],Weights[0])
                    Grup   = (Grups[2],Grups[3],Grups[1],Grups[0])
        elif (Weight[3]>=Weight[0]) and (Weight[3]>=Weight[1]) and (Weight[3]>=Weight[2]) :
            #3
            if   (Weight[0]>=Weight[1]) and (Weight[0]>=Weight[2]) :
                #0
                if (Weight[1]>=Weight[2]):
                    #1-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[0],Weights[1],Weights[2])
                    Grup   = (Grups[3],Grups[0],Grups[1],Grups[2])
                elif (Weight[2]>=Weight[1]):
                    #2-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[0],Weights[2],Weights[1])
                    Grup   = (Grups[3],Grups[0],Grups[2],Grups[1])
            elif (Weight[1]>=Weight[0]) and (Weight[1]>=Weight[2]) :
                #1
                if (Weight[0]>=Weight[2]):
                    #0-2
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[1],Weights[0],Weights[2])
                    Grup   = (Grups[3],Grups[1],Grups[0],Grups[2])
                elif (Weight[2]>=Weight[0]):
                    #2-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[1],Weights[2],Weights[0])
                    Grup   = (Grups[3],Grups[1],Grups[2],Grups[0])
            elif (Weight[2]>=Weight[0]) and (Weight[2]>=Weight[1]) :
                #2
                if (Weight[0]>=Weight[1]):
                    #0-1
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[2],Weights[0],Weights[1])
                    Grup   = (Grups[3],Grups[2],Grups[0],Grups[1])
                elif (Weight[1]>=Weight[0]):
                    #1-0
                    Weights = Weight
                    Grups   = Grup
                    Weight = (Weights[3],Weights[2],Weights[1],Weights[0])
                    Grup   = (Grups[3],Grups[2],Grups[1],Grups[0])
        
    #Cтара вигрузка костей
    if self.download_bones == "Old_bones" :
        if len(mesh.vertices[j].groups) == 7 :
            #0
            if Slovar[mesh.vertices[j].groups[0].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[0].weight)
            elif Slovar[mesh.vertices[j].groups[0].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[0].weight)
            elif Slovar[mesh.vertices[j].groups[0].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[0].weight)
            else:
                if Slovar[mesh.vertices[j].groups[0].group][0]   == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[0].group][1]
                elif Slovar[mesh.vertices[j].groups[0].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[0].group][1]
                elif Slovar[mesh.vertices[j].groups[0].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[0].group][1]
                elif Slovar[mesh.vertices[j].groups[0].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[0].group][1]
            #1
            if Slovar[mesh.vertices[j].groups[1].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[1].weight)
            elif Slovar[mesh.vertices[j].groups[1].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[1].weight)
            elif Slovar[mesh.vertices[j].groups[1].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[1].weight)
            else:
                if Slovar[mesh.vertices[j].groups[1].group][0]   == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[1].group][1]
                elif Slovar[mesh.vertices[j].groups[1].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[1].group][1]
                elif Slovar[mesh.vertices[j].groups[1].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[1].group][1]
                elif Slovar[mesh.vertices[j].groups[1].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[1].group][1]    
            #2
            if Slovar[mesh.vertices[j].groups[2].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[2].weight)
            elif Slovar[mesh.vertices[j].groups[2].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[2].weight)
            elif Slovar[mesh.vertices[j].groups[2].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[2].weight)
            else:
                if Slovar[mesh.vertices[j].groups[2].group][0]   == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[2].group][1]
                elif Slovar[mesh.vertices[j].groups[2].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[2].group][1]
                elif Slovar[mesh.vertices[j].groups[2].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[2].group][1]
                elif Slovar[mesh.vertices[j].groups[2].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[2].group][1]   
            #3
            if Slovar[mesh.vertices[j].groups[3].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[3].weight)
            elif Slovar[mesh.vertices[j].groups[3].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[3].weight)
            elif Slovar[mesh.vertices[j].groups[3].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[3].weight)
            else:
                if Slovar[mesh.vertices[j].groups[3].group][0]   == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[3].group][1]
                elif Slovar[mesh.vertices[j].groups[3].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[3].group][1]
                elif Slovar[mesh.vertices[j].groups[3].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[3].group][1]
                elif Slovar[mesh.vertices[j].groups[3].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[3].group][1]
            #4
            if Slovar[mesh.vertices[j].groups[4].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[4].weight)
            elif Slovar[mesh.vertices[j].groups[4].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[4].weight)
            elif Slovar[mesh.vertices[j].groups[4].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[4].weight)
            else:
                if Slovar[mesh.vertices[j].groups[4].group][0] == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[4].group][1]
                elif Slovar[mesh.vertices[j].groups[4].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[4].group][1]
                elif Slovar[mesh.vertices[j].groups[4].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[4].group][1]
                elif Slovar[mesh.vertices[j].groups[4].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[4].group][1]
            #5
            if Slovar[mesh.vertices[j].groups[5].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[5].weight)
            elif Slovar[mesh.vertices[j].groups[5].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[5].weight)
            elif Slovar[mesh.vertices[j].groups[5].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[5].weight)
            else:
                if Slovar[mesh.vertices[j].groups[5].group][0] == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[5].group][1]
                elif Slovar[mesh.vertices[j].groups[5].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[5].group][1]
                elif Slovar[mesh.vertices[j].groups[5].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[5].group][1]
                elif Slovar[mesh.vertices[j].groups[5].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[5].group][1]
            #6
            if Slovar[mesh.vertices[j].groups[6].group]   == "Articular_W1":
                Weight[0] = (mesh.vertices[j].groups[6].weight)
            elif Slovar[mesh.vertices[j].groups[6].group] == "Articular_W2":
                Weight[1] = (mesh.vertices[j].groups[6].weight)
            elif Slovar[mesh.vertices[j].groups[6].group] == "Articular_W3":
                Weight[2] = (mesh.vertices[j].groups[6].weight)
            else:
                if Slovar[mesh.vertices[j].groups[6].group][0]   == "A" :
                    Grup[0] = Slovar[mesh.vertices[j].groups[6].group][1]
                elif Slovar[mesh.vertices[j].groups[6].group][0] == "B" :
                    Grup[1] = Slovar[mesh.vertices[j].groups[6].group][1]
                elif Slovar[mesh.vertices[j].groups[6].group][0] == "C" :
                    Grup[2] = Slovar[mesh.vertices[j].groups[6].group][1]
                elif Slovar[mesh.vertices[j].groups[6].group][0] == "D" :
                    Grup[3] = Slovar[mesh.vertices[j].groups[6].group][1]
                    
    return (Weight,Grup)

def offloading( self, filepath):
    #log = open(filepath+".log" , 'w')
    
    self.report({'INFO'}, "#===========================================================================\n# Початок експорта Ski файла\n#===========================================================================")
    self.report({'INFO'}, '\n export *.ski file %r' % filepath )  
    time_main = time.time()
    
    file_object = ""
    data1 = ("MOXBIKSA".encode('gbk'))
    
    if self.use_Logs_rewrite:
        file_object = open(filepath , 'rb')
        file_object.read(8)
        SKY_TYPE = struct.unpack('<I', file_object.read(4))[0]
        OBJ_TYPE_count = struct.unpack('<4I', file_object.read(16)) # Обекти
        L3 = struct.unpack('<I', file_object.read(4))[0] # textures || texture_count
        L4 = struct.unpack('<I', file_object.read(4))[0] # material || material_count
        L5 = struct.unpack('<I', file_object.read(4))[0] # num_bips
        file_object.read(4)
        TYPE_MASK = struct.unpack('<I', file_object.read(4))[0] # type_mask || определяет количество костей в *.bon файла
        file_object.read(60)
        
    textures = 0 
    material = 0
    obj_type_count_0 = 0
    obj_type_count_1 = 0
    # для рахунку матеріалів і текстур буду використовувати
    # словарь текстур і словар матриць ключ це номер
    # а дані це дата борк матеріала або текстури
    matrix_textures  = {}
    matrix_materials = {}
    
    
    scene=bpy.context.scene
    if self.use_selection:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene) and ob.select)
    else:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene))
#===========================================================================
# кількість матеріалів і текстур 
#===========================================================================
    for SceneObject in ObjectList:
        if SceneObject.type in {'ARMATURE'}:
            if SceneObject.name == "Bone1" :
                type_mask_bit = str(SceneObject.pose.bones)
                type_mask_bit = int(type_mask_bit[16:-14])
        
        if SceneObject.type in {'MESH'}:
            ##Треба добавити свойство при експорті   
            if self.object_tiyp == 'Pets': 
                obj_type_count_0 = obj_type_count_0 +1
            if self.object_tiyp == 'Casuals': 
                obj_type_count_0 = obj_type_count_0 +1
            if self.object_tiyp == 'Weapons': 
                obj_type_count_1 = obj_type_count_1 +1
            
            if SceneObject.active_material:
                #якщо не копія матеріалу то
                if SceneObject.active_material.name[-4] != "." :
                    #добавляєм матеріал в словарь
                    matrix_materials[material] = SceneObject.active_material 
                    #збульшуєм кількість матеріалів на 1
                    material += 1
            
            if SceneObject.active_material.active_texture:
                #добавляєм текстуру в словарь
                matrix_textures[textures] = SceneObject.active_material.active_texture
                #збульшуєм кількість матеріалів на 1
                textures+=1
    
    
    
    if self.use_selection:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene) and ob.select)
    else:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene))
    data_bips,num_bips,Slovar,Slovar_bone = Bip(self,ObjectList)
    
    if self.use_Logs_rewrite == True:
        if self.use_Logs_Title == True :
            self.report({'OPERATOR'}, '_________________________________________________')
            self.report({'OPERATOR'}, '| Тип *.ski файла                 | %.2i -> %.2i        |' % (SKY_TYPE,self.ski_tiyp) )
            self.report({'OPERATOR'}, '| Кількість обектів файла         | %.2i -> %.2i        |' % (OBJ_TYPE_count[0],obj_type_count_0))
            self.report({'OPERATOR'}, '| Кількість текстур               | %.2i -> %.2i        |' % (L3,textures))
            self.report({'OPERATOR'}, '| Кількість матеріалів            | %.2i -> %.2i        |' % (L4,material))
            self.report({'OPERATOR'}, '| Кількість костей                | %.2i -> %.2i        |' % (L5,num_bips))
            self.report({'OPERATOR'}, '| Количество костей в *.bon файлі | %.2i -> %.2i        |' % (TYPE_MASK,self.type_mask))
            self.report({'OPERATOR'}, '*************************************************')
            print ("Type",SKY_TYPE,"-->>",self.ski_tiyp)
            print ("Object",OBJ_TYPE_count,"-->>",obj_type_count_0,obj_type_count_1,0,0)
            print ("Textures",L3,"-->>",textures)
            print ("Materials",L4,"-->>",material)
            print ("Weight",L5,"-->>",num_bips)
            print ("Bones",TYPE_MASK,"-->>",self.type_mask )
    else:
        if self.use_Logs_Title == True :
            self.report({'OPERATOR'}, '_________________________________________________')
            self.report({'OPERATOR'}, '| Тип *.ski файла                 | %.2i          |' % self.ski_tiyp)
            self.report({'OPERATOR'}, '| Кількість обектів файла         | %.2i          |' % obj_type_count_0)
            self.report({'OPERATOR'}, '| Кількість текстур               | %.2i          |' % textures)
            self.report({'OPERATOR'}, '| Кількість матеріалів            | %.2i          |' % material)
            self.report({'OPERATOR'}, '| Кількість костей                | %.2i          |' % num_bips)
            self.report({'OPERATOR'}, '| Количество костей в *.bon файлі | %.2i         |' % self.type_mask)
            self.report({'OPERATOR'}, '*************************************************')
            print ("Type",self.ski_tiyp)
            print ("Object",obj_type_count_0)
            print ("Textures",textures)
            print ("Materials",material)
            print ("Weight",num_bips)
            print ("type_mask количество костей",self.type_mask)
            
    # Запис 1 блока даних
    data1 = data1 + struct.pack('<I', self.ski_tiyp ) #9 pet
    data1 = data1 + struct.pack('<4I',obj_type_count_0,obj_type_count_1,0,0)
    data1 = data1 + struct.pack('<I', textures)
    data1 = data1 + struct.pack('<I', material)
    data1 = data1 + struct.pack('<I', num_bips) # num_bips
    data1 = data1 + struct.pack('<I', 0) # unknown_2 || (всегда значение 0 найдено до сих пор)
    data1 = data1 + struct.pack('<I', self.type_mask )
    # Запис блока пустих байтив
    data1 = data1 + struct.pack('<15I', 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 )
    

    # Загрузка костей якшо ski_tiyp = 9
    # Функція перерахунку груп костей в меші
    if self.ski_tiyp == 9 :
        #===============================================================================
        # функция тики для лога
        #===============================================================================
        if self.use_Logs_rewrite == True :
            Download_Bip(self,data_bips,num_bips,file_object)
        data1 = data1 + data_bips
        
#===============================================================================
# Загрузка пути текстури 
#===============================================================================
    data1 = Download_Textures(self,data1,file_object,matrix_textures,filepath)    
#===============================================================================
#Вигрузка матеріалу
#вигрузка матеріалів здійстюєца по словарю матеріалів
#вигружаєця кожен елемент попорядку
#===============================================================================
    data1 = Download_Material(self,data1,matrix_materials,material,file_object)
#===============================================================================
# Загрузка сетки обекта
#===============================================================================
    if self.use_selection:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene) and ob.select)
    else:
        ObjectList = (ob for ob in scene.objects if ob.is_visible(scene))
    
    if obj_type_count_0 > 0 : data1 = Download_Mesh_0(self,obj_type_count_0,file_object,data1,Slovar,Slovar_bone,matrix_materials,matrix_textures,ObjectList)
    #if obj_type_count_1 > 0 : data1 = Download_Mesh_1(self,obj_type_count_1,file_object,data1)
    
    if self.use_Logs_Poligon == True:
        file_object.close()
        
        
    
    time_new = time.time()
    self.report({'INFO'}, "#===========================================================================\n# Кінець експорта Ski файла\n#===========================================================================")
    self.report({'INFO'}, "Експорт закинчено закінчено: за %.4f секнд." % ( (time_new - time_main)) )  
     
    if ERROR == False:
        file_object = open(filepath, 'wb')
        file_object.write(data1)
        file_object.close()
         
        
         
        if self.object_tiyp == "Casuals" :
            if self.object_сasuals_tiyp == "Man" :
                head, tail = os.path.split(filepath)
                file_object = open( head+"/妖兽"+tail[:-4]+"一级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                     
                file_object = open(head+"/妖兽"+tail[:-4]+"三级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/妖兽"+tail[:-4]+"二级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/男通用"+tail[:-4]+"一级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/男通用"+tail[:-4]+"三级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/男通用"+tail[:-4]+"二级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
            if self.object_сasuals_tiyp == "Woomen" :
                head, tail = os.path.split(filepath)
                file_object = open( head+"/女通用"+tail[:-4]+"一级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                     
                file_object = open(head+"/女通用"+tail[:-4]+"三级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/女通用"+tail[:-4]+"二级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/妖精"+tail[:-4]+"一级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/妖精"+tail[:-4]+"三级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
                
                file_object = open(head+"/妖精"+tail[:-4]+"二级"+".ski", 'wb')
                file_object.write(data1)
                file_object.close()
    
    return {'FINISHED'}
            
def Download_Bip(self,data_bips,num_bips,file_object):
#===============================================================================
# функция тики для лога
#===============================================================================
    n=0
    for i in range(num_bips):
        NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
        NAME_BON = file_object.read(NAME_TYP).decode('gbk')
        name_typ = struct.unpack('<I',data_bips[n:n+4])[0]
        n+=4
        name_bon = data_bips[n:n+name_typ].decode('gbk')
        n+=name_typ
        if self.use_Logs_Grups:
            print (i,")",NAME_TYP,NAME_BON,"-->",name_typ,name_bon ) 
    return ()

def Bip(self,ObjectList):
    i = 0
    mesh_nom = -1
    num_bips = 0
    
    Slovar = {}
    Slovar_bone = {} # словар имен костей
    
    #Загрузка костей стандартно
    if self.download_bones == "Complete_bones" :
        for SceneObject in ObjectList:
            if SceneObject.type in {'MESH'}:
                mesh_nom = mesh_nom + 1
                bit = 0
                Slolvar_bit = {}
                for groups in SceneObject.vertex_groups :
                    if groups.name[-2:] == "_1":
                        groupsname = groups.name[:-2]
                        Slolvar_bit[str(bit)]= 1
                    elif groups.name[-2:] == "_2":
                        groupsname = groups.name[:-2]
                        Slolvar_bit[str(bit)]= 2 
                    elif groups.name[-2:] == "_3":
                        groupsname = groups.name[:-2]                     
                        Slolvar_bit[str(bit)]= 3
                    else :
                        groupsname = groups.name
                        Slolvar_bit[str(bit)]= 0
                    
                    Slolvar_bit[bit]=groupsname
                    if i == 0 :
                        data = struct.pack('<I', len(groupsname.encode('gbk')))
                        data = data + groupsname.encode('gbk')
                        Slovar [bit] = num_bips
                        Slovar_bone[groupsname] = num_bips # словар имен костей
                        num_bips = num_bips + 1 
                    else :
                        bat = 0
                        for I in range(num_bips) :#num_bips
                            NAME_TYP = struct.unpack_from('<I', data , bat )[0]
                            bat = bat + 4
                            if groupsname == data [bat:bat+NAME_TYP].decode('gbk') :
                                Slovar [bit] = I
                                break
                            bat = bat+NAME_TYP  
                        else:
                            data = data + struct.pack('<I', (len(groupsname.encode('gbk'))))
                            data = data + groupsname.encode('gbk')
                            Slovar [bit] = num_bips
                            Slovar_bone[groupsname] = num_bips # словар имен костей
                            num_bips = num_bips + 1  
                    bit = bit +1
                    i=i+1
                Slovar[mesh_nom]=Slolvar_bit
    
    
    if self.download_bones == "Experement_bones" :
        for SceneObject in ObjectList:
            if SceneObject.type in {'MESH'}:
                mesh_nom = mesh_nom + 1 # рахунок обєктів
                bit = 0 # рахунок груп 
                for groups in SceneObject.vertex_groups :
                    groupsname = groups.name
                    try:
                        Slovar_bone[groups.name]
                    except KeyError:
                        if num_bips == 0 :
                            data = struct.pack('<I', len(groups.name.encode('gbk')))
                            data = data + groups.name.encode('gbk')
                        else :
                            data = data + struct.pack('<I', (len(groups.name.encode('gbk'))))
                            data = data + groups.name.encode('gbk')
                        if self.use_Logs_Grups:
                            print(num_bips,groups.name)
                            self.report({'OPERATOR'}, '%2.i)  %s' % (num_bips,groups.name) )
                        Slovar_bone[groups.name] = num_bips # словар имен костей |номер = Slovar_bone[імя кості] 
                        num_bips += 1
                        
        
    #Загрузка костей старий варіант
    if self.download_bones == "Old_bones" :
        datas = {}
        data1 = {}
        data2 = {}
        data3 = {}
        data4 = {}
        
        bone_1 = {}
        bone_2 = {}
        bone_3 = {}
        bone_4 = {}
        
        num_bips1=0 
        num_bips2=0
        num_bips3=0
        num_bips4=0
        
        for SceneObject in ObjectList:
            if SceneObject.type in {'MESH'}:
                mesh_nom = mesh_nom + 1
                bit = 0
                for groups in SceneObject.vertex_groups :
                    if groups.name[:5] == "_grp_" :
                        Slovar[bit] = (groups.name[9],int(groups.name[5:8]))
                        if groups.name[9] == "A" :
                            datas [int(groups.name[5:8])] = groups.name[12:-1]
                            data1[num_bips1] = groups.name[12:-1]
                            bone_1[bit] =  num_bips1
                            num_bips1 = num_bips1 + 1
                        if groups.name[9] == "B" :
                            datas [int(groups.name[5:8])] = groups.name[12:-1]
                            data2[num_bips2] = groups.name[12:-1]
                            bone_2[bit] =  num_bips2
                            num_bips2 = num_bips2 + 1
                        if groups.name[9] == "C" :
                            datas [int(groups.name[5:8])] = groups.name[12:-1]
                            data3[num_bips3] = groups.name[12:-1]
                            bone_3[bit] =  num_bips3
                            num_bips3 = num_bips3 + 1
                        if groups.name[9] == "D" :
                            datas [int(groups.name[5:8])] = groups.name[12:-1]
                            data4[num_bips4] = groups.name[12:-1]
                            bone_4[bit] =  num_bips4
                            num_bips4 = num_bips4 + 1
                    
                    elif groups.name == "Articular_W1" :
                        Slovar[bit] = "Articular_W1"
                    elif groups.name == "Articular_W2" :
                        Slovar[bit] = "Articular_W2"
                    elif groups.name == "Articular_W3" :
                        Slovar[bit] = "Articular_W3"
                    bit = bit + 1
            data = b""       
            for groupsname in datas :
                name = datas[groupsname].encode('gbk')
                data = data + struct.pack('<I', len(name) )
                data = data + name
            num_bips = len(datas)
    if num_bips == 0 :
            data = b""
            
    return (data,num_bips,Slovar,Slovar_bone)

def Download_Textures(self,data1,file_object,matrix_textures,filepath):
#===============================================================================
# Загрузка текстур
#===============================================================================
    if self.use_Logs_Textures == True:
        print ("=================================")
        print ("=============TEXTURES============")
        print ("=================================")
    for index in matrix_textures:
        Tex = matrix_textures[index].image.filepath
        Textures = os.path.basename(Tex)
        if Textures =='' :
            Textures=Tex[Tex.find('\\')+1:]
        if self.use_Logs_rewrite == True:
            tex = struct.unpack('<I', file_object.read(4))[0]
            textures = (file_object.read(tex).decode('gbk'))
            if self.use_Logs_Textures :
                print (tex,"-->",len(Textures.encode('gbk')))
                print (textures,"-->",Textures)
        else:
            if self.use_Logs_Textures :
                print (len(Textures.encode('gbk')))
                print (Textures)
                self.report({'OPERATOR'}, (Textures) )
        data1 = data1 + struct.pack('<I', len(Textures.encode('gbk')))
        data1 = data1 + Textures.encode('gbk')
    return (data1)

def Download_Material(self,data1,matrix_materials,material,file_object):
#===============================================================================
#Загрузка матеріалу
#!!! НЕЗРОБЛЕНО !!!
#===============================================================================
    if self.use_Logs_Material:
        print ("=================================")
        print ("=============Material============")
        print ("=================================")
    
    for i in range(material) :
                mat= matrix_materials[i]
                data1 = data1 + 'MATERIAL: '.encode('gbk') + struct.pack('<B',0)
                data1 = data1 + struct.pack('<f', mat.diffuse_color[0]) + struct.pack('<f', mat.diffuse_color[1]) + struct.pack('<f', mat.diffuse_color[2]) + struct.pack('<f', mat.diffuse_intensity)
                data1 = data1 + struct.pack('<f', mat.specular_color[0]) + struct.pack('<f', mat.specular_color[1]) + struct.pack('<f', mat.specular_color[2]) + struct.pack('<f', mat.specular_intensity)
                
                #LOG
                if self.use_Logs_rewrite :
                    file_object.read(11)
                    diffuse_color  = struct.unpack('<3f', file_object.read(12))
                    diffuse_intensity = struct.unpack('<f', file_object.read(4))[0]
                    specular_color = struct.unpack('<3f', file_object.read(12))
                    specular_intensity = struct.unpack('<f', file_object.read(4))[0]
                    specular_color2 = struct.unpack('<3f', file_object.read(12))
                    specular_intensity2 = struct.unpack('<f', file_object.read(4))[0]
                    emissive_color = struct.unpack('<3f', file_object.read(12))
                    emissive_intensity = struct.unpack('<f', file_object.read(4))[0]
                    alpha  = struct.unpack('<f', file_object.read(4))[0]
                    bIsClothing = struct.unpack('<B', file_object.read(1))[0]
                    if self.use_Logs_Material :
                        print (diffuse_color,"-->",mat.diffuse_color)
                        print (diffuse_intensity,"-->",mat.diffuse_intensity)
                        print (specular_color,"-->",mat.specular_color)
                        print (specular_intensity,"-->",mat.specular_intensity)
                        print (specular_color2,"-->",mat.mirror_color)
                        print (specular_intensity2,"-->",mat.raytrace_mirror.gloss_facto)
                        print (emissive_color,"-->",mat.subsurface_scattering.color)
                        print (emissive_intensity,"-->",mat.subsurface_scattering.color_factor)
                        print (alpha,"-->",mat.alpha)
                        print (bIsClothing,"-->",1)
                else:
                    if self.use_Logs_Material :
                        print ("diffuse_color,-->",mat.diffuse_color)
                        print ("diffuse_intensity,-->",mat.diffuse_intensity)
                        print ("specular_color,-->",mat.specular_color)
                        print ("specular_intensity,-->",mat.specular_intensity)
                        print ("specular_color2,-->",mat.mirror_color)
                        print ("specular_intensity2,-->",mat.raytrace_mirror.gloss_factor)
                        print ("emissive_color,-->",mat.subsurface_scattering.color)
                        print ("emissive_intensity,-->",mat.subsurface_scattering.color_factor)
                        print ("alpha,-->",mat.alpha)
                        print ("bIsClothing,-->",1)
                        self.report({'OPERATOR'}, '____________________Material______________________')
                        self.report({'OPERATOR'}, '| diffuse_color             | %.2f  %.2f  %.2f   |' % (mat.diffuse_color[0],mat.diffuse_color[1],mat.diffuse_color[2]) )
                        self.report({'OPERATOR'}, '| diffuse_intensity         | %.2f               |' % mat.diffuse_intensity)
                        self.report({'OPERATOR'}, '| specular_color            | %.2f  %.2f  %.2f   |' % (mat.specular_color[0],mat.specular_color[1],mat.specular_color[2]) )
                        self.report({'OPERATOR'}, '| specular_intensity        | %.2f               |' % mat.specular_intensity)
                        self.report({'OPERATOR'}, '| specular_color2           | %.2f  %.2f  %.2f   |' % (mat.mirror_color[0],mat.mirror_color[1],mat.mirror_color[2]) )
                        self.report({'OPERATOR'}, '| specular_intensity2       | %.2f               |' % mat.raytrace_mirror.gloss_factor)
                        self.report({'OPERATOR'}, '| emissive_color            | %.2f  %.2f  %.2f   |' % (mat.subsurface_scattering.color[0],mat.subsurface_scattering.color[1],mat.subsurface_scattering.color[2]) )
                        self.report({'OPERATOR'}, '| emissive_intensity        | %.2f               |' % mat.subsurface_scattering.color_factor)
                        self.report({'OPERATOR'}, '| mat.alpha                 | %.2f               |' % mat.alpha)
                        self.report({'OPERATOR'}, '*************************************************')    
                      
                if mat.raytrace_mirror.use :
                    data1 = data1 + struct.pack('<f', mat.mirror_color[0]) + struct.pack('<f', mat.mirror_color[1]) + struct.pack('<f', mat.mirror_color[2]) + struct.pack('<f', mat.raytrace_mirror.gloss_factor)
                else:
                    data1 = data1 + struct.pack('<f', 0) + struct.pack('<f', 0) + struct.pack('<f', 0) + struct.pack('<f', 1)
                
                if mat.subsurface_scattering.use :
                    data1 = data1 + struct.pack('<f', mat.subsurface_scattering.color[0]) + struct.pack('<f', mat.subsurface_scattering.color[1]) + struct.pack('<f', mat.subsurface_scattering.color[2]) + struct.pack('<f', mat.subsurface_scattering.color_factor)
                else:
                    data1 = data1 + struct.pack('<f', 0) + struct.pack('<f', 0) + struct.pack('<f', 0) + struct.pack('<f', 1)

                data1 = data1 + struct.pack('<f', mat.alpha)
                #show_double_sided
                data1 = data1 + struct.pack('<B', 1 ) ## 1 нормали в 2 сторони # 0 нормали в одну сторону
    return (data1)

def Download_Mesh_0(self,obj_type_count_0,file_object,data1,Slovar,Slovar_bone,matrix_materials,matrix_textures,ObjectList):
    global ERROR
    B = 0
    for ob in ObjectList:
        if ob.type in {'MESH'}:
            if self.use_Logs_rewrite :
                NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
                name = file_object.read(NAME_TYP).decode('gbk')
                ob = bpy.data.objects[name]
            #--- +
            mesh = ob.data
            #mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
            name1 = ob.name
            
            scene = bpy.context.scene
            j, derived = create_derived_objects(scene, ob)
            for ob_derived, j in derived:
                meshq  = ob_derived.to_mesh(scene, True, 'PREVIEW') 
            tri_list = Edit_Mesh.extract_triangles(self,meshq)
            
            vert_array, uv_array,normal_array, tri_list,weight_array,grup_array = Edit_Mesh.remove_face_uv(self,tri_list,mesh,Slovar,Slovar_bone,ob,B)
            
            
            #визначення індекса матеріала
            for mat_index in matrix_materials:
                if ob.active_material.name[-4] != ".":
                    if matrix_materials[mat_index].name == ob.active_material.name:
                        Material_index=mat_index
                else:
                    if matrix_materials[mat_index].name == ob.active_material.name[:-4]:
                        Material_index=mat_index
            
            #визначення індекса текстури
            for tex_index in matrix_textures:
                try:
                    if matrix_textures[tex_index].name == ob.active_material.active_texture.name:
                        Textures_index=tex_index
                except AttributeError:
                    self.report({'ERROR'},'Ошыбка в текстурах')
                    ERROR=True;
                
            if self.use_Logs_rewrite :
                texture_index = struct.unpack('<I', file_object.read(4))[0]
                material_index = struct.unpack('<I', file_object.read(4))[0]
                vertex_count = struct.unpack('<I', file_object.read(4))[0]
                index_count = struct.unpack('<I', file_object.read(4))[0]
                if self.use_Logs_Poligon:
                    print(name,"-->",name1,"(",NAME_TYP,"->",len(name1.encode('gbk')),")" )
                    print('texture_index',texture_index,"-->",Textures_index)
                    print('material_index',material_index,"-->",Material_index)
                    print ("Вершин:",vertex_count,"-->",len (mesh.vertices))
                    print ("index_count:",index_count,"-->",len(mesh.loops))
            
            
            data1 = data1 + struct.pack('<I',len(name1.encode('gbk')))         # NAME_TYP
            data1 = data1 + name1.encode('gbk')                                # NAME
            data1 = data1 + struct.pack('<I',Textures_index)  # mesh.polygons[0].material_index+ texture_index
            
            try:
                data1 = data1 + struct.pack('<I',Material_index)  # mesh.polygons[0].material_index+ material_index
            except UnboundLocalError:
                self.report({'ERROR'},'Ошыбка в материалах')
                self.report({'WARNING'},'Потрибно перевирыты правельнисть написання имен материалив')
                ERROR=True;
            
            data1 = data1 + struct.pack('<I',len (mesh.vertices))
            data1 = data1 + struct.pack('<I',len (mesh.loops))            
            # МАТРИЦЯ ТЕКСТУРНИХ ВЕРШИН
            matrix_uv = {}
            for i,polygon in enumerate(mesh.polygons):
                matrix_uv[polygon.vertices[0]] = mesh.uv_layers[0].data[i*3].uv
                matrix_uv[polygon.vertices[1]] = mesh.uv_layers[0].data[i*3+1].uv
                matrix_uv[polygon.vertices[2]] = mesh.uv_layers[0].data[i*3+2].uv
                                                                                       
            for j in range(len(mesh.vertices)) :  
#===============================================================================
#1. VERTICES (position) Список координат вершин
#===============================================================================
                if self.use_root == False :
                    if self.use_Logs_rewrite :
                        x = struct.unpack('<f', file_object.read(4))[0]
                        y = struct.unpack('<f', file_object.read(4))[0]
                        z = struct.unpack('<f', file_object.read(4))[0]
                        print ("(V)",x,y,z,"-->",mesh.vertices[j].co[1],mesh.vertices[j].co[2],-mesh.vertices[j].co[0])
                    data1 = data1 + struct.pack('<f',mesh.vertices[j].co[1]) + struct.pack('<f',mesh.vertices[j].co[2])  + struct.pack('<f',-mesh.vertices[j].co[0])
                else:
                    if self.use_Logs_rewrite :
                        x = struct.unpack('<f', file_object.read(4))[0]
                        y = struct.unpack('<f', file_object.read(4))[0]
                        z = struct.unpack('<f', file_object.read(4))[0]
                        print ("(V)",x,y,z,"-->",mesh.vertices[j].co[0],mesh.vertices[j].co[2],-mesh.vertices[j].co[1])
                    data1 = data1 + struct.pack('<f',mesh.vertices[j].co[0]) + struct.pack('<f',mesh.vertices[j].co[2])  + struct.pack('<f',-mesh.vertices[j].co[1])       
#===============================================================================
# 2. Grups           
#===============================================================================
                Weight,Grup = Grups(self,mesh,Slovar,Slovar_bone,ob,j,B)
                if self.use_Logs_rewrite :
                        vertex_color = struct.unpack('<3f', file_object.read(12))
                        vgroups = struct.unpack('<4B', file_object.read(4)) 
                        print ("(VG)",vertex_color,"-->",Weight[0],Weight[1],Weight[2])
                        print ("(G)",vgroups,"-->",Grup)
                        
                data1 = data1 + struct.pack('<f',Weight[0]) + struct.pack('<f',Weight[1]) + struct.pack('<f',Weight[2])
                data1 = data1 + struct.pack('<B',Grup[0]) + struct.pack('<B',Grup[1]) + struct.pack('<B',Grup[2]) + struct.pack('<B',Grup[3])
#===============================================================================
# 3. Нормалі    
#===============================================================================
                if self.use_root == False :
                    if self.use_Logs_rewrite :
                        nX,nZ,nY = struct.unpack('<3f', file_object.read(12))
                        print ("(H)",nX,nZ,nY, "-->",mesh.vertices[j].normal[1],mesh.vertices[j].normal[2],-mesh.vertices[j].normal[0])
                    data1 = data1 + struct.pack('<f',mesh.vertices[j].normal[1]) + struct.pack('<f',mesh.vertices[j].normal[2]) + struct.pack('<f',-mesh.vertices[j].normal[0])
                else:
                    if self.use_Logs_rewrite :
                        nX,nZ,nY = struct.unpack('<3f', file_object.read(12))
                        print ("(H)",nX,nZ,nY, "-->",mesh.vertices[j].normal[0],mesh.vertices[j].normal[2],-mesh.vertices[j].normal[1])
                    data1 = data1 + struct.pack('<f',mesh.vertices[j].normal[0]) + struct.pack('<f',mesh.vertices[j].normal[2]) + struct.pack('<f',-mesh.vertices[j].normal[1])
#===============================================================================
#4. UV TEXTURES
#===============================================================================
                if self.use_Logs_rewrite :
                    uv_coordinates = struct.unpack('<2f',file_object.read(8))
                    try:
                        print ("(UV)",uv_coordinates,"-->",matrix_uv[j][0],1 - matrix_uv[j][1])
                    except KeyError:
                        print ("(UV)",uv_coordinates,"-->","Битий вертекс")
                #Защита від битої ув розвортки і вертекса без полігона
                try:
                    data1 = data1 + struct.pack('<f',matrix_uv[j][0]) + struct.pack('<f', 1 - matrix_uv[j][1])
                except KeyError:
                    data1 = data1 + struct.pack('<f',0) + struct.pack('<f',0)
            
            for pol in  mesh.polygons :
                if self.use_Logs_rewrite :
                    polig = struct.unpack('<3H', file_object.read(6))
                    print ("(P)",polig,"-->",pol.vertices[0],pol.vertices[1],pol.vertices[2])
                data1 = data1 + struct.pack('<H',pol.vertices[0]) + struct.pack('<H',pol.vertices[1]) + struct.pack('<H',pol.vertices[2])
            B = B + 1
    return (data1)
    
def Download_Mesh_1(download_bones,obj_type_count_1,file_object,data1):
    B = 0
    for ob in bpy.context.scene.objects:
        if ob.type in {'MESH'}:
            #--- +
            mesh = ob.data
            #mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
            name1 = ob.name
            
            data1 = data1 + struct.pack('<I',len(name1.encode('gbk')))         # NAME_TYP
            data1 = data1 + name1.encode('gbk')                                # NAME
            data1 = data1 + struct.pack('<I',B)  # mesh.polygons[0].material_index+ texture_index
            data1 = data1 + struct.pack('<I',B)  # mesh.polygons[0].material_index+ material_index
            data1 = data1 + struct.pack('<I',B)  # mesh.polygons[0].material_index+ material_index
            
            data1 = data1 + struct.pack('<I',len (mesh.vertices))
            data1 = data1 + struct.pack('<I',len (mesh.loops))            
            matrix_uv = {}
            for i,polygon in enumerate(mesh.polygons):
                matrix_uv[polygon.vertices[0]] = mesh.uv_layers["UVMap"].data[i*3].uv
                matrix_uv[polygon.vertices[1]] = mesh.uv_layers["UVMap"].data[i*3+1].uv
                matrix_uv[polygon.vertices[2]] = mesh.uv_layers["UVMap"].data[i*3+2].uv
#            for i, polygon in enumerate(mesh.polygons):
#                nCountOfVertexesInPolygon = len(polygon.vertices) # 4 3 який много угольник
#                if nCountOfVertexesInPolygon == 4 : 
#                    print ("Aльша перероби в триугольники")
#                for j in range(nCountOfVertexesInPolygon):
#                    vertex = mesh.vertices[polygon.vertices[j]]
#                    if GotTexCoords:
#                        TexCoords = mesh.uv_layers.active.data[polygon.loop_indices[j]].uv
#                        matrix_uv[vertex.index] = (TexCoords[0],1-TexCoords[1])
#                    else :
#                        matrix_uv[vertex.index] = (0,0)

            for j in range(len(mesh.vertices)) :  
#===============================================================================
#1. VERTICES (position) Список координат вершин
#===============================================================================
                data1 = data1 + struct.pack('<f',mesh.vertices[j].co[1]) + struct.pack('<f',mesh.vertices[j].co[2])  + struct.pack('<f',-mesh.vertices[j].co[0])         
#===============================================================================
# 3. Нормалі    
#===============================================================================
                data1 = data1 + struct.pack('<f',-mesh.vertices[j].normal[1]) + struct.pack('<f',mesh.vertices[j].normal[0]) + struct.pack('<f',-mesh.vertices[j].normal[2]) 
#===============================================================================
#4. UV TEXTURES
#===============================================================================
                data1 = data1 + struct.pack('<f',matrix_uv[j][0]) + struct.pack('<f', 1 - matrix_uv[j][1])
            for pol in  mesh.polygons :
                data1 = data1 + struct.pack('<H',pol.vertices[0]) + struct.pack('<H',pol.vertices[1]) + struct.pack('<H',pol.vertices[2])                       
            B = B + 1
    return (data1)


class Edit_Mesh():
    #округлення кординат розвертки
    def uv_key(self,uv):
        return round(uv[0], 6), round(uv[1], 6)
    #перетворення ув розвертки до потрібної в пв
    def remove_face_uv(self,tri_list,mesh,Slovar,Slovar_bone,ob,B):
        """Удалить лицо УФ координат из списка треугольников.
    
        С 3ds файлы поддерживают только одну пару УФ координаты для каждой вершины лицо УФ координат
        должны быть преобразованы к вершине УФ координат. Это означает, что вершины должны быть дублированы, когда
        Есть несколько координаты УФ на вершине."""
        # инициализировать список UniqueLists, по одному на вершине:
        unique_uvs = [{} for i in range(len(ob.data.vertices))]
        
        
        # для каждой грани УФ координат, добавьте его в UniqueList вершины
        for tri in tri_list:
            for i in range(3):
                # store the index into the UniqueList for future reference:
                context_uv_vert = unique_uvs[tri.vertex_index[i]]
                uvkey = tri.faceuvs[i]
                offset_index__uv_3ds = context_uv_vert.get(uvkey)
                if not offset_index__uv_3ds:
                    offset_index__uv_3ds = context_uv_vert[uvkey] = len(context_uv_vert), Dani.point_uv(uvkey)
                tri.offset[i] = offset_index__uv_3ds[0]
                
                
        
        # В цей момент масив має: до кожної uv розвертки прикриплена 1 вершина
    
        # Now we need to duplicate every vertex as many times as it has uv coordinates and make sure the
        # faces refer to the new face indices:
        vert_index = 0
        vert_array = Dani.array()
        uv_array = Dani.array()
        normal_array = Dani.array()
        weight_array = Dani.array()
        grup_array = Dani.array()
               
        
        index_list = []
        for i, vert in enumerate(ob.data.vertices):
            index_list.append(vert_index)
            pt = Dani.point_3d(vert.co)  # reuse, should be ok
            nt = Dani.point_3d(vert.normal)  # reuse, should be ok
            Weight,Grup = Grups(self,mesh,Slovar,Slovar_bone,ob,i,B) 
            
            uvmap = [None] * len(unique_uvs[i])
            for ii, uv_3ds in unique_uvs[i].values():
                # add a vertex duplicate to the vertex_array for every uv associated with this vertex:
                vert_array.add(pt)
                normal_array.add(nt)
                weight_array.add(Weight)
                grup_array.add(Grup)
                # add the uv coordinate to the uv array:
                # This for loop does not give uv's ordered by ii, so we create a new map
                # and add the uv's later
                # uv_array.add(uv_3ds)
                uvmap[ii] = uv_3ds
    
            # Add the uv's in the correct order
            for uv_3ds in uvmap:
                # add the uv coordinate to the uv array:
                uv_array.add(uv_3ds)
            vert_index += len(unique_uvs[i])
    
        # Make sure the triangle vertex indices now refer to the new vertex list:
        for tri in tri_list:
            for i in range(3):
                tri.offset[i] += index_list[tri.vertex_index[i]]
            tri.vertex_index = tri.offset
        return vert_array, uv_array,normal_array, tri_list,weight_array,grup_array
    
    #розбиття на тугольні полігони 
    def extract_triangles(self, mesh):
        """Выписка треугольники из сетки.
        Если сетка содержит каре, они будут разделены на треугольники."""
        tri_list = []
        do_uv = bool(mesh.tessface_uv_textures)
         
        for i, face in enumerate(mesh.tessfaces):
            f_v = face.vertices
            uf = mesh.tessface_uv_textures.active.data[i] if do_uv else None
            
            if do_uv:
                f_uv = uf.uv
            
            if len(f_v) == 3:
                new_tri = Dani.tri_wrapper((f_v[0], f_v[1], f_v[2]) )
                if (do_uv):
                    new_tri.faceuvs = Edit_Mesh.uv_key(self,f_uv[0]), Edit_Mesh.uv_key(self,f_uv[1]), Edit_Mesh.uv_key(self,f_uv[2])
                    
                tri_list.append(new_tri)
            
            else:  # it's a quad
                new_tri = Dani.tri_wrapper((f_v[0], f_v[1], f_v[2]) )
                new_tri_2 = Dani.tri_wrapper((f_v[0], f_v[2], f_v[3]) )
                
                if (do_uv):
                    new_tri.faceuvs = Edit_Mesh.uv_key(self,f_uv[0]), Edit_Mesh.uv_key(self,f_uv[1]), Edit_Mesh.uv_key(self,f_uv[2])
                    new_tri_2.faceuvs = Edit_Mesh.uv_key(self,f_uv[0]), Edit_Mesh.uv_key(self,f_uv[2]), Edit_Mesh.uv_key(self,f_uv[3])
                    
                tri_list.append(new_tri)
                tri_list.append(new_tri_2)
        return tri_list


class Dani():
    #клас для памяті трикутних полигонів и uv кординат
    class tri_wrapper(object):
        """Класс, представляющий треугольник.
        Используется при преобразовании граней треугольников"""
        __slots__ = "vertex_index", "faceuvs", "offset"
        def __init__(self, vindex=(0, 0, 0),  faceuvs=None , ): #image=None, mat=None,
            self.vertex_index = vindex
            self.faceuvs = faceuvs
            self.offset = [0, 0, 0]  # offset indices

    #клас для памяті uv кординати
    class point_uv(object):
        """Class representing a UV-coordinate for a 3ds file."""
        __slots__ = ("uv", )
        def __init__(self, point):
            self.uv = point
    
#         def get_size(self):
#             return 2 * SZ_FLOAT
#         def __str__(self):
#             return '(%g, %g)' % self.uv
#         def write(self, file):
#             data = struct.pack('<2f', self.uv[0], self.uv[1])
#             file.write(data)
    
    #клас для памяті кординат
    class point_3d(object):
        """Class representing a three-dimensional point for a 3ds file."""
        __slots__ = "x", "y", "z"
    
        def __init__(self, point):
            self.x, self.y, self.z = point
    
#         def get_size(self):
#             return 3 * SZ_FLOAT
    
#         def write(self, file):
#             file.write(struct.pack('<3f', self.x, self.y, self.z))
#     
        def __str__(self):
            return '(%f, %f, %f)' % (self.x, self.y, self.z)
    # клас фертех колорив
    class rgb_color(object):
        """Class representing a (24-bit) rgb color for a 3ds file."""
        __slots__ = "r", "g", "b"
    
        def __init__(self, col):
            self.r, self.g, self.b = col
    
#         def get_size(self):
#             return 3
    
#         def write(self, file):
#             file.write(struct.pack('<3B', int(255 * self.r), int(255 * self.g), int(255 * self.b)))
    
        def __str__(self):
            return '{%f, %f, %f}' % (self.r, self.g, self.b)
    #клас сворення масиву
    class array(object):
        """Класс, представляющий массив переменных для 3ds файл.
        Consists of a _3ds_ushort to indicate the number of items, followed by the items themselves.
        """
        __slots__ = "values", "size"
    
        def __init__(self):
            self.values = []
#             self.size = SZ_SHORT
    
        # add an item:
        def add(self, item):
            self.values.append(item)
            #self.size += item.get_size()
    
        def get_size(self):
            return self.size
    
        def validate(self):
            return len(self.values) <= 65535
        
        # To not overwhelm the output in a dump, a _3ds_array only
        # outputs the number of items, not all of the actual items.
        def __str__(self):
            return '(%d items)' % len(self.values)
        
        
class ExportSki(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_ski.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Ski File"
    bl_options = {'PRESET', 'UNDO'}
    # ExportHelper mixin class uses this
    filename_ext = ".ski"

    filter_glob = StringProperty(
            default="*.ski",
            options={'HIDDEN'},
            )
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    type_mask = IntProperty(name="Количество костей в *.bon файла",default=1,)
    ski_tiyp = IntProperty(name="Ski тип",description="9 Type pets",default=9,)
    use_root = BoolProperty(name="RotZ-90%",description="Поворот на 90%",default= True,)
    use_selection = BoolProperty(name="Selection Only",description="Export selected objects only",default=False,)
    
    #use_Object  = BoolProperty(name="Лог об'єкта",description="Включити логи об'єкта",default=False,)
    use_Logs  = BoolProperty(name="Логи",description="Включтити логи",default=False,)
    #меню логів
    use_Logs_rewrite  = BoolProperty(name="Лог перезапису",description="Включити логи зрівнення файлів",default=False,)
    use_Logs_Title  = BoolProperty(name="Лог шапки",description="Включити лог основної шапки",default=False,)
    use_Logs_Textures = BoolProperty(name="Лог текстур",description="Включити лог назв текстур",default=False,)
    use_Logs_Material = BoolProperty(name="Лог материалив",description="Включити лог матеріалів",default=False,)
    use_Logs_Grups    = BoolProperty(name="Лог груп",description="Включити лог назв груп",default=False,)
    use_Logs_Poligon  = BoolProperty(name="Лог полисетки",description="Включити доступ до логів вершин,груп,нормалів,UV",default=False,)
    use_Logs_Vertex   = BoolProperty(name="Лог Vertex",description="Включтити лог Вершин",default=False,)
    use_Logs_Weight   = BoolProperty(name="Лог Weight",description="Включити лог весов ",default=False,)
    use_Logs_Uv       = BoolProperty(name="Лог Uv",description="Включити лог UV вершин",default=False,)
    use_Logs_Mesh     = BoolProperty(name="Лог Полігонів",description="Включити лог Полігонів",default=False,)
    use_Logs_Normals = BoolProperty(name="Лог нормалив",description="Включити лог нормалів",default=False,)
    #
    
    download_bones = EnumProperty(
        name="Bone",
        items=(#('Old_bones', "Стара загрузка костей", ""),
               #('Basic_bones', "Основна загрузка костей", ""),
               ('Complete_bones', "Повна загрузка костей", "Загрузкакостей 2 матриці з інвертною"),
               ('Experement_bones', "Експерементальна загрузка костей", ""),
               ),
        default='Complete_bones',
        )
    
    object_tiyp = EnumProperty(
        name="",
        items=(('Pets', "Пети", ""),
               ('Weapons', "Оружея", ""),
               ('Casuals', "Стиль", ""),
               ),
        default='Pets',
        )
    
    object_сasuals_tiyp = EnumProperty(
        name="",
        items=(('Man', "Чоловичий", ""),
               ('Woomen', "Жіночий", ""),
               ),
        default='Man',
        )
    
    # функция виведення меню
    def draw(self, context):
        try:
            # Взяття информациї з Property свойств обєкта
            self.ski_tiyp = bpy.context.object.ski_tiyp                                             # @UndefinedVariable
            self.type_mask = bpy.context.object.type_mask                                           # @UndefinedVariable
        except AttributeError:
            pass
        layout = self.layout
        #layout.prop(self, "use_Object" , icon='OBJECT_DATA')
        
        objec = layout.box()
        objec.prop(self, "use_selection" )
        objec.prop(self, "object_tiyp" , icon='MOD_ARMATURE')
        if self.object_tiyp == "Casuals" :
            objec.prop(self, "object_сasuals_tiyp" , icon='MOD_ARMATURE')
            
        objec.prop(self, "use_root" ,)
        objec.prop(self, "ski_tiyp" , icon='MOD_ARMATURE')
        objec.prop(self, "type_mask", icon='MOD_ARMATURE')
           

        layout = self.layout
        layout.label("Weight Paint", icon='WPAINT_HLT')
        row = layout.row()
        row.alignment = 'LEFT'
        
        bones = row.box()
        #bones.prop(self, "use_download_weight" , icon='GROUP_VERTEX')
        bones.prop(self, "download_bones" , icon='GROUP_VERTEX')
        #bones.prop(self, "Bone_1" , icon='BONE_DATA')
        layout = layout.row()
        Log = layout.box()
        Log.prop(self, "use_Logs" , icon='ERROR')
        if self.use_Logs:
            row = layout.row()
            row.alignment = 'LEFT'
            #Log = row.box()
            Log.prop(self, "use_Logs_rewrite" , icon='FILE_REFRESH')
            Log.prop(self, "use_Logs_Title" , icon='COLLAPSEMENU')
            Log.prop(self, "use_Logs_Textures", icon='TEXTURE')
            Log.prop(self, "use_Logs_Material", icon='MATERIAL')
            Log.prop(self, "use_Logs_Grups", icon='WPAINT_HLT')
            Log.prop(self, "use_Logs_Poligon", icon='TRIA_DOWN')
            if self.use_Logs_Poligon:
                Log = Log.box()
                Log.prop(self, "use_Logs_Vertex", icon='OUTLINER_OB_LATTICE')
                Log.prop(self, "use_Logs_Weight", icon='WPAINT_HLT')
                Log.prop(self, "use_Logs_Uv", icon='TPAINT_HLT')
                Log.prop(self, "use_Logs_Mesh", icon='OBJECT_DATA')
                Log.prop(self, "use_Logs_Normals", icon='LATTICE_DATA')
    #
    def execute(self, context):
#         sys.path.append(sys.path[1]+'/io_Perfect_world')
#         import export_ski
#         export_ski.save(self, context, self.filepath, 
#                     self.ski_tiyp,
#                     self.type_mask,
#                     self.download_bones,
#                     self.use_root,
#                     self.use_log,
#                     self.use_save,
#                     self.object_tiyp)
        
        offloading(self,self.filepath)
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(ExportSki)
    
def unregister():
    bpy.utils.unregister_class(ExportSki)
    

if __name__ == "__main__":
    register()
    # test call
    bpy.ops.export_ski.some_data('INVOKE_DEFAULT')  # @UndefinedVariable
    
