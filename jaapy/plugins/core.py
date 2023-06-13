# Core plugin
# author: Vladislav Janvarev

from jaapy.chain_img_processor import ChainImgProcessor

# start function
def start(core:ChainImgProcessor):
    manifest = {
        "name": "Core plugin",
        "version": "1.0",

        "default_options": {
            "default_chain": "faceswap", # default chain to run
            "init_on_start": "faceswap", # init these processors on start
        },

    }
    return manifest

def start_with_options(core:ChainImgProcessor, manifest:dict):
    #print(manifest["options"])
    options = manifest["options"]

    core.default_chain = options["default_chain"]
    core.init_on_start = options["init_on_start"]

    return manifest
