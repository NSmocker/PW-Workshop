'''
Created on 24.12.2014
@author: user
'''

import bpy.utils
import os
import struct
import mathutils
import time

from bpy.props import StringProperty, BoolProperty, EnumProperty,IntProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


#class DataImporter:
def Download(self,filepath):
    
    self.report({'INFO'}, "#===========================================================================\n# Початок импорта Ski файла\n#===========================================================================")
    self.report({'INFO'}, '\nimporting obj %r' % filepath )  
    time_main = time.time()
    
    file_object = open(filepath , 'rb')
    file_object.read(8)
    ski_tiyp = struct.unpack('<I', file_object.read(4))[0]
    obj_type_count = struct.unpack('<4I', file_object.read(16)) # Обекти
    L3 = struct.unpack('<I', file_object.read(4))[0]            # textures || texture_count
    L4 = struct.unpack('<I', file_object.read(4))[0]            # material || material_count
    L5 = struct.unpack('<I', file_object.read(4))[0]            # num_bips
    L6 = struct.unpack('<I', file_object.read(4))[0]            # unknown_2 || (всегда значение 0 найдено до сих пор)
    type_mask = struct.unpack('<I', file_object.read(4))[0]     # type_mask || определяет количество костей в *.bon файла
    
    
    if self.use_Logs_Title: #логи шапки
        self.report({'OPERATOR'}, '_________________________________________________')
        self.report({'OPERATOR'}, '| Тип *.ski файла                 | %.2i          |' % ski_tiyp)
        self.report({'OPERATOR'}, '| Кількість обектів файла         | %.2i %.2i %.2i %.2i |' % obj_type_count)
        self.report({'OPERATOR'}, '| Кількість текстур               | %.2i          |' % L3)
        self.report({'OPERATOR'}, '| Кількість матеріалів            | %.2i          |' % L4)
        self.report({'OPERATOR'}, '| Кількість костей                | %.2i          |' % L5)
        self.report({'OPERATOR'}, '| L6                              | %.2i          |' % L6)
        self.report({'OPERATOR'}, '| Количество костей в *.bon файлі | %.2i          | ' % type_mask)
        self.report({'OPERATOR'}, '*************************************************')
        
    
    bpy.types.Object.ski_tiyp  = IntProperty ( name = "Ski tiyp"  , min = 0 , max = 100 , default = ski_tiyp)
    bpy.types.Object.type_mask = IntProperty ( name = "Type mask" , min = 0 , max = 100 , default = type_mask) 
    struct.unpack('<15I', file_object.read(60)) # далі 60 байт всех 0
    
    #--- Загрузка костей якшо ski_tiyp = 9
    if ski_tiyp == 9:
        name_bon = Download_Bip(self,ski_tiyp,L5,file_object)
    else:                
        name_bon = False
        name_bon = Download_Bip_in_Ski()
        
    time_new = time.time()
    self.report({'INFO'}, "Назви костей загружені: за %.4f секнд." % ( (time_new - time_main)) )
    #--- Загрузка пути текстури 
    matrix_img_textures = Download_Textures(self,L3,filepath,file_object)
    
    time_new = time.time()
    self.report({'INFO'}, "Текстури загружені: за %.4f секнд." % ( (time_new - time_main)) )
    
    #--- Загрузка матеріалу
    mat = Download_Material(self,L4,file_object)
    
    time_new = time.time()
    self.report({'INFO'}, "Матеріали загружені: за %.4f секнд." % ( (time_new - time_main)) )  

    #--- Загрузка сетки обекта
    if obj_type_count[0] > 0 : ob = Download_Mesh_0(self,obj_type_count,file_object,name_bon,matrix_img_textures,mat)
    if obj_type_count[1] > 0 : ob = Download_Mesh_1(self,obj_type_count,file_object,name_bon,matrix_img_textures,mat)
    
    self.report({'INFO'}, "Полісетка загружена" )  
    
    #--- Присвоэння свойст обэкту
    ob.type_mask = type_mask
    ob.ski_tiyp = ski_tiyp
    file_object.close()
    
    time_new = time.time()
    self.report({'INFO'}, "#===========================================================================\n# Кінець импорта Ski файла\n#===========================================================================")
    self.report({'INFO'}, "Імпорт закінчено: за %.4f секнд." % ( (time_new - time_main)) )  
    
    return {'FINISHED'}

def Download_Bip_in_Ski():
#===============================================================================
# Загрузка костей якшо ski_tiyp = 8
#===============================================================================
    name_bon = {}
    i=0
    try:
        for bone in bpy.data.objects["Bone1"].data.bones :
            name_bon[i] = bone.name
            i+=1
    except KeyError:
        name_bon = False
    return (name_bon)

def Download_Bip(self,ski_tiyp,num_bips,file_object):
#===============================================================================
# Загрузка костей якшо ski_tiyp = 9
#===============================================================================
    name_bon = {}
    for i in range(num_bips):
        NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
        name_bon[i] = file_object.read(NAME_TYP).decode('gbk')
        if self.use_Logs_Grups:
            self.report({'OPERATOR'}, '%.2i ) %s' % (i,name_bon[i]) )
    return (name_bon)


def Download_Textures(self,texture_count,filepath,file_object):
    matrix_img_textures = {}
    for j in range(texture_count) :
        NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
        #назва текстури
        imagepath = (file_object.read(NAME_TYP).decode('gbk'))
        if self.use_Logs_Textures:
            self.report({'OPERATOR'}, '%i' % (NAME_TYP))
            self.report({'OPERATOR'}, 'Назва текстури  %s ' % imagepath)
        if self.use_textures:
            #папка модели
            path = ( os.path.dirname(filepath) )
            #пошук тектури
            for floder in os.listdir(path) :
                if floder.find(".") == -1 :
                    path1 = os.path.join(path,floder)
                    for name in os.listdir(path1) :
                            if name[:-4] == imagepath[:-4] or name[:-4] == imagepath[:-4].lower() :
                                if name[-3:] == "dds" or name[-3:] == ["DDS"]:                                           
                                    name_tex= name
                                    img = bpy.data.images.load(os.path.join(path,floder,name))
                    
            try:
                # Создание текстуры image из загруженного рисунка
                cTex = bpy.data.textures.new(name_tex+str(j), type = 'IMAGE')
                cTex.use_alpha = True
                cTex.image = img
                matrix_img_textures[j] = cTex
                if self.use_Logs_Textures:
                    self.report({'OPERATOR'}, 'Текстура загружена %s ' % img)
            except UnboundLocalError:
                    self.report({'ERROR'}, "Текстура не загружина:  %s" % (path1) )
    return (matrix_img_textures)

def Download_Material(self,material_count,file_object):
    mat = {}
#===============================================================================
#Загрузка матеріалу                      !!! НЕЗРОБЛЕНО !!!
#===============================================================================
    for i in range(material_count) :
        file_object.read(11)
        diffuse_color  = struct.unpack('<3f', file_object.read(12))    # Diffuse Color, R,G,B +?
        diffuse_intensity = struct.unpack('<f', file_object.read(4))[0]
        specular_color           = struct.unpack('<3f', file_object.read(12))    # Specular Color, R,G,B, +?
        specular_intensity = struct.unpack('<f', file_object.read(4))[0]
        emissive_color = struct.unpack('<3f', file_object.read(12))    # 
        emissive_intensity = struct.unpack('<f', file_object.read(4))[0]
        unknown_block  = struct.unpack('<3f', file_object.read(12))    #
        unknown_intensity = struct.unpack('<f', file_object.read(4))[0]
        alpha  = struct.unpack('<f', file_object.read(4))[0]
        bIsClothing = struct.unpack('<B', file_object.read(1))[0]        # One BYTE  1
        
        if self.use_Logs_Material :
            self.report({'OPERATOR'}, '_________________________________________________')
            self.report({'OPERATOR'}, 'Диффузі %s %s'%(diffuse_color,diffuse_intensity))
            self.report({'OPERATOR'}, 'Блик    %s %s'%(specular_color,specular_intensity))
            self.report({'OPERATOR'}, 'Емісі   %s %s'%(emissive_color,emissive_intensity))
            self.report({'OPERATOR'}, 'Неопознаний %s %s'%(unknown_block,unknown_intensity))
            self.report({'OPERATOR'}, 'Альфа прозрачність %s'%(alpha)) 
            self.report({'OPERATOR'}, 'Отсікать задні грані %s'%(bIsClothing))

        mat[i] = bpy.data.materials.new('Материал'+str(i))
        mat[i].diffuse_color= diffuse_color 
        mat[i].diffuse_intensity = diffuse_intensity
        mat[i].specular_color = specular_color
        mat[i].specular_intensity = specular_intensity
        mat[i].mirror_color = emissive_color
        mat[i].raytrace_mirror.gloss_factor = emissive_intensity
        mat[i].subsurface_scattering.color = unknown_block
        mat[i].subsurface_scattering.color_factor = unknown_intensity
        mat[i].alpha = 0#alpha
        if alpha==1:
            mat[i].use_transparency = 0
        else:
            mat[i].use_transparency = 1
            
        mat[i].game_settings.use_backface_culling = bIsClothing
        mat[i].transparency_method = 'MASK'

        
    return (mat)

def Download_Mesh_0(self,obj_type_count,file_object,name_bon,matrix_img_textures,mat):
    for i in range(obj_type_count[0]):
        verts = []
        faces = []
        vertices_raw = []
        normal = []  
        verts_tex = []
        uvtextures = []
        vertex_normal = []
        
        vertex_color = {}
        
        if self.download_bones == "Complete_bones" :
            vgroups_a_1 = {}
            vgroups_b_1 = {}
            
            vgroups_a_2 = {}
            vgroups_b_2 = {}
            
            vgroups_a_3 = {}
            vgroups_b_3 = {}
            
            vgroups_a_4 = {}
            vgroups_b_4 = {}
            
        if self.download_bones == "Experement_bones" :
            vgroups_a = {}
            vgroups_b = {}
            
        if self.download_bones == "Old_bones" :
            vgroups_a_1 = {}
            vgroups_b_1 = {}
            
            vgroups_a_2 = {}
            vgroups_b_2 = {}
            
            vgroups_a_3 = {}
            vgroups_b_3 = {}
            
            vgroups_a_4 = {}
            vgroups_b_4 = {}

        NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
        name = file_object.read(NAME_TYP).decode('gbk') 
        texture_index = struct.unpack('<I', file_object.read(4))[0]
        material_index = struct.unpack('<I', file_object.read(4))[0]
        vertex_count = struct.unpack('<I', file_object.read(4))[0]
        index_count = struct.unpack('<I', file_object.read(4))[0]
        
        if self.use_Logs_Poligon:
            self.report({'OPERATOR'}, '_________________________________________________')
            self.report({'OPERATOR'}, '%i )  %s'%(i,name))
            self.report({'OPERATOR'}, 'texture_index %s'%(texture_index))
            self.report({'OPERATOR'}, 'material_index %s'%(material_index))
            self.report({'OPERATOR'}, 'index_count(num_faces*3): %i'%(index_count))
            self.report({'OPERATOR'}, 'vertex_count %i'%(vertex_count)) 

#===============================================================================
#Создайте новый блок данных сетки
#===============================================================================
        mesh = bpy.data.meshes.new(name)
        for j in range(vertex_count) :
#===============================================================================
#for x in xrange(vertex_count):
#1. VERTICES (position)
#Read in order -z,x,y
#===============================================================================
            x = struct.unpack('<f', file_object.read(4))[0]
            y = struct.unpack('<f', file_object.read(4))[0]
            z = struct.unpack('<f', file_object.read(4))[0]
            
            if self.use_Logs_Vertex:
                self.report({'OPERATOR'}, 'V %f %f %f '%(x,y,z))
#===============================================================================
# Список координат вершин
#===============================================================================
            if self.use_root == False:
                verts.extend( [-z, x, y] )
            else:
                #verts.extend( [-x, -z, y] )
                verts.extend( [x, -z, y] )
#===============================================================================
#3. Веса меша
#===============================================================================
            vertex_color[0] = struct.unpack('<f', file_object.read(4))[0]
            vertex_color[1] = struct.unpack('<f', file_object.read(4))[0]
            vertex_color[2] = struct.unpack('<f', file_object.read(4))[0]
            vgroups_n = struct.unpack('<4B', file_object.read(4))        # e.g. [13,12,0,0] or [15,16,17,12] or [26,0,4,2]
            
            if self.use_Logs_Weight:
                self.report({'OPERATOR'}, 'VG %f %f %f '%(vertex_color[0],vertex_color[1],vertex_color[2]))
                self.report({'OPERATOR'}, 'GR %s %s %s %s '%(vgroups_n[0],vgroups_n[1],vgroups_n[2],vgroups_n[3]))
            
            if self.use_download_weight:
                if self.download_bones == "Complete_bones" :
                    for I in range(3) :
                        vertex_color[I] = round(vertex_color[I] ,6)            
                    if vertex_color[0] > 0 :
                        vgroups_a_1,vgroups_b_1 = Calculation_Grup(vgroups_n[0],vertex_color[0],vgroups_a_1,vgroups_b_1,j)
                    if vertex_color[1] > 0 :
                        vgroups_a_2,vgroups_b_2 = Calculation_Grup(vgroups_n[1],vertex_color[1],vgroups_a_2,vgroups_b_2,j)
                    if vertex_color[2] > 0 :
                        vgroups_a_3,vgroups_b_3 = Calculation_Grup(vgroups_n[2],vertex_color[2],vgroups_a_3,vgroups_b_3,j)
                    vgroups_a_4,vgroups_b_4 = Calculation_Grup(vgroups_n[3],1-(vertex_color[0]+vertex_color[1]+vertex_color[2]),vgroups_a_4,vgroups_b_4,j)
                
                if self.download_bones == "Experement_bones" :
                    for I in range(3) :
                        vertex_color[I] = round(vertex_color[I] ,6)            
                    vgroups_a,vgroups_b = Calculation_Grup(vgroups_n[0],vertex_color[0],vgroups_a,vgroups_b,j)
                    vgroups_a,vgroups_b = Calculation_Grup(vgroups_n[1],vertex_color[1],vgroups_a,vgroups_b,j)
                    vgroups_a,vgroups_b = Calculation_Grup(vgroups_n[2],vertex_color[2],vgroups_a,vgroups_b,j)
                    vgroups_a,vgroups_b = Calculation_Grup(vgroups_n[3],1-(vertex_color[0]+vertex_color[1]+vertex_color[2]),vgroups_a,vgroups_b,j)
            
#===============================================================================
#4. Нормалі
#Читайте в порядке x,z,y
#===============================================================================
            nX,nZ,nY = struct.unpack('<3f', file_object.read(12))
            normal = mathutils.Vector()
            normal[0] = nX
            normal[1] = -nY
            normal[2] = nZ
            if self.use_Logs_Normal:
                self.report({'OPERATOR'}, 'NV %f %f %f '%(normal[0],normal[1],normal[2]))
            vertex_normal.extend((normal[0],normal[1],normal[2]) )  
#===============================================================================
#5. UV TEXTURES
#===============================================================================
            uv_coordinates_x = struct.unpack('<f',file_object.read(4))[0]
            uv_coordinates_y =1- struct.unpack('<f',file_object.read(4))[0]
            uv_coordinates= uv_coordinates_x,uv_coordinates_y
            verts_tex.append ( uv_coordinates )
            if self.use_Logs_Uv:
                self.report({'OPERATOR'}, 'UV %f %f '%(uv_coordinates_x ,uv_coordinates_y))
                
        num_faces =int ( index_count/3)
#===============================================================================
#6. Poligons
#===============================================================================
        for j in range(num_faces) : 
            x = struct.unpack('<H', file_object.read(2))[0]
            y = struct.unpack('<H', file_object.read(2))[0]
            z = struct.unpack('<H', file_object.read(2))[0]
            vertices_raw.extend([x])
            vertices_raw.extend([y])
            vertices_raw.extend([z])
            faces.extend( (x, y, z , 0) )   
            uvtextures.extend(verts_tex[x])
            uvtextures.extend(verts_tex[y])
            uvtextures.extend(verts_tex[z])
            if self.use_Logs_Poligon :
                self.report({'OPERATOR'}, 'PL %f %f %f '%( x, y, z ))
#===============================================================================
# Создание пустых геометрии и топологии
#===============================================================================
        mesh.vertices.add (len(verts)/3)
        mesh.tessfaces.add(len(faces)/4)

#===============================================================================
# Добавить вершин
#===============================================================================
        mesh.vertices.foreach_set("co", verts)
#===============================================================================
# Добавить полигони
#===============================================================================
        mesh.tessfaces.foreach_set("vertices_raw", faces)
        mesh.tessfaces.foreach_set("normal", vertex_normal)
#===============================================================================
# Добавить uv кординати
#===============================================================================
        if verts_tex and mesh.tessfaces:
            uvtex = mesh.tessface_uv_textures.new()
            uvtex.name = "UVMap"
            data = uvtex.data
            for n in range(num_faces): 
                data[n].uv1 = uvtextures[  (n*6)],uvtextures[1+(n*6)]
                data[n].uv2 = uvtextures[2+(n*6)],uvtextures[3+(n*6)]
                data[n].uv3 = uvtextures[4+(n*6)],uvtextures[5+(n*6)]
#===============================================================================
#                    Треба переробити
#===============================================================================
        mesh.update(calc_edges=True)
        ob = bpy.data.objects.new(name, mesh)
        # виділити обєкт
        bpy.context.scene.objects.link(ob)
        
#=======================================================================
# Імпорт і приєднання текстури texture_index индекс текстури
#=======================================================================
        if self.use_textures:
            if mat[material_index].users == 0:
                try:
                    setMatTex(ob,mat[material_index],matrix_img_textures[texture_index])
                except KeyError :
                    self.report({'ERROR'}, "Текстура не загружина:")
            else:
                try:
                    mat[material_index] = mat[material_index].copy()
                    setMatTex(ob,mat[material_index],matrix_img_textures[texture_index])
                except KeyError :
                    self.report({'ERROR'}, "Текстура не загружина: ")
#=======================================================================
# Створення, запис груп. можуть бути проблеми за инт
#=======================================================================
        if self.use_download_weight:
            if self.download_bones == "Complete_bones" :
                # 1        
                if  type(name_bon) ==  bool :
                    for name in vgroups_a_1.keys():
                        grp = ob.vertex_groups.new("Bones"+str(name))
                        if type(vgroups_a_1[name]) is int:
                            v = vgroups_a_1[name]
                            w = vgroups_b_1[name]
                        else :
                            for a in range(len(vgroups_a_1[name])) :
                                v = vgroups_a_1[name][a]
                                w = vgroups_b_1[name][a]
                                grp.add([v], w, 'REPLACE')
                else:
                    for name in vgroups_a_1.keys():
                        if name_bon[name] :
                            grp = ob.vertex_groups.new(name_bon[name])
                            if type(vgroups_a_1[name]) is int:
                                v = vgroups_a_1[name]
                                w = vgroups_b_1[name]
                            else :
                                for a in range(len(vgroups_a_1[name])) :
                                    v = vgroups_a_1[name][a]
                                    w = vgroups_b_1[name][a]
                                    grp.add([v], w, 'REPLACE')
                                                       
                #2           
                if type(name_bon) ==  bool :
                    for name in vgroups_a_2.keys():
                        grp = ob.vertex_groups.new("Bones"+str(name)+('_1'))
                        if type(vgroups_a_2[name]) is int:
                            v = vgroups_a_2[name]
                            w = vgroups_b_2[name]
                        else :
                            for a in range(len(vgroups_a_2[name])) :
                                v = vgroups_a_2[name][a]
                                w = vgroups_b_2[name][a]
                                grp.add([v], w, 'REPLACE')
                else:
                    for name in vgroups_a_2.keys():
                        if name_bon[name] :
                            grp = ob.vertex_groups.new(name_bon[name]+('_1'))
                            if type(vgroups_a_2[name]) is int:
                                v = vgroups_a_2[name]
                                w = vgroups_b_2[name]
                            else :
                                for a in range(len(vgroups_a_2[name])) :
                                    v = vgroups_a_2[name][a]
                                    w = vgroups_b_2[name][a]
                                    grp.add([v], w, 'REPLACE')   
                #3           
                if type(name_bon) ==  bool :
                    for name in vgroups_a_3.keys():
                        grp = ob.vertex_groups.new("Bones"+str(name)+('_2'))
                        if type(vgroups_a_3[name]) is int:
                            v = vgroups_a_3[name]
                            w = vgroups_b_3[name]
                        else :
                            for a in range(len(vgroups_a_3[name])) :
                                v = vgroups_a_3[name][a]
                                w = vgroups_b_3[name][a]
                                grp.add([v], w, 'REPLACE')
                else:
                    for name in vgroups_a_3.keys():
                        if name_bon[name] :
                            grp = ob.vertex_groups.new(name_bon[name]+('_2'))
                            if type(vgroups_a_3[name]) is int:
                                v = vgroups_a_3[name]
                                w = vgroups_b_3[name]
                            else :
                                for a in range(len(vgroups_a_3[name])) :
                                    v = vgroups_a_3[name][a]
                                    w = vgroups_b_3[name][a]
                                    grp.add([v], w, 'REPLACE')
                #4          
                if type(name_bon) ==  bool :
                    for name in vgroups_a_4.keys():
                        grp = ob.vertex_groups.new("Bones"+str(name)+('_3'))
                        if type(vgroups_a_4[name]) is int:
                            v = vgroups_a_4[name]
                            w = vgroups_b_4[name]
                        else :
                            for a in range(len(vgroups_a_4[name])) :
                                v = vgroups_a_4[name][a]
                                w = vgroups_b_4[name][a]
                                grp.add([v], w, 'REPLACE')
                else:
                    for name in vgroups_a_4.keys():
                        if name_bon[name] :
                            grp = ob.vertex_groups.new(name_bon[name]+('_3'))
                            if type(vgroups_a_4[name]) is int:
                                v = vgroups_a_4[name]
                                w = vgroups_b_4[name]
                            else :
                                for a in range(len(vgroups_a_4[name])) :
                                    v = vgroups_a_4[name][a]
                                    w = vgroups_b_4[name][a]
                                    grp.add([v], w, 'REPLACE')              
                       
            if self.download_bones == "Experement_bones" :                     
                if type(name_bon) ==  bool :
                    for name in vgroups_a.keys():
                        grp = ob.vertex_groups.new("Bones"+str(name))
                        if type(vgroups_a[name]) is int:
                            v = vgroups_a[name]
                            w = vgroups_b[name]
                        else :
                            for a in range(len(vgroups_a[name])) :
                                v = vgroups_a[name][a]
                                w = vgroups_b[name][a]
                                grp.add([v], w, 'REPLACE')
                else:
                    for name in vgroups_a.keys():
                        try:
                            if name_bon[name] :
                                grp = ob.vertex_groups.new(name_bon[name])
                                if type(vgroups_a[name]) is int:
                                    v = vgroups_a[name]
                                    w = vgroups_b[name]
                                else :
                                    for a in range(len(vgroups_a[name])) :
                                        v = vgroups_a[name][a]
                                        w = vgroups_b[name][a]
                                        grp.add([v], w, 'REPLACE')                    
                        except KeyError:
                            grp = ob.vertex_groups.new("ERROR_Bones"+str(name))
                            if type(vgroups_a[name]) is int:
                                v = vgroups_a[name]
                                w = vgroups_b[name]
                            else :
                                for a in range(len(vgroups_a[name])) :
                                    v = vgroups_a[name][a]
                                    w = vgroups_b[name][a]
                                    grp.add([v], w, 'REPLACE')      
        try:
            #ПРИЄДНАННЯ МЕША ДО АРМАТУРИ
            ob.parent = bpy.data.objects["Bone1"]
            try:
                #МЕШУ МОДИФІКАТОР АРМАТУРИ
                mod = ob.modifiers.new("Bone2", 'ARMATURE')
                mod.object = bpy.data.objects["Bone2"]
                mod.use_bone_envelopes = False
                mod.use_vertex_groups = True
            except KeyError:
                pass
            #МЕШУ МОДИФІКАТОР АРМАТУРИ
            mod = ob.modifiers.new("Bone1", 'ARMATURE')
            mod.object = bpy.data.objects["Bone1"]
            mod.use_bone_envelopes = False
            mod.use_vertex_groups = True
        except KeyError:
            self.report({'ERROR'}, "До арматури не приєднано: %s <-to-> %s" % (ob,"Bone1") )   
    return (ob)

def Download_Mesh_1(self,obj_type_count,file_object,name_bon,matrix_img_textures,mat):
    for i in range(obj_type_count[1]):
        verts = []
        faces = []  
        normal = []  
        verts_tex = []
        uvtextures = []
        vertex_normal = []
        NAME_TYP = struct.unpack('<I', file_object.read(4))[0]
        name = file_object.read(NAME_TYP).decode('gbk') 
        texture_index = struct.unpack('<I', file_object.read(4))[0]
        material_index = struct.unpack('<I', file_object.read(4))[0]
        bone_index = struct.unpack('<I', file_object.read(4))[0]
        vertex_count = struct.unpack('<I', file_object.read(4))[0]
        index_count = struct.unpack('<I', file_object.read(4))[0]
        
        if self.use_Logs_Mesh:
            print(i,")",name)
            print('texture_index',texture_index)
            print('material_index',material_index)
            print ("bone_index",bone_index)
            print ("vertex_count:",vertex_count)
            print ("index_count(num_faces*3):",index_count)
        
        mesh = bpy.data.meshes.new(name)
        for j in range(vertex_count) :
#===============================================================================
#for x in xrange(vertex_count):
#1. VERTICES (position)
#Read in order -z,x,y
#===============================================================================
            x = struct.unpack('<f', file_object.read(4))[0]
            y = struct.unpack('<f', file_object.read(4))[0]
            z = struct.unpack('<f', file_object.read(4))[0]
#===============================================================================
# Список координат вершин
#===============================================================================
            if self.use_root == False:
                verts.extend( [-z, x, y] )
            else:
                verts.extend( [-x, -z, y] )
#===============================================================================
#4. Нормалі
#Читайте в порядке x,z,y
#===============================================================================
            nX,nZ,nY = struct.unpack('<3f', file_object.read(12))
            normal = mathutils.Vector()
            normal[0] = -nX
            normal[1] = -nY
            normal[2] = -nZ
            vertex_normal.extend((normal[0],normal[1],normal[2]) )  
#===============================================================================
#5. UV TEXTURES
#===============================================================================
            uv_coordinates_x = struct.unpack('<f',file_object.read(4))[0]
            uv_coordinates_y =1- struct.unpack('<f',file_object.read(4))[0]
            verts_tex.append ( (uv_coordinates_x,uv_coordinates_y) )
#===============================================================================
#6. Poligon
#===============================================================================
        num_faces =int ( index_count/3) 
        for j in range(num_faces) : 
            x = struct.unpack('<H', file_object.read(2))[0]
            y = struct.unpack('<H', file_object.read(2))[0]
            z = struct.unpack('<H', file_object.read(2))[0]
            faces.extend( (x, y, z , 0) )   
            uvtextures.extend(verts_tex[x])
            uvtextures.extend(verts_tex[y])
            uvtextures.extend(verts_tex[z])

#===============================================================================
# Создание пустых геометрии и топологии
#===============================================================================
        mesh.vertices.add(len(verts)/3)
        mesh.tessfaces.add(len(faces)/4)
#===============================================================================
# Добавить вершин
#===============================================================================
        mesh.vertices.foreach_set("co", verts)
# Добавить полигони
#===============================================================================
        mesh.tessfaces.foreach_set("vertices_raw", faces)
#===============================================================================
# Добавить uv textures
#===============================================================================
        if verts_tex and mesh.tessfaces:
            uvtex = mesh.tessface_uv_textures.new()
            uvtex.name = name
            data = uvtex.data
            for j in range(num_faces): 
                data[j].uv1 = uvtextures[(j*6)],uvtextures[1+(j*6)]
                data[j].uv2 = uvtextures[2+(j*6)],uvtextures[3+(j*6)]
                data[j].uv3 = uvtextures[4+(j*6)],uvtextures[5+(j*6)]
#===============================================================================
#           Треба переробити
#===============================================================================
        
        mesh.tessfaces.foreach_set("normal", vertex_normal)
        mesh.update()
        
        ob = bpy.data.objects.new(name, mesh)
        bpy.context.scene.objects.link(ob)
#=======================================================================
# Імпорт і приєднання текстури 
#=======================================================================
        if self.use_textures:
            if mat[material_index].users == 0:
                setMatTex(ob,mat[material_index],matrix_img_textures[texture_index])
            else:
                mat[material_index] = mat[material_index].copy()
                setMatTex(ob,mat[material_index],matrix_img_textures[texture_index])
            
                mod = ob.constraints.new("Bone1", 'ARMATURE')
                mod.object = bpy.data.objects["Bone1"]
                mod.use_bone_envelopes = False
                mod.use_vertex_groups = True
        try:
            #ПРИЄДНАННЯ МЕША ДО АРМАТУРИ
            ob.parent = bpy.data.objects["Bone1"]
            #МЕШУ ПЕРЕОБРАЗОВАННЯ
            con = ob.constraints.new(type='COPY_TRANSFORMS')
            con.target = bpy.data.objects["Bone1"]
            con.subtarget = bpy.data.objects["Bone1"].data.bones[bone_index].name
        except KeyError:
            self.report({'ERROR'}, "До арматури не приєднано: %s <-to-> %s" % (ob,"Bone1") )   
    
        return (ob)

def Calculation_Grup(V,A,vgroups_a,vgroups_b,j):
#===============================================================================
#Загрузка ГРУП
#       оптимізація зроблена
#===============================================================================
#j номер vertex
#V група
#A вес
# vgroups_a групи
# vgroups_b веса# перевигра чи е група
    if V in vgroups_a:
        #якшо група є дані переписуємо в тимчасові велечини
        Bit = vgroups_a[V]

        #перевірка чи одна вершина вгрупі
        if type(vgroups_a[V]) == int :
            # в групі 1 вершина
            #перевірка чи одна вершина НЕ дублюеця
            if vgroups_a[V] == j :
                pass
            else :
                # якшо білше 1 вершити створення списків
                vgroups_a[V] = [ vgroups_a[V], j ]
                vgroups_b[V] = [ vgroups_b[V], A ]
        else :
            if j in Bit :
                pass
            else:
                vgroups_a[V].append(j)
                vgroups_b[V].append(A)
    else :
        vgroups_a[V] = j
        vgroups_b[V] = A
    return (vgroups_a,vgroups_b)


def setMatTex(ob,mat,tex):
# Добавление текстурного слота для цветной текстуры
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True 
    mtex.use_map_color_emission = True 
    mtex.emission_color_factor = 0.5
    mtex.use_map_emit = True
    mtex.use_map_density = True 
    mtex.mapping = 'FLAT'
    me = ob.data
    me.materials.append(mat)
    
    return ()

    
class Import_ski (Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_ski.some_data"
    bl_label = "Import Ski Data"

    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".ski"
    filter_glob = StringProperty(
            default="*.ski",
            options={'HIDDEN'},
            )
    Object       = BoolProperty(name="Object",default=False,)
    Weight_Paint = BoolProperty(name="Weight Paint",default=False,)
    #меню логів
    use_Logs          = BoolProperty(name="Лог",description="Виведення логів",default=False,)
    use_Logs_Title    = BoolProperty(name="Лог шапки",description="Exause_Logs_mple Tooltip",default=False,)
    use_Logs_Textures = BoolProperty(name="Лог текстур",description="Example Tooltip",default=False,)
    use_Logs_Material = BoolProperty(name="Лог материалив",description="Example Tooltip",default=False,)
    use_Logs_Grups    = BoolProperty(name="Лог груп",description="Example Tooltip",default=False,)
    use_Logs_Poligon  = BoolProperty(name="Лог полисетки",description="Example Tooltip",default=False,)
    use_Logs_Vertex   = BoolProperty(name="Лог Vertex",description="Example Tooltip",default=False,)
    use_Logs_Weight   = BoolProperty(name="Лог Weight",description="Example Tooltip",default=False,)
    use_Logs_Uv       = BoolProperty(name="Лог Uv",description="Example Tooltip",default=False,)
    use_Logs_Mesh     = BoolProperty(name="Лог Mesh",description="Example Tooltip",default=False,)
    use_Logs_Normal   = BoolProperty(name="Лог Нормалів",description="Example Tooltip",default=False,)
    
    
    use_root = BoolProperty(name="RotZ-90%",description="Поворот на 90%",default= True,)
    use_textures = BoolProperty(name="Download Textures",description="Загружати текстуры",default= True,)
    use_download_weight = BoolProperty(name="Download Weight",description="Загружати веса",default= True,)
    
    download_bones = EnumProperty(
            name="",
            items=(
                   ('Experement_bones', "Експерементальна загрузка костей", "Загрузкакостей токо 1 матриці без інвертної"),
                   ('Complete_bones', "Повна загрузка костей", "Загрузкакостей 2 матриці з інвертною"),
                   ),
            default='Experement_bones',
            )
#     download_bones = EnumProperty(
#             name="",
#             items=(('Old_bones', "Стара загрузка костей", ""),
#                    ('Complete_bones', "Основна загрузка костей", "Complete_bones"),
#                    ('Experement_bones', "Повна загрузка костей", "Experement_bones"),
#                    ),
#             default='Experement_bones',
#             )
            
    def execute(self, context):
        
        Download(self,self.filepath)
#         from . import import_ski
#         import_ski.Download(self,self.filepath)
        return {'FINISHED'}
        
    # функция виведення меню
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Object" , icon='OBJECT_DATA')
        if self.Object:
            row = layout.row()
            row.alignment = 'LEFT'
            objec = row.box()
            objec.prop(self, "use_root" , icon='MOD_ARMATURE')
        
        layout = self.layout
        layout.label("Texture", icon='TEXTURE')
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(self, "use_textures" )
        
        layout = self.layout
        layout.label("Material", icon='MATERIAL')
        row = layout.row()
        row.alignment = 'LEFT'

        layout = self.layout
        layout.prop(self, "Weight_Paint" , icon='WPAINT_HLT')
        if self.Weight_Paint:
            row = layout.row()
            row.alignment = 'LEFT'
            bones = row.box()
            bones.prop(self, "use_download_weight" , icon='GROUP_VERTEX')
            bones.prop(self, "download_bones" , icon='GROUP_VERTEX')
            
        layout.prop(self, "use_Logs" , icon='ERROR')
        if self.use_Logs:
            row = layout.row()
            row.alignment = 'LEFT'
            Log = row.box()
            Log.prop(self, "use_Logs_Title" , icon='COLLAPSEMENU')
            Log.prop(self, "use_Logs_Textures", icon='TEXTURE')
            Log.prop(self, "use_Logs_Material", icon='MATERIAL')
            Log.prop(self, "use_Logs_Grups", icon='WPAINT_HLT')
            Log.prop(self, "use_Logs_Mesh", icon='OBJECT_DATAMODE')
            if self.use_Logs_Mesh:
                Log = Log.box()
                Log.prop(self, "use_Logs_Vertex", icon='EDITMODE_HLT')
                Log.prop(self, "use_Logs_Weight", icon='WPAINT_HLT')
                Log.prop(self, "use_Logs_Normal", icon='EMPTY_DATA')
                Log.prop(self, "use_Logs_Uv",     icon='TPAINT_HLT')
                Log.prop(self, "use_Logs_Poligon",icon='OUTLINER_OB_LATTICE')
                
def register():
    bpy.utils.register_class(Import_ski)

def unregister():
    bpy.utils.unregister_class(Import_ski)

if __name__ == "__main__":
    register()
    bpy.ops.import_ski.some_data('INVOKE_DEFAULT')  # @UndefinedVariable
