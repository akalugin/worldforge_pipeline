'''
Tool depends on Blender to Ogre exporter http://code.google.com/p/blender2ogre
'''

bl_info = {
	'name': 'Pipeline Tools',
	'category': 'WorldForge',
	'author': 'anisimkalugin.com',
	'version': (0, 0, 1),
	'blender': (2, 71, 0),
	'description': 'Worldforge Pipeline Tools',
	'warning': '',
	'wiki_url': ''
	}

import bpy, os, shutil
from bpy.types import Operator
# from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
#from mathutils import Vector
class RigAnimationUtilities:
	def __init__( self ):
		self.DEBUG = False
	
	def clean_vertex_groups( self, context ):
		sel = bpy.context.selected_objects

		for ob in sel:
			vertex_groups = ob.vertex_groups
			if len(ob.modifiers) > 0:
				rig = ob.modifiers[-1].object # get the rig
				bones = rig.data.bones
				
				
				if self.DEBUG:
					print( ob.name )
					print( rig.name )
					print( bones )
				#get data
				vgrp_list = [grp.name for grp in ob.vertex_groups]
				bone_list = [bone.name for bone in rig.data.bones if bone.use_deform ]

				#compare lists 
				del_group = [itm for itm in vgrp_list if itm not in bone_list]
				mkv_groups = [itm for itm in bone_list if itm not in vgrp_list]

				#add vertex groups based on armatures deformable bones
				[ob.vertex_groups.new(name) for name in mkv_groups] 

				# remove groups that are not part of the current armatures deformable bones
				# list comprehension code may be a bit too long
				[ob.vertex_groups.remove( ob.vertex_groups[ ob.vertex_groups.find( group ) ] ) for group in del_group]
				return True

		return False

class OgreMaterialManager:
	'''Worldforge material management utilites'''
	def __init__( self ):
		self.DEBUG = False
		
	def get_base_name( self, path ):
		bad_names_l = ['//..','texture','source','model',]
		tkns = path.split(os.sep)[1:-1]
		seps = []
		for i in range( len(tkns)):
			itm =  tkns[i]
			if not itm in bad_names_l:
			   seps.append(itm)
		if seps == []:
			return 'blender file name'
			#bpy.path.display_name_from_filepath(bpy.data.filepath)
		return seps[-1]

	def open_ogre_materials(self, context):
		'''opens ogre.material based on the texture file path'''
		sel = bpy.context.selected_objects
		tmp_txt = bpy.data.texts.new('{tmp}') #hacky shit

		for ob in sel:
			for slot in ob.material_slots:
				mat = slot.material

				if mat.active_texture == None:
					continue

				image_path = mat.active_texture.image.filepath
				ogre_mat_file = bpy.path.abspath(image_path)[:-5] + 'ogre.material'
				if os.path.isfile(ogre_mat_file):
					txt_datablock = bpy.data.texts

					filepaths = [itm.filepath for itm in bpy.data.texts]

					for dat in filepaths:
						exists = ogre_mat_file in filepaths
						if exists == False:
							bpy.ops.text.open(filepath=ogre_mat_file)
						
						if self.DEBUG == True:
							print ( '---- debug statements ----' )
							print ( image_path )
							print ( ogre_mat_file )
							print ( filepaths )
							print ( exists )
		bpy.data.texts.remove(tmp_txt)
#
	def get_ogre_mat_name( self, relative_path ):
		'''retrieves ogre.material based on the current image'''
		#ogre_mat_file = relative_path[:-5] + 'ogre.material'
		ogre_mat_file = bpy.path.abspath(relative_path)[:-5] + 'ogre.material'
		# ogre_mat_file = testPath[:-5] + 'ogre.material'
		matNames = []
		if os.path.isfile(ogre_mat_file):
			f = open(ogre_mat_file, 'r')
			for line in f:
				if line[:8] == 'material':
					matNames.append( line.split(' ')[1] )
			f.close()

		return matNames

	def write_to_text_datablock(self, b_list):
		'''writes out the list to a ogre mat textblock'''
		ogre_tdb = self.get_text_datablock()
		ogre_tdb.write('--------------\n')
		for itm in b_list:
			ogre_tdb.write('%s \n' % itm )

	def get_text_datablock( self, tdb = 'ogre_mats' ):
		'''gets/creates a text data block (tdb)'''
		txt_datablock = bpy.data.texts.find( tdb )
		if txt_datablock == -1:
			return bpy.data.texts.new( tdb )
		return bpy.data.texts[tdb]

	def wf_fix_materials( self, context):
		'''tries to fix material names based on ogre.material files'''
		sel = bpy.context.selected_objects
		for ob in sel:
			for slot in ob.material_slots:
				mat = slot.material
				mat.name
				
				if mat.active_texture == None:
					continue

				img = mat.active_texture
				image_path = mat.active_texture.image.filepath #= 'asdfsadf' manipulate the file path
				
				#image_names_list = self.get_ogre_mat_name( image_path )
				image_names_list = [itm for itm in self.get_ogre_mat_name( image_path ) if itm[-12:] != 'shadowcaster']
				if image_names_list != []:
					if len(image_names_list) > 1:
						self.write_to_text_datablock( image_names_list )
					else:
						mat.name = image_names_list[0]
						
				image_type = (bpy.path.display_name( image_path )).lower()
				asset_name = self.get_base_name( image_path )
				image_name = '_'.join( [asset_name, image_type] )

				mat.active_texture.name = image_name
				mat.active_texture.image.name = image_name
							
				if self.DEBUG == True:
					print( image_path )
					print( image_type )
					print( asset_name )
					print( image_name )
					print( image_names_list )

def get_directory_intersection( intersection_string, directory = None ):
	if directory ==  None:
		directory = bpy.data.filepath

	tkn = os.path.abspath( directory ).split(os.sep)
	intersect = None
	if intersection_string in tkn:
		intersect = tkn.index( intersection_string )
	return intersect

def get_humanoid_skeleton_relative_path ( ):
	r'''gets the relative path to the humanoid skeleton '''
	blender_path = bpy.data.filepath

	tkn = os.path.abspath( blender_path ).split(os.sep)

	intersect_source = get_directory_intersection('source' )
	model_dir =  (os.sep).join( tkn[0:intersect_source] + ['model'])

	intersect_biped = get_directory_intersection('biped' )
	skeleton_dir = ( (os.sep).join( tkn[0:intersect_biped + 1] + ['animations/humanoid'])  )
	
	model_dir =  os.path.abspath( model_dir )
	skeleton_dir = os.path.abspath( skeleton_dir ) 

	relative_path = os.path.relpath(skeleton_dir, model_dir )
	relative_path = (relative_path).replace('\\', '/')
	return relative_path

def convert_ogre_xml(path):
	command = r'D:\\worldforge\\resources\\asset_manager\\bin\\OgreCommandLineTools_1.7.2\\OgreXMLConverter.exe '
	print (command + path)
	os.system(command + path)
	# os.system('OgreXmlConverter.exe -t -q ' + path)

def get_tmp_dir (root_path):
	'''make a temp path based on given directory'''
	tmp_dir = (os.sep).join([root_path, 'tmp'])
	if not os.path.exists(tmp_dir):
		return os.mkdir(tmp_dir)
	return tmp_dir

def adjust_ogre_xml_skeleton(ogre_xml_file, skeleton_name = None ):
	'''adjusts the name of the skeleton name of a given ogre_xml_file'''
	if os.path.exists(ogre_xml_file):
		f = open(ogre_xml_file, 'r')
		lines = f.readlines()
		f.close()

		with open(ogre_xml_file, 'w') as f:
			for line in lines:
				if (line.strip())[0:5] == '<skel':
					tks = line.split('=')
					fixed_skeleton_line =  ('%s=\'%s.skeleton\'/>\n' % (tks[0], skeleton_name))
					f.write(fixed_skeleton_line)
				else:
					f.write(line)
			f.close()

def get_wf_export_path( animated = False ):
	'''Figures out where export xml files to'''
	blender_path = bpy.data.filepath
	tkn = blender_path.split(os.sep)
	intersect = -1 
	if 'source' in tkn:
		intersect = tkn.index('source')

	xmlName = (tkn[-1].split('.')[0]) + '.mesh.xml'
	tkn = tkn[0:intersect]
	tkn.append('model')
	if animated == True:
		tkn.append( 'tmp' )
	root_path = (os.sep).join(tkn)
	ogre_xml_path = os.path.join(root_path, xmlName)
	return  root_path, ogre_xml_path  

def convert_ogre_xmls_to_mesh(root_dir):
	'''converts all xml files in the directory'''
	ll = os.listdir(root_dir)
	for dd in ll:
		if dd.endswith('.xml'):
			xml_file = os.path.abspath(os.path.join(root_dir, dd))
			mesh_file = ( xml_file[:-4] )
			if os.path.isfile(mesh_file):
				os.remove(mesh_file)

			convert_ogre_xml(xml_file)
			os.remove(xml_file)
	
def wf_export_ogre(ogre_xml_path, animation = False):
	'''Ogre Exporter'''
	bpy.ops.ogre.export(
		EX_COPY_SHADER_PROGRAMS     =False, 
		EX_SWAP_AXIS                ='xz-y', 
		EX_SEP_MATS                 =False, 
		EX_ONLY_DEFORMABLE_BONES    =False, 
		EX_ONLY_ANIMATED_BONES      =False, 
		EX_SCENE                    =False, 
		EX_SELONLY                  =True, 
		EX_FORCE_CAMERA             =False, 
		EX_FORCE_LAMPS              =False, 
		EX_MESH                     =True, 
		EX_MESH_OVERWRITE           =True, 
		EX_ARM_ANIM                 =animation, 
		EX_SHAPE_ANIM               =animation, 
		EX_INDEPENDENT_ANIM         =animation, 
		EX_TRIM_BONE_WEIGHTS        =0.01, 
		EX_ARRAY                    =True, 
		EX_MATERIALS                =False, 
		EX_FORCE_IMAGE_FORMAT       ='NONE', 
		EX_DDS_MIPS                 =1, 
		EX_lodLevels                =0, 
		EX_lodDistance              =300, 
		EX_lodPercent               =40, 
		EX_nuextremityPoints        =0, 
		EX_generateEdgeLists        =False, 
		EX_generateTangents         =True, 
		EX_tangentSemantic          ='uvw', 
		EX_tangentUseParity         =4, 
		EX_tangentSplitMirrored     =False, 
		EX_tangentSplitRotated      =False, 
		EX_reorganiseBuffers        =False, 
		EX_optimiseAnimations       =False, 
		filepath=ogre_xml_path)

def xml_skeleton_shuffle (tmp_dir, skeleton_name):
	'''renames the skeleton link with a given string'''
	
	if skeleton_name == 'humanoid':
		skeleton_name = get_humanoid_skeleton_relative_path()
		print (skeleton_name)

	# renamed_skeleton_xml = os.path.join(tmp_dir, ('%s.skeleton.xml' % skeleton_name) )

	for fl in os.listdir(tmp_dir):
		xml_file = os.path.join(tmp_dir, fl)

		# if xml_file[-12:] == 'skeleton.xml':
			#cleanup the skeleton files in the directory
			
			# if not os.path.exists(renamed_skeleton_xml):
			# 	shutil.move(xml_file, renamed_skeleton_xml)
			# else:
			# 	os.remove(xml_file)

		if xml_file[-8:] == 'mesh.xml':
			#adjust the mesh files to point to the skeleton name
			adjust_ogre_xml_skeleton(xml_file, skeleton_name )

def clean_tmp_dir( tmp_dir,root_path ):
	'''Clean up the temp directory'''
	#print root_path
	for fl in os.listdir(tmp_dir):
		src = os.path.join(tmp_dir, fl)
		dst = os.path.join(root_path, fl)
		if fl[-8:] == 'skeleton' or fl[-4:] == 'mesh':
			if os.path.exists(dst):
				os.remove(dst)
			shutil.move(src, dst)
		else:
			os.remove(src)
	shutil.rmtree(tmp_dir)

def export_ogre_static (self, context, convert = True):
	'''Main exporter for static content'''
	root_path, ogre_xml_path  = get_wf_export_path()
	
	wf_export_ogre(ogre_xml_path)
	if convert == True:
		convert_ogre_xmls_to_mesh(root_path)

def export_ogre_animated (self, context, convert = True):
	'''Main exporter for animated content'''
	skeleton_name = bpy.data.scenes['Scene'].Rig
	
	if skeleton_name == '':
		print('No skeleton file selected')
		return {'FINISHED'}
		
	root_path, ogre_xml_path  = get_wf_export_path(True)
	print (root_path)
	print (ogre_xml_path)
	wf_export_ogre(ogre_xml_path, True)
	xml_skeleton_shuffle (root_path, skeleton_name)
	convert_ogre_xmls_to_mesh(root_path)
	clean_tmp_dir(root_path, root_path[:-4])


# ----------------------------------------------------------------------------
# -------------------------- COMMAND EXEC ------------------------------------
# ----------------------------------------------------------------------------
class OBJECT_OT_wfoe_animated(Operator, AddObjectHelper):
	'''export animated ogre file'''
	bl_idname = 'mesh.wf_export_ogre_animated'
	bl_label = 'Export Ogre Animated'
	bl_category = 'WorldForge'
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		export_ogre_animated(self, context, True)
		return {'FINISHED'}

class OBJECT_OT_wfoe_static(Operator, AddObjectHelper):
	'''export static ogre file'''
	bl_idname = 'mesh.wf_export_ogre_static'
	bl_label = 'Export Ogre Static'
	bl_category = 'WorldForge'
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		export_ogre_static(self, context, True)
		return {'FINISHED'}

class OBJECT_OT_wf_fix_materials(Operator, AddObjectHelper):
	'''Gets meshes ready for woldforge export'''
	bl_idname = 'mesh.wf_fix_materials'
	bl_label = 'WF Mat Fixer'
	bl_category = 'WorldForge'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj is not None

	def execute(self, context):
		OMM = OgreMaterialManager()
		OMM.wf_fix_materials(context)
		return {'FINISHED'}

class OBJECT_OT_wf_open_ogre_materials(Operator, AddObjectHelper):
	'''open ogre materials based on the texture filename '''
	bl_idname = 'scene.wf_open_ogre_materials'
	bl_label = 'WF Open Ogre Materials'
	bl_category = 'WorldForge'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj is not None

	def execute(self, context):
		OMM = OgreMaterialManager()
		OMM.DEBUG = False
		OMM.open_ogre_materials(context)
		return {'FINISHED'}

class OBJECT_OT_clean_vertex_groups(Operator, AddObjectHelper):
	'''Cleans vertex groups on select objects base on current armatures deformable bones'''
	bl_idname = 'object.clean_vertex_groups'
	bl_label = 'Clean Vertex Groups'
	bl_category = 'WorldForge'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj is not None

	def execute(self, context):
		RAU = RigAnimationUtilities()
		RAU.DEBUG = True
		RAU.clean_vertex_groups(context)
		return {'FINISHED'}

class OBJECT_OT_wf_rename_objects( Operator):
    """Renames multiple objects names and the data names to a supplied string"""
    bl_idname = "object.wf_rename_objects"
    bl_label = "Rename Object"
    bl_options = {'REGISTER', 'UNDO'} 

    

    @classmethod
    def poll(cls, context):
        return context.selected_objects != None

    def execute(self, context):
        print ('renaming objects')
        ll = ['|',' ','.',':','\'','\"','\\', '@','#','$','%','^',';']

        arr = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o',]
        obs = context.selected_editable_objects
        print(obs)
        if context.scene.wf_rename_panel != '':
            new_name = context.scene.wf_rename_panel
            for i in new_name:
                if i in ll:
                    new_name.replace (i,'_')

            new_name = new_name.lower()
            new_name = new_name.replace (' ', '_')
            print (new_name)
            if len(obs) > 1:
                for zz in range(0, len(obs)):
                    ob = obs[zz]
                    ob.name = new_name + ('_%s' % arr[zz])
                    ob.data.name = new_name + ('_%s' % arr[zz])
            else:
                ob = obs[0]
                ob.name = new_name
                ob.data.name = new_name
        
        return {'FINISHED'}

class OBJECT_OT_wf_pivot_to_selected( Operator ):
    """Pivot to Selection"""
    bl_idname = "object.wf_pivot_to_selected"
    bl_label = "Pivot To Selected"
    bl_options = {'REGISTER', 'UNDO'}
 
    # @classmethod
    # def poll(cls, context):
    #     obj = context.active_object
    #     return obj is not None and obj.mode == 'EDIT'
 
    def execute(self, context):
        obj = context.active_object
        if obj.mode =='EDIT':
            saved_location = bpy.context.scene.cursor_location.copy()
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  
            bpy.context.scene.cursor_location = saved_location
            bpy.ops.object.mode_set(mode = 'EDIT')

        if obj.mode == 'OBJECT':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        return {'FINISHED'}
# ----------------------------------------------------------------------------
# ------------------------ BUTTON MAPPING ------------------------------------
# ----------------------------------------------------------------------------
def wfoe_static_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.mesh.wf_export_ogre_static', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def wfoe_animated_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.mesh.wf_export_ogre_animated', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def wf_fix_materials_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.mesh.wf_fix_materials', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def wf_open_ogre_materials_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.scene.wf_open_ogre_materials', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def clean_vertex_groups_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.object.clean_vertex_groups', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def wf_rename_objects_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.object.wf_rename_objects', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

def wf_pivot_to_selected_manual_map():
	url_manual_prefix = 'http://wiki.blender.org/index.php/Doc:2.6/Manual/'
	url_manual_mapping = (('bpy.ops.object.wf_pivot_to_selected', 'Modeling/Objects'), )
	return url_manual_prefix, url_manual_mapping

# ----------------------------------------------------------------------------
# --------------------------- REGISRATION ------------------------------------
# ----------------------------------------------------------------------------
def register():
	bpy.types.Scene.wf_rename_panel = bpy.props.StringProperty(name="", description = "Rename objects with this string") 

	bpy.utils.register_class(OBJECT_OT_wfoe_static)
	bpy.utils.register_manual_map(wfoe_static_manual_map)

	bpy.utils.register_class(OBJECT_OT_wfoe_animated)
	bpy.utils.register_manual_map(wfoe_animated_manual_map)

	bpy.utils.register_class(OBJECT_OT_wf_fix_materials)
	bpy.utils.register_manual_map(wf_fix_materials_manual_map)

	bpy.utils.register_class(OBJECT_OT_wf_open_ogre_materials)
	bpy.utils.register_manual_map(wf_open_ogre_materials_manual_map)

	bpy.utils.register_class(OBJECT_OT_clean_vertex_groups)
	bpy.utils.register_manual_map(clean_vertex_groups_manual_map)
	
	bpy.utils.register_class(OBJECT_OT_wf_rename_objects)
	bpy.utils.register_manual_map(wf_rename_objects_manual_map)
	
	bpy.utils.register_class(OBJECT_OT_wf_pivot_to_selected)
	bpy.utils.register_manual_map(wf_pivot_to_selected_manual_map)

def unregister():
	del bpy.types.Scene.rename_panel

	bpy.utils.unregister_class(OBJECT_OT_wfoe_static)
	bpy.utils.unregister_manual_map(wfoe_static_manual_map)

	bpy.utils.unregister_class(OBJECT_OT_wfoe_animated)
	bpy.utils.unregister_manual_map(wfoe_animated_manual_map)

	bpy.utils.unregister_class(OBJECT_OT_wf_fix_materials)
	bpy.utils.unregister_manual_map(wf_fix_materials_manual_map)

	bpy.utils.unregister_class(OBJECT_OT_wf_open_ogre_materials)
	bpy.utils.unregister_manual_map(wf_open_ogre_materials_manual_map)

	bpy.utils.unregister_class(OBJECT_OT_clean_vertex_groups)
	bpy.utils.unregister_manual_map(clean_vertex_groups_manual_map)

	bpy.utils.unregister_class(OBJECT_OT_wf_rename_objects)
	bpy.utils.unregister_manual_map(wf_rename_objects_manual_map)
	
	bpy.utils.unregister_class(OBJECT_OT_wf_pivot_to_selected)
	bpy.utils.unregister_manual_map(wf_pivot_to_selected-manual_map)

if __name__ == '__main__':
	register()



'''
ob = bpy.context.active_object

def clean_vertex_groups( ob ):
	vertex_groups = ob.vertex_groups
	rig = ob.modifiers[-1].object # get the rig
	bones = rig.data.bones
	#get data
	vgrp_list = [grp.name for grp in ob.vertex_groups]
	bone_list = [bone.name for bone in rig.data.bones if bone.use_deform ]

	#compare lists 
	del_group = [itm for itm in vgrp_list if itm not in bone_list]
	mkv_groups = [itm for itm in bone_list if itm not in vgrp_list]

	#add vertex groups based on armatures deformable bones
	[ob.vertex_groups.new(name) for name in mkv_groups] 

	# remove groups that are not part of the current armatures deformable bones
	# list comprehension code may be a bit too long
	[ob.vertex_groups.remove( ob.vertex_groups[ ob.vertex_groups.find( group ) ] ) for group in del_group]
		
clean_vertex_groups( ob )    
'''






