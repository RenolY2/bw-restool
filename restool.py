
import gzip
import os 
import json

from io import BytesIO

from lib.bw_archive import BWArchive
from lib.bw_archive_base import BWResourceFromData
from lib.helper import write_uint32

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
    
    game = "Battalion Wars" if bwarc.is_bw() else "Battalion Wars 2"
    print("Archive detected as", game)

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
            texfilename = texturename+".texture"
            
            if texturename not in used_textures:
                used_textures[texturename] = True 
            
            with open(os.path.join(modelfolder, texfilename), "wb") as f:
                f.write(tex.data)
                
    print("Dumped models and their textures")
    for tex in bwarc.textures:
        texname = str(tex.res_name, encoding="ascii").strip("\x00")
        
        if texname not in used_textures:
            filename = texname+".texture"
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
    import itertools
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
        
        textures_already_added = {}
        
        with open(os.path.join(input_path, "resinfo.txt"), "rb") as f:
            resinfo = json.load(f)
            
        is_bw2 = resinfo["Game"] == "Battalion Wars 2"
        compress = False 
        if output is None:
            if input_path.endswith("_Folder"):
                output = input_path[0:-7]
            else:
                if is_bw2:
                    output = input_path + ".res.gz"
                else:
                    output = input_path + ".res"
                    
            if is_bw2:
                compress = True 
                
        
        if output.endswith(".gz"):
            compress = True
            
        print("Searching path", input_path, "for files to pack into the resource archive")
        for dirpath, dirnames, filenames in os.walk(input_path):
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                filename_noextension = filename[0:filename.rfind(".")]
                                
                # Textures 
                if filename.endswith(".texture"):
                    if filename_noextension not in textures_already_added:
                        textures_already_added[filename_noextension] = True
                        data = BytesIO()
                        
                        with open(fullpath, "rb") as f:
                            data.write(f.read())
                        
                        if is_bw2:
                            resource = BWResourceFromData(b"DXTG", data)
                        else:
                            resource = BWResourceFromData(b"TXET", data)
                        
                        
                        textures.append(resource)
                
                # Models
                elif filename.endswith(".modl"):
                    data = BytesIO()
                    write_uint32(data, len(filename_noextension))
                    data.write(bytes(filename_noextension, encoding="ascii"))
                    
                    with open(fullpath, "rb") as f:
                        modeldata = f.read()
                    
                    # Model data is embedded inside another LDOM section
                    data.write(b"LDOM")
                    write_uint32(data, len(modeldata))
                    data.write(modeldata)
                    
                    resource = BWResourceFromData(b"LDOM", data)
                    
                    models.append(resource)
                
                # Sounds 
                elif filename.endswith(".adp"):
                    # Write sound data 
                    data = BytesIO()
                    
                    with open(fullpath, "rb") as f:
                        data.write(f.read())
                    
                    resource = BWResourceFromData(b"DPSD", data)
                    
                    # Write sound header
                    assert len(filename_noextension) <= 32
                    
                    data = BytesIO()
                    data.write(bytes(filename_noextension, encoding="ascii"))
                    data.write(b"\x00"*(32-len(filename_noextension)))
                    
                    soundheader = BWResourceFromData(b"HPSD", data)
                    sounds.append(soundheader)
                    sounds.append(resource)
                
                # Animations 
                elif filename.endswith(".anim"):
                    data = BytesIO()
                    write_uint32(data, len(filename_noextension))
                    data.write(bytes(filename_noextension, encoding="ascii"))
                    
                    with open(fullpath, "rb") as f:
                        data.write(f.read())
                    
                    resource = BWResourceFromData(b"MINA", data)
                    animations.append(resource)
                    
                # Special effects 
                elif filename.endswith(".txt") and filename != "resinfo.txt":
                    data = BytesIO()
                    write_uint32(data, len(filename_noextension))
                    data.write(bytes(filename_noextension, encoding="ascii"))
                    
                    with open(fullpath, "rb") as f:
                        data.write(f.read())
                    
                    resource = BWResourceFromData(b"FEQT", data)
                    effects.append(resource)
                
                # Scripts 
                elif filename.endswith(".luap"):
                    data = BytesIO()
                    write_uint32(data, len(filename_noextension))
                    data.write(bytes(filename_noextension, encoding="ascii"))
                    
                    with open(fullpath, "rb") as f:
                        data.write(f.read())
                    
                    resource = BWResourceFromData(b"PRCS", data)
                    scripts.append(resource)
                
        print("Done searching.")
        print("{0} textures\n{1} models\n{2} sounds\n{3} animations\n{4} effects\n{5} scripts".format(
            len(textures), len(models), len(sounds)//2, len(animations), len(effects), len(scripts)
        ))
        
        if compress:
            # BW2 archives are gzip compressed and always end with .gz 
            bwopen = gzip.open
        else:
            bwopen = open 
            
        print("Writing to", output)
        
        f = BytesIO()
        
        #with bwopen(output, "wb") as f:
        if True:
            f.write(b"RXET")
            fxet_size_offset = f.tell()
            f.write(b"ABCD")
            write_uint32(f, len(resinfo["Level name"]))
            f.write(bytes(resinfo["Level name"], encoding="ascii"))
            
            if is_bw2:
                f.write(b"FTBG")
            else:
                f.write(b"FTBX")
                
            texsection_size_offset = f.tell()
            f.write(b"BACD")
            write_uint32(f, len(textures))
            
            for texdata in textures:
                #f.write(texdata.data)
                texdata.write(f)
            texdata_end = f.tell()
            
            texsection_size = texdata_end - texsection_size_offset - 4
            
            fxet_size = texdata_end - fxet_size_offset - 4
            
            f.seek(fxet_size_offset)
            write_uint32(f, fxet_size)
            
            f.seek(texsection_size_offset)
            write_uint32(f, texsection_size)
            
            f.seek(texdata_end)
            
            f.write(b"DNOS")
            sound_size_offset = f.tell()
            f.write(b"FOOO")
            write_uint32(f, len(resinfo["Level name"]))
            f.write(bytes(resinfo["Level name"], encoding="ascii"))
            
            f.write(b"HFSB")
            write_uint32(f, 4)
            write_uint32(f, len(sounds)//2)
            
            for entry in sounds:
                #f.write(entry.data)
                entry.write(f)
                
            end = f.tell()
            sound_section_size = end - sound_size_offset - 4 
            f.seek(sound_size_offset)
            write_uint32(f, sound_section_size)
            f.seek(end)
            
            for entry in itertools.chain(models, animations, effects, scripts):
                #f.write(entry.data)
                entry.write(f)

        with bwopen(output, "wb") as final:
            final.write(f.getbuffer())

    
    