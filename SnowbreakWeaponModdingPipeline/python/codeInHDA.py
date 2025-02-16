import os
import json
from PIL import Image
import numpy as np
import shutil

node = None

def open_folder(path):
    if os.path.exists(path):
        os.startfile(path)
    else:
        print("[Open Folder] Cannot find folder: " + path)

def convert_path(path):
    # split path
    path_components = os.path.normpath(path).split(os.sep)
    # convert to houdini path
    houdini_path = "/".join(path_components)
    return houdini_path

def new_node(node_type, node_name):
    global node
    old_node = hou.node("../" + node_name)
    if old_node is not None:
        old_node.destroy(True)
    return node.parent().createNode(node_type, node_name)

def get_material_from_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
        for info in config:
            if info["Type"] == "StaticMesh":
                material = info["Properties"]["StaticMaterials"][0]["MaterialSlotName"]    
    return material

def import_from_fmodel(kwargs):
    global node
    # check fmodel output directory
    node = kwargs["node"]
    fmodel_dir = node.parm("inputdir").eval()
    output_dir = node.parm("outputdir").eval()

    if not os.path.exists(fmodel_dir):
        print("[Import] Cannot find FModel Output Directory: " + fmodel_dir)
        return
    print("[Import] FModel Output Directory: " + fmodel_dir)

    if not os.path.exists(output_dir):
        print("[Import] Cannot find Output Directory: " + output_dir)
        return
    print("[Import] Output Directory: " + output_dir)


    # check model format
    files = os.listdir(fmodel_dir)
    fmt_value = node.parm("modelfmt").eval()
    fmts = [".gltf", ".glb", ".obj"]
    if fmt_value >= len(fmts):
        fmt_value = 0
    fmt = fmts[fmt_value]
    print("[Import] Model Format: " + fmt)

    # check whether mesh files exist
    mesh_files = [f for f in files if f.lower().endswith(fmt)]
    if len(mesh_files) == 0:
        print("[Import] No mesh files found")
        return    
    print("[Import] Mesh Files: " + str(mesh_files))

    # get the main mesh file
    weapon_base_name = node.parm("basename").eval()
    if (weapon_base_name + fmt) not in mesh_files:
        print("[Import] Please specify the correct base name")
        return
    print("[Import] Weapon Main Mesh: " + weapon_base_name + fmt)

    # get other mesh files
    other_mesh_files = [f for f in mesh_files if f != weapon_base_name + fmt]
    print("[Import] Other Mesh Files: " + str(other_mesh_files))

    all_mesh = [weapon_base_name + fmt] + other_mesh_files
    for index, mesh in enumerate(all_mesh):
        if index == 0:
            node_name = "Weapon_Mesh"
            # this is the main mesh
            print("[Import] Importing Main Mesh: " + mesh)
        else:
            node_name = "attach_" + str(index - 1)
            # this is the attachment mesh
            print("[Import] Importing Attachment Mesh: " + mesh)
        # create node for gltf or obj
        import_node = None
        if fmt == ".gltf" or fmt == ".glb":
            import_node = new_node("gltf", node_name)
            import_node.parm("filename").set(convert_path(os.path.join(fmodel_dir, mesh)))
        else:
            import_node = new_node("file", node_name)
            import_node.parm("file").set(convert_path(os.path.join(fmodel_dir, mesh)))

        # load config
        material = get_material_from_config(os.path.join(fmodel_dir, mesh.replace(fmt, ".json")))
        
        # set transform node
        transform_node = new_node("xform", "Transform_" + node_name)
        transform_node.setNextInput(import_node)

        # whether to delete vertex color
        delvtxcolor_node = new_node("attribdelete", "DelVtxColor_" + node_name)
        if not node.parm("vtxclr").eval():
            delvtxcolor_node.parm("ptdel").set("")
            delvtxcolor_node.parm("vtxdel").set("")
            delvtxcolor_node.parm("primdel").set("")
        else:
            delvtxcolor_node.parm("ptdel").set("Cd")
            delvtxcolor_node.parm("vtxdel").set("Cd")
            delvtxcolor_node.parm("primdel").set("Cd")
        delvtxcolor_node.setNextInput(transform_node)

        # set null node
        null_node = new_node("null", "ModifyHere_" + node_name)
        # set this node color red
        null_node.setColor(hou.Color((1, 0, 0)))        
        null_node.setNextInput(delvtxcolor_node)
        
        # set material
        material_node = new_node("attribwrangle", "Material_" + node_name)
        material_node.parm("class").set(1)
        material_node.parm("snippet").set(f's@shop_materialpath = "{material}";\ns@name = "{mesh.replace(fmt, "")}";')
        material_node.setNextInput(null_node)

        # set name node
        name_node = new_node("null", mesh.replace(fmt, ""))
        name_node.setNextInput(material_node)
        if index == 0:
            name_node.setDisplayFlag(True)
            name_node.setRenderFlag(True)

        # set output node
        rop_node = new_node("rop_fbx", node_name + "_rop")
        rop_node.parm("sopoutput").set(convert_path(os.path.join(output_dir, mesh.replace(fmt, ".fbx"))))
        rop_node.parm("exportkind").set(False)
        rop_node.parm("convertunits").set(True)
        rop_node.parm("computesmoothinggroups").set(True)
        rop_node.setNextInput(name_node)


    # layout children
    node.parent().layoutChildren()

def create_texture(kwargs):    
    global node
    # check fmodel output directory
    node = kwargs["node"]
    output_dir = node.parm("outputdir").eval()

    # check texture file
    diffuse_file = node.parm("diffuse").eval()
    normal_file = node.parm("normal").eval()
    metallic_file = node.parm("metallic").eval()
    roughness_file = node.parm("roughness").eval()
    if not os.path.exists(diffuse_file):
        print("[Texture] Cannot find Diffuse Texture: " + diffuse_file)
        return
    if not os.path.exists(normal_file):
        print("[Texture] Cannot find Normal Texture: " + normal_file)
        return
    if not os.path.exists(metallic_file):
        print("[Texture] Cannot find Metallic Texture: " + metallic_file)
        return
    if not os.path.exists(roughness_file):
        print("[Texture] Cannot find Roughness Texture: " + roughness_file)
        return
    
    # get mask channel
    rmask = node.parm("rmask").eval()
    rc = -1
    if rmask & 1:
        rc = 0
    elif rmask & 2:
        rc = 1
    elif rmask & 4:
        rc = 2
    elif rmask & 8:
        rc = 3
    mmask = node.parm("mmask").eval()
    mc = -1
    if mmask & 1:
        mc = 0
    elif mmask & 2:
        mc = 1
    elif mmask & 4:
        mc = 2
    elif mmask & 8:
        mc = 3
    print("[Texture] Metallic Mask: " + str(rc))
    print("[Texture] Roughness Mask: " + str(mc))

    # get texture name from file
    bake_name = node.parm("bakename").eval()
    if bake_name == "":
        print("[Texture] Please specify the bake name")
        return
    if bake_name.find("/") != -1:
        bake_name = bake_name.split("/")[-1]
    if bake_name.find(".") != -1:
        bake_name = bake_name.split(".")[0]
    if bake_name.endswith("_sm"):
        bake_name = bake_name[:-3]
    print("[Texture] Bake Name: " + bake_name)
    
    # create mix texture
    mimg = Image.open(metallic_file)
    img_data = np.array(mimg)
    # if only has two dimension, then it is a grayscale image
    if len(img_data.shape) == 2:
        m_data = img_data
    else:
        m_data = img_data[:,:,mc]
    rimg = Image.open(roughness_file)
    img_data = np.array(rimg)
    # if only has two dimension, then it is a grayscale image
    if len(img_data.shape) == 2:
        r_data = img_data
    else:
        r_data = img_data[:,:,rc]
    new_data = np.zeros((m_data.shape[0], m_data.shape[1], 4), dtype=np.uint8)
    new_data[:,:,0] = m_data
    new_data[:,:,1] = r_data
    new_data[:,:,2] = 0
    new_data[:,:,3] = 255
    new_img = Image.fromarray(new_data)
    new_img.save(os.path.join(output_dir, bake_name + "_r.tga"))

    # copy diffuse and normal texture
    d_ext = os.path.basename(diffuse_file).split(".")[-1]
    d_output = os.path.join(output_dir, bake_name + "_d." + d_ext)
    shutil.copyfile(diffuse_file, d_output)
    n_ext = os.path.basename(normal_file).split(".")[-1]
    n_output = os.path.join(output_dir, bake_name + "_n." + n_ext)
    shutil.copyfile(normal_file, n_output)

def open_fmodel_output_dir(kwargs):
    global node
    node = kwargs["node"]
    fmodel_dir = node.parm("inputdir").eval()
    open_folder(fmodel_dir)

def open_output_dir(kwargs):
    global node
    node = kwargs["node"]
    output_dir = node.parm("outputdir").eval()
    open_folder(output_dir)

def open_unrealpak_dir(kwargs):
    global node
    node = kwargs["node"]
    unrealpak_dir = node.parm("urlpakdir").eval()
    open_folder(unrealpak_dir)

def copy_and_pack(kwargs):
    global node
    node = kwargs["node"]
    project_dir = node.parm("projdir").eval()
    unrealpak_dir = node.parm("urlpakdir").eval()
    fmodel_dir = node.parm("inputdir").eval()

    # check project directory
    if not os.path.exists(project_dir):
        print("[Copy and Pack] Cannot find Project Directory: " + project_dir)
        return
    print("[Copy and Pack] Project Directory: " + project_dir)

    # check unrealpak directory
    if not os.path.exists(unrealpak_dir):
        print("[Copy and Pack] Cannot find UnrealPak Directory: " + unrealpak_dir)
        return
    print("[Copy and Pack] UnrealPak Directory: " + unrealpak_dir)

    # delete unused directory
    project_name = os.path.basename(project_dir)
    original_path = os.path.join(project_dir, "Saved", "Cooked", "WindowsNoEditor", project_name, "Content", "Characters", "Weapon")
    subdirectories = [f for f in os.listdir(original_path) if os.path.isdir(os.path.join(original_path, f))]
    weapon_name = os.path.basename(fmodel_dir)
    for subdirectory in subdirectories:
        if subdirectory != weapon_name:
            shutil.rmtree(os.path.join(original_path, subdirectory))
        else:
            # delete files which include "_inst"
            files = os.listdir(os.path.join(original_path, subdirectory))
            for f in files:
                if f.find("_inst") != -1:
                    os.remove(os.path.join(original_path, subdirectory, f))

    # copy files
    original_path = os.path.join(project_dir, "Saved", "Cooked", "WindowsNoEditor", project_name, "Content", "Characters")
    target_path = os.path.join(unrealpak_dir, weapon_name, "Game", "Content", "Characters")
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    shutil.copytree(original_path, target_path)

    # pack files
    unrealpak_bat = os.path.join(unrealpak_dir, "UnrealPak-With-Compression_nopause.bat")
    if not os.path.exists(unrealpak_bat):
        print("[Copy and Pack] Cannot find UnrealPak Bat: " + unrealpak_bat)
        return
    os.chdir(unrealpak_dir)
    os.system(unrealpak_bat + " " + weapon_name)

    # rename pak file
    mod_name = node.parm("modname").eval()
    if mod_name != "":
        shutil.move(os.path.join(unrealpak_dir, weapon_name + ".pak"), os.path.join(unrealpak_dir, mod_name + ".pak"))
        shutil.move(os.path.join(unrealpak_dir, weapon_name), os.path.join(unrealpak_dir, mod_name))
        weapon_name = mod_name

    # copy pak file to mod directory
    mod_dir = node.parm("moddir").eval()
    if os.path.exists(mod_dir):
        shutil.copyfile(os.path.join(unrealpak_dir, weapon_name + ".pak"), os.path.join(mod_dir, weapon_name + ".pak"))