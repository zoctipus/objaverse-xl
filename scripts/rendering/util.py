import bpy

NONE_HEIGHLIGHT_COLOR = (0.8 , 0.8 , 0.8 , 0.3)
HIGHLIGHT_COLOR = (0.6 , 0.6 , 0.0 , 0.7)

def set_all_transparent(alpha_value=0.1):
    for m in bpy.data.materials:
        # Check if the material has a node tree
        if m.use_nodes and m.node_tree:
            # Get the Principled BSDF node
            bsdf = next((node for node in m.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                # Set the Alpha value
                bsdf.inputs['Alpha'].default_value = NONE_HEIGHLIGHT_COLOR[3]
                
                # Find the material output node
                material_output = next((node for node in m.node_tree.nodes if node.type == 'OUTPUT_MATERIAL'), None)
                if material_output:
                    # Set the blend method for Eevee
                    m.blend_method = 'BLEND'
                    # Optionally, adjust the settings for shadows as needed
                    # m.shadow_method = 'HASHED' or 'CLIP

def remove_all_materials_from_all_objects_and_data():
    # Iterate through all objects in the scene
    for obj in bpy.data.objects:
        # Clear materials from the object
        if obj.type == 'MESH':
            obj.data.materials.clear()

    # Remove unused materials from Blender's data block
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)


def assign_material_and_set_alpha_to_all_objects(material_name, alpha_value = NONE_HEIGHLIGHT_COLOR[3]):
    # Create or get the existing material
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        if not mat.node_tree.nodes.get('Principled BSDF'):
            mat.node_tree.nodes.clear()
            bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            mat_output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            mat.node_tree.links.new(bsdf.outputs['BSDF'], mat_output.inputs['Surface'])
    
    # Set the material's alpha value and blend method
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Alpha'].default_value = alpha_value
    mat.blend_method = 'BLEND'
    
    # Iterate through all objects and assign the material
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)


def assign_highlight_material_without_delete(obj, name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        # Create material
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if not bsdf:
            # If the material does not have a Principled BSDF node, create one
            mat.node_tree.nodes.clear()
            bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        # bsdf.inputs['Base Color'].default_value = HIGHLIGHT_COLOR[0:3] + (1.0,)  # RGB + fully opaque for base color
        bsdf.inputs['Alpha'].default_value = HIGHLIGHT_COLOR[3]  # Set alpha
        mat.blend_method = 'BLEND'  # Set blend method for transparency

        # Link BSDF to material output
        mat_output = mat.node_tree.nodes.get('Material Output')
        if not mat_output:
            mat_output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], mat_output.inputs['Surface'])

    # Assign it to object
    if obj.data.materials:
        # Assign to 1st material slot, keeping the previous material
        temp_mat = obj.data.materials[0]
        obj.data.materials[0] = mat
        if temp_mat != mat:
            obj.data.materials.append(temp_mat)
    else:
        # No slots
        obj.data.materials.append(mat)

def assign_highlight_material(obj, highlight_material_name, base_color = HIGHLIGHT_COLOR[0:3] + (1.0,), alpha_value = HIGHLIGHT_COLOR[3]):
    # Create or get the highlight material
    highlight_mat = bpy.data.materials.get(highlight_material_name)
    if not highlight_mat:
        highlight_mat = bpy.data.materials.new(name=highlight_material_name)
        highlight_mat.use_nodes = True
        bsdf = highlight_mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        mat_output = highlight_mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        highlight_mat.node_tree.links.new(bsdf.outputs['BSDF'], mat_output.inputs['Surface'])
    
    # Set highlight material properties
    bsdf.inputs['Base Color'].default_value = base_color + (1,)  # Add full alpha for base color display
    bsdf.inputs['Alpha'].default_value = alpha_value
    highlight_mat.blend_method = 'BLEND'
    
    # Disable or delete the object's default material
    obj.data.materials.clear()

    # Assign the highlight material to the object
    obj.data.materials.append(highlight_mat)

def remove_material_from_obj(obj, name):
    # This function searches for a material by name and removes it
    for i, mat in enumerate(obj.data.materials):
        if mat.name == name:
            obj.data.materials.pop(index=i)
            break

def remove_material_from_data(material_name):
    material = bpy.data.materials.get(material_name)
    if material:
        # Ensure the material is not used by any other objects
        if material.users == 0:
            bpy.data.materials.remove(material)
        else:
            print(f"Material '{material_name}' is still in use by other objects and cannot be removed from data.")

def reassign_existing_material(obj, material_name):
    # Get the existing material by name
    existing_mat = bpy.data.materials.get(material_name)
    if existing_mat:
        # Clear any current materials
        obj.data.materials.clear()
        # Reassign the existing material
        obj.data.materials.append(existing_mat)
    else:
        print(f"Material '{material_name}' not found.")
