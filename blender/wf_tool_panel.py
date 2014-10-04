bl_info = {
    "name": "Tools Panel",
    "category": "WorldForge",
    "author": "anisimkalugin.com",
    "description": "Worldforge Pipeline Panel",
    } 
    
import bpy

bpy.types.Scene.Rig = bpy.props.StringProperty()

def get_armature (name):
    '''gets the name of the current armature '''
    for ob in bpy.data.objects:
        if ob.name == name:
            return ob
    return False

class PANEL_OT_wf_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "WorldForge"
    bl_label = "Tools"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Rename Objects:")
        layout.prop(scene, "wf_rename_panel") 
        row = layout.row()
        row.operator('object.wf_rename_objects', text='Renamer', icon="FILE_TICK")
        col = layout.column(align=True)
        col.operator('object.wf_pivot_to_selected', text='', icon='FORCE_FORCE')
        row = col.row(align=True)
        row.operator("object.shade_smooth", text="Smooth")
        row.operator("object.shade_flat", text="Flat")

class PANEL_OT_wf_mat_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "WorldForge"
    bl_label = "Material Utils"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout

        row = layout.row()
        # layout.qlabel(text="Material Utilities")
        row = layout.row(align=True)
        row.operator('mesh.wf_fix_materials', text= 'Fix Materials', icon='SCULPTMODE_HLT')
        row.operator('scene.wf_open_ogre_materials', text='Ogre Mats', icon='IMASEL')
        # col = layout.column(align=True)
        row = layout.row(align=True)
        row.operator('view3d.material_to_texface',text = 'Mat to Tex', icon='MATERIAL_DATA')
        row.operator('view3d.texface_to_material',text = 'Tex to Mat', icon='FACESEL_HLT')

class PANEL_OT_wf_rigging_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "WorldForge"
    bl_label = "Rigging Utils"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.row()
        col.operator('object.vertex_group_limit_total', text= 'Limit Weights')
        col.operator('object.clean_vertex_groups', text= 'Clean Weights')

class PANEL_OT_wf_ogre_export(bpy.types.Panel):
    """Worldforge Tools Panel"""
    bl_label = "WorldForge Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "WorldForge"
    # bl_context = "objectmode"
    bl_label = "Ogre Export"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        scene = context.scene


        row = layout.row()
        row.operator("mesh.wf_export_ogre_static", icon='VIEW3D')


        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")
        col = layout.column() 
        obj = get_armature ('wf_armature')
        
        col.prop_search(scene, "Rig", bpy.data, "armatures")
        row = layout.row()
        row.operator("mesh.wf_export_ogre_animated", icon='BONE_DATA')


def register():
    bpy.utils.register_class(PANEL_OT_wf_ogre_export)
    bpy.utils.register_class(PANEL_OT_wf_mat_panel)
    bpy.utils.register_class(PANEL_OT_wf_rigging_panel)
    bpy.utils.register_class(PANEL_OT_wf_tools)

def unregister():
    bpy.utils.unregister_class(PANEL_OT_wf_ogre_export)
    bpy.utils.unregister_class(PANEL_OT_wf_mat_panel)
    bpy.utils.unregister_class(PANEL_OT_wf_rigging_panel)
    bpy.utils.unregister_class(PANEL_OT_wf_tools)

if __name__ == "__main__":
    register()



