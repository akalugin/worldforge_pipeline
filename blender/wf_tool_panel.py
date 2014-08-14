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

class CustomPanel(bpy.types.Panel):
    """Worldforge Tools Panel"""
    bl_label = "WorldForge Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "WorldForge"
    # bl_context = "objectmode"
    bl_label = "WorldForge"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        scn = context.scene
        
        obj = get_armature ('wf_armature')
        
        layout.label(text="OGRE Object Exporter")
        row = layout.row()
        row.operator("mesh.wf_export_ogre_static")
        
        layout.separator()
        layout.separator()
        layout.label(text="OGRE Animation Exporter")

        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")
        col = layout.column() 
        #col.label('Choose a Rig For Export')
        col.prop_search(scene, "Rig", bpy.data, "armatures")
        row = layout.row()
        row.operator("mesh.wf_export_ogre_animated")
        
        row = layout.row()
        layout.label(text="Weight Utilities")
        row = layout.row()
        row.operator('object.vertex_group_limit_total', text= 'Limit Weights')
        
        row = layout.row()
        layout.label(text="Material Utilities")
        row = layout.row()
        row.operator('mesh.wf_fix_materials', text= 'Fix Materials')
        
def register():
    bpy.utils.register_class(CustomPanel)

def unregister():
    bpy.utils.unregister_class(CustomPanel)

if __name__ == "__main__":
    register()



