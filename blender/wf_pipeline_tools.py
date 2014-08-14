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

class OgreMaterialManager:
    '''Worldforge material management utilites'''
    def __init__(self):
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

def convertXMLToMesh(path):
    os.system('OgreXmlConverter.exe -t -q ' + path)

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
            convertXMLToMesh(os.path.abspath(os.path.join(root_dir, dd)))
    
def wf_export_ogre(ogreXmlPath, animation = False):
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
        filepath=ogreXmlPath)

def xml_skeleton_shuffle (tmp_dir, skeleton_name):
	'''renames the skeleton link with a given string'''
	renamed_skeleton_xml = os.path.join(tmp_dir, ('%s.skeleton.xml' % skeleton_name) )

	for fl in os.listdir(tmp_dir):
		xml_file = os.path.join(tmp_dir, fl)

		if xml_file[-12:] == 'skeleton.xml':
			#cleanup the skeleton files in the directory
			
			if not os.path.exists(renamed_skeleton_xml):
				shutil.move(xml_file, renamed_skeleton_xml)
			else:
				os.remove(xml_file)

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
        
    else:
        root_path, ogre_xml_path  = get_wf_export_path(True)
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
    url_manual_mapping = (('bpy.ops.mesh.wf_export_ogre_animated', 'Modeling/Objects'), )
    return url_manual_prefix, url_manual_mapping

# ----------------------------------------------------------------------------
# --------------------------- REGISRATION ------------------------------------
# ----------------------------------------------------------------------------
def register():
    bpy.utils.register_class(OBJECT_OT_wfoe_static)
    bpy.utils.register_manual_map(wfoe_static_manual_map)

    bpy.utils.register_class(OBJECT_OT_wfoe_animated)
    bpy.utils.register_manual_map(wfoe_animated_manual_map)

    bpy.utils.register_class(OBJECT_OT_wf_fix_materials)
    bpy.utils.register_manual_map(wf_fix_materials_manual_map)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_wfoe_static)
    bpy.utils.unregister_manual_map(wfoe_static_manual_map)

    bpy.utils.unregister_class(OBJECT_OT_wfoe_animated)
    bpy.utils.unregister_manual_map(wfoe_animated_manual_map)

    bpy.utils.unregister_class(OBJECT_OT_wf_fix_materials)
    bpy.utils.unregister_manual_map(wf_fix_materials_manual_map)


if __name__ == '__main__':
    register()





