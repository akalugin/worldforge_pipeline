bl_info = {
    "name": "Tools Panel",
    "category": "WorldForge",
    "author": "a.kalugin"
    } 
    
import bpy

bpy.types.Scene.Current_Rig = bpy.props.StringProperty()

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
        
 
        
        #row.prop(None, "")
        #row.prop(obj, "name")
        #row = layout.row()
        #row.label(text="Active object is: " + obj.name)
        
        
        #obj = context.object
        #layout = self.layout
        #row = layout.row()
        #row.template_list(obj, "myCollection", obj, "myCollection_index")

        
        #dummy_object1 = bpy.data.objects[0]
        #col = layout.column()
        #col.prop(dummy_object1, "parent")
        #row.label(text="Active object is: " + obj.name)

        
def register():
    bpy.utils.register_class(CustomPanel)

def unregister():
    bpy.utils.unregister_class(CustomPanel)

if __name__ == "__main__":
    register()


