if (heapSize < 200000) then
        heapSize = 2000000 -- allow ~ 40 MB instead of just 7.5 MB. Prevents "Runtime Error: Out of scripter memory"
gname = getOpenFileName \
caption:"Open .bon from Bones folder" \
types:"SKI Bones (*.bon)|*.bon" \
historyCategory:"SKIObjectPresets"
g = fopen gname "rb"
fname = getOpenFileName \
caption:"Open .ski from Mesh folder" \
types:"SKI Mesh (*.ski)|*.ski" \
historyCategory:"SKIObjectPresets"
f = fopen fname "rb"

clearlistener()

fn readFixedString bstream fixedLen = (
local str = ""
for i = 1 to fixedLen do (
str += bit.intAsChar (ReadByte bstream #unsigned))
str
)

fn readColors fstream = (
	cR = (readfloat fstream) * 255
	cG = (readfloat fstream) * 255
	cB = (readfloat fstream) * 255
	cA = (readfloat fstream) * 255
	return (color cR cG cB cA)
	)

fn readHalfFloat fstream = (
    hf=readshort fstream #unsigned
    sign = bit.get hf 16
    exponent = (bit.shift (bit.and hf (bit.hexasint "7C00")) -10) as integer - 16
    fraction = bit.and hf (bit.hexasint "03FF")
    if sign==true then sign = 1 else sign = 0
    exponentF = exponent + 127
    outputAsFloat = bit.or (bit.or (bit.shift fraction 13) \
    (bit.shift exponentF 23)) (bit.shift sign 31)
    return bit.intasfloat outputasfloat*2
    )
	
struct weight_data
(
	boneids,weights
)

clearlistener()

fseek g 0x0 #seek_set
MOXBEKSA=readFixedString g 8
Version = ReadLong g
numBones = ReadLong g
numTotalBones = ReadLong g
Unk1 = ReadLong g
numTexture = ReadLong g
numMaterial = ReadLong g
CountLong = ReadLong g
Unk = ReadLong g
fseek g 0x3C #seek_cur
Print ("Info End @ 0x"+((bit.intAsHex(ftell g))as string))
BNArr = #()
for a = 1 to numTotalBones do (

BoneNameSize = ReadLong g	
BoneName = readFixedString g BoneNameSize
BoneId = ReadLong g 		
BoneParent = ReadLong g
BoneChild = ReadLong g 	
LongCount = ReadLong g 	
	
c11 = ReadFloat g; c12 = ReadFloat g; c13 = ReadFloat g; c14 = ReadFloat g	
c21 = ReadFloat g; c22 = ReadFloat g; c23 = ReadFloat g; c24 = ReadFloat g	
c31 = ReadFloat g; c32 = ReadFloat g; c33 = ReadFloat g; c34 = ReadFloat g
c41 = ReadFloat g; c42 = ReadFloat g; c43 = ReadFloat g; c44 = ReadFloat g	
	
d11 = ReadFloat g; d12 = ReadFloat g; d13 = ReadFloat g; d14 = ReadFloat g	
d21 = ReadFloat g; d22 = ReadFloat g; d23 = ReadFloat g; d24 = ReadFloat g	
d31 = ReadFloat g; d32 = ReadFloat g; d33 = ReadFloat g; d34 = ReadFloat g
d41 = ReadFloat g; d42 = ReadFloat g; d43 = ReadFloat g; d44 = ReadFloat g	
	
for x = 1 to LongCount do (
Unk1 = Readlong g  
)		

tfm = matrix3 [d11,d12,d13] [d21,d22,d23] [d31,d32,d33] ([d41,d42,d43]*100)	
tfm2 = matrix3 [c11,c12,c13] [c21,c22,c23] [c31,c32,c33] [c41,c42,c43]	

if (BoneParent != -1) do (
tfm2 = tfm2 * BNArr[(BoneParent + 1)].objecttransform	
)	
newBone = bonesys.createbone	\
				  tfm.row4	\
				  (tfm.row4 + 0.01 * (normalize tfm.row1)) \
				  (normalize tfm.row3)
			newBone.name = BoneName
			newBone.width  = 0.01
			newBone.height = 0.01
			newBone.transform =  inverse tfm
			newBone.setBoneEnable false 0
			newBone.wirecolor = white
			newbone.showlinks = true
			newBone.pos.controller      = TCB_position ()
			newBone.rotation.controller = TCB_rotation ()	
 if (BoneParent != -1) then
 newBone.parent = BNArr[(BoneParent)+1]						  
append BNArr newBone					  
)	

rootRT = dummy name:"Main_Root" boxsize:[.1,.1,.1]
for b in BNArr where b.parent==undefined do b.parent = rootRT
rootRT.transform = (matrix3 [-1,0,0] [0,0,1] [0,-1,0] [0,0,0])

Print ("Bone End @ 0x"+((bit.intAsHex(ftell g))as string))

fclose g	
	
BoneNamesArray = #()	
fseek f 0x0 #seek_set
MOXBIKSA=readFixedString f 8
Version = ReadLong f
numSkinObjext = ReadLong f
numStaticObject = ReadLong f
Unk1 = ReadLong f
Unk2 = ReadLong f
numTexture = ReadLong f
numMaterial = ReadLong f
numUsedBones = ReadLong f
Unk3 = ReadLong f
numSkeletonBones = ReadLong f
fseek f 0x3C #seek_cur
if Version==8 then fseek f 0x0 #seek_cur	
if Version!=8 then	
for a = 1 to numUsedBones Do (
BoneNameSize = ReadLong f
BName = readFixedString f BoneNameSize
append BoneNamesArray BName	
)
	textureArray = #()
	for i = 1 to numTexture do (
		texture_name = readFixedString f (readlong f)
		)
	matArray = #()
	for i = 1 to numMaterial do (
		MtlName = readFixedString f 11
		Mtl = standardmaterial ambient:(readColors f) diffuse:(readColors f) specular:(readColors f) twosided:true
		Mtl.selfIllumColor = (readColors f)
		Mtl.useSelfIllumColor = on
		Mtl.specularLevel = (readfloat f)
		MtlId = readbyte f
		)
for a = 1 to numSkinObjext Do (
	
ModelNameSize = ReadLong f
ModelName = readFixedString f ModelNameSize
TextureID = ReadLong f
MatlID = ReadLong f
numVerts = ReadLong f
numFaces = ReadLong f
	
vertArray = #()
Facearray = #()	
UV_array = #()
Weight_array =#()
	
for x = 1 to numVerts Do (
vx = Readfloat f
vy = Readfloat f
vz = Readfloat f
	
weight1 = Readfloat f
weight2 = Readfloat f
weight3 = Readfloat f
weight4 = 0
	
bone1 = readbyte f #unsigned	
bone2 = readbyte f #unsigned	
bone3 = readbyte f #unsigned	
bone4 = readbyte f #unsigned	
	
n1= Readfloat f
n2 = Readfloat f
n3 = Readfloat f	

tu=ReadFloat f	
tv=ReadFloat f*-1	

w = (weight_data boneids:#() weights:#())
maxweight = 0
if(weight1 != 0) then
   maxweight = maxweight + weight1
if(weight2 != 0) then
   maxweight = maxweight + weight2
if(weight3 != 0) then
   maxweight = maxweight + weight3
if(weight4 != 0) then
   maxweight = maxweight + weight4


if(maxweight != 0) then (
      if(weight1 != 0) then (
         w1 = weight1 as float
         append w.boneids (bone1 + 1)
         append w.weights (w1)
      )
      if(weight2 != 0) then (
         w2 = weight2 as float
         append w.boneids (bone2 + 1)
         append w.weights (w2)
      )
      if(weight3 != 0) then (
         w3 = weight3 as float
         append w.boneids (bone3 + 1)
         append w.weights (w3)
      )
      if(weight4 != 0) then (
         w4 = weight4 as float
         append w.boneids (bone4 + 1)
        append w.weights (w4)
      )      
   )
append Weight_array w			   
append vertArray ([-vx,-vz,vy]*100)
append UV_array [tu,tv,0]	 
)	


for x = 1 to (numFaces/3) do 
(
f1 = (Readshort f #unsigned + 1) 
f2 = (Readshort f #unsigned + 1) 
f3 = (Readshort f #unsigned + 1) 
append Facearray [f3,f2,f1]
)

msh = mesh vertices:vertArray faces:faceArray
msh.numTVerts = UV_array.count
msh.name=ModelName
buildTVFaces msh
for j = 1 to UV_array.count do setTVert msh j UV_array[j]
for j = 1 to faceArray.count do setTVFace msh j faceArray[j]
msh.displayByLayer = false
msh.backfacecull = true
msh.wirecolor = (color 230 200 210)

if Version==8 then
(				
try(
max modify mode
select msh
skinMod = skin ()
addModifier msh skinMod
for i = 1 to BNArr.count do
(
	maxbone = BNArr[i] 
	if i != BNArr.count then 
		skinOps.addBone skinMod maxbone 0
	else
		skinOps.addBone skinMod maxbone 1
)
modPanel.setCurrentObject skinMod
for i = 1 to (numVerts) do (
   w = Weight_array[i]
   bi = #() --bone index array
   wv = #() --weight value array
   
   for j = 1 to w.boneids.count do
   (
      boneid = w.boneids[j]
      weight = w.weights[j]
      append bi boneid
      append wv weight
   )   
   
   skinOps.ReplaceVertexWeights skinMod i bi wv
   
)
)catch(format "Failed - New VertType!!!\n")
)

if Version!=8 then
(	
try(
max modify mode
select msh
skinMod = skin ()
addModifier msh skinMod	
for i = 1 to numUsedBones do
(
	maxbone = getnodebyname BoneNamesArray[i] 
	if i != numUsedBones then 
		skinOps.addBone skinMod maxbone 0
	else
		skinOps.addBone skinMod maxbone 1
)
modPanel.setCurrentObject skinMod
for i = 1 to (numVerts) do (
   w = Weight_array[i]
   bi = #() --bone index array
   wv = #() --weight value array
   
   for j = 1 to w.boneids.count do
   (
      boneid = w.boneids[j]
      weight = w.weights[j]
      append bi boneid
      append wv weight
   )   
   
   skinOps.ReplaceVertexWeights skinMod i bi wv
   
)
)catch(format "Failed - New VertType!!!\n")
)
)
  
for a = 1 to numStaticObject Do (
	
ModelNameSize = ReadLong f
ModelName = readFixedString f ModelNameSize
Unk1 = ReadLong f	
TextureID = ReadLong f
MatlID = ReadLong f
numVerts = ReadLong f
numFaces = ReadLong f
	
vertArray = #()
Facearray = #()	
UV_array = #()
Weight_array =#()
BNArr = #()	
	
for x = 1 to numVerts Do (
vx = Readfloat f
vy = Readfloat f
vz = Readfloat f
	
n1= Readfloat f
n2 = Readfloat f
n3 = Readfloat f	

tu=ReadFloat f	
tv=ReadFloat f*-1	
	   
append vertArray ([-vx,-vz,vy]*100)
append UV_array [tu,tv,0]	 
)	


for x = 1 to (numFaces/3) do 
(
f1 = (Readshort f #unsigned + 1) 
f2 = (Readshort f #unsigned + 1) 
f3 = (Readshort f #unsigned + 1) 
append Facearray [f3,f2,f1]
)

try(
msh = mesh vertices:vertArray faces:faceArray
msh.numTVerts = UV_array.count
msh.name=ModelName	
buildTVFaces msh
for j = 1 to UV_array.count do setTVert msh j UV_array[j]
for j = 1 to faceArray.count do setTVFace msh j faceArray[j]
msh.displayByLayer = false
msh.backfacecull = true
msh.wirecolor = (color 230 200 210)

)catch(format "Failed - Static Mesh Error!!!\n")
)

fclose f
