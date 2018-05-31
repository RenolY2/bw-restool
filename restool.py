
import gzip
import os 
import json

from lib.bw_archive import BWArchive

def read_bwres(filepath):
    if filepath.endswith(".gz"):
        with gzip.open(filepath, "rb") as f:
            bwres = BWArchive(f)
    else:
        with open(filepath, "rb") as f:
            bwres = BWArchive(f)
    
    return bwres
    
def write_bwres(filepath, bwres):
    if filepath.endswith(".gz"):
        with gzip.open(filepath, "rb") as f:
            bwres.write(f)
    else:
        with open(filepath, "r") as f:
            bwres.write(f)



def dump_res_to_folder(inputpath, outputfolder):
    bwarc = read_bwres(inputpath)
    archeader = bwarc.entries[0]
    filename = str(archeader.filename, encoding="ascii")
    print("making", filename)

    os.makedirs(outputfolder, exist_ok=True)

    TEXTUREFOLDER = os.path.join(outputfolder, "Textures")
    SOUNDFOLDER = os.path.join(outputfolder, "Sounds")
    MODELFOLDER = os.path.join(outputfolder, "Models")
    ANIMFOLDER = os.path.join(outputfolder, "Animations")
    EFFECTS = os.path.join(outputfolder, "SpecialEffects")
    SCRIPTS = os.path.join(outputfolder, "Scripts")
    print(bwarc.is_bw())
    game = "Battalion Wars" if bwarc.is_bw() else "Battalion Wars 2"

    data = {"Game": game,
            "Level name": filename}



    with open(os.path.join(outputfolder, "resinfo.txt"), "w") as f:
        json.dump(data, f, indent=" "*4)
        


    for folder in ( TEXTUREFOLDER, SOUNDFOLDER, MODELFOLDER,
                    ANIMFOLDER, EFFECTS, SCRIPTS):
        os.makedirs(folder, exist_ok=True)
        
    print("Created directory structure")

    for script in bwarc.scripts:
        filename = str(script.res_name, encoding="ascii") + ".luap"
        with open(os.path.join(SCRIPTS, filename), "wb") as f:
            f.write(script.script_data)

    print("Dumped scripts")
            
    for animation in bwarc.animations:
        filename = str(animation.res_name, encoding="ascii") + ".anim"
        with open(os.path.join(ANIMFOLDER, filename), "wb") as f:
            f.write(animation.animation_data)

    print("Dumped animations")
            
    for effect in bwarc.effects:
        filename = str(effect.res_name, encoding="ascii") + ".txt"
        with open(os.path.join(EFFECTS, filename), "wb") as f:
            f.write(effect.particle_data)

    print("Dumped effects")
            
    for (soundname, sounddata) in bwarc.sounds:
        filename = str(soundname.res_name, encoding="ascii").strip("\x00") + ".adp"
        with open(os.path.join(SOUNDFOLDER, filename), "wb") as f:
            f.write(sounddata.data)

    print("Dumped sounds")

    texturenames = []

    used_textures = {}

    for tex in bwarc.textures:
        texturenames.append((bytes(tex.res_name).strip(b"\x00"), tex))

    for model in bwarc.models:
        modelname = str(model.res_name, encoding="ascii") 
        modeldata = bytes(model.entries[0].data)
        
        modelfolder = os.path.join(MODELFOLDER, modelname)
        
        filename = modelname+".modl"
        os.makedirs(modelfolder, exist_ok=True)
        with open(os.path.join(modelfolder, filename), "wb") as f:
            f.write(modeldata)
        
        textures = []
        print("searching textures for", filename)
        for name, tex in texturenames:
            if modeldata.find(name) != -1:
                textures.append(tex)
                
        print("found", textures)
        
        for tex in textures:
            texturename = str(tex.res_name, encoding="ascii").strip("\x00")
            texfilename = texturename+".tex"
            
            if texturename not in used_textures:
                used_textures[texturename] = True 
            
            with open(os.path.join(modelfolder, texfilename), "wb") as f:
                f.write(tex.data)
    print("Dumped models and their textures")
    for tex in bwarc.textures:
        texname = str(tex.res_name, encoding="ascii").strip("\x00")
        
        if texname not in used_textures:
            filename = texname+".tex"
            with open(os.path.join(TEXTUREFOLDER, filename), "wb") as f:
                f.write(tex.data)
                
    print("Dumped all remaining textures")

    print("Done!")

def choose_open_func(path):
    if path.endswith(".gz"):
        return gzip.open 
    else:
        return open 
    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help="Path to folder, .res or .res.gz file.")
    parser.add_argument("output", default=None, nargs = '?',
                        help=(
                            "If input is a folder, write packed data into output file. "
                            "If output ends with .gz, output file will be compressed with gzip."
                            "If input is a .res or .res.gz file, write extracted data into output folder."
                            
                        ))

    args = parser.parse_args()
    
    input_path = args.input
    output = args.output
    
    if os.path.isfile(input_path):
        # extract res file to folder 
        if output is None:
            output = input_path + "_Folder"
        
        dump_res_to_folder(input_path, output)
    
    else:
        # pack folder into res file 
        
        textures = []
        models = []
        sounds = []
        animations = []
        effects = []
        scripts = []
        
        #for         
                
        
        #input_res = "SP_5.4_Level.res.gz"
        #folder_out = input_res+"_Folder"
        
        
        

    
    