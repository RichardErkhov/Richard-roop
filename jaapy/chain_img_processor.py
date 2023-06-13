from jaapy.jaa import JaaCore
from termcolor import colored, cprint
from typing import Any

version = "3.1.2"


class ChainImgProcessor(JaaCore):
    def __init__(self):
        JaaCore.__init__(self)

        self.processors:dict = {
        }

        self.processors_objects:dict[str,list[ChainImgPlugin]] = {}

        self.default_chain = ""
        self.init_on_start = ""

        self.inited_processors = []

    def process_plugin_manifest(self, modname, manifest):
        # adding processors from plugin manifest
        if "img_processor" in manifest:  # process commands
            for cmd in manifest["img_processor"].keys():
                self.processors[cmd] = manifest["img_processor"][cmd]

        return manifest

    def init_with_plugins(self):
        self.init_plugins(["core"])
        #self.init_plugins()
        self.display_init_info()

        #self.init_translator_engine(self.default_translator)
        init_on_start_arr = self.init_on_start.split(",")
        for proc_id in init_on_start_arr:
            self.init_processor(proc_id)

    def run_chain(self, img, params:dict[str,Any] = None, chain:str = None, thread_index:int = 0):
        if chain is None:
            chain = self.default_chain
        if params is None:
            params = {}
        params["_thread_index"] = thread_index

        chain_ar = chain.split(",")
        # init all not inited processors first
        for proc_id in chain_ar:
            if proc_id != "":
                if not proc_id in self.inited_processors:
                    self.init_processor(proc_id)

        # run processing
        for proc_id in chain_ar:
            if proc_id != "":
                #img = self.processors[proc_id][1](self, img, params) # params can be modified inside
                img = self.processors_objects[proc_id][thread_index].process(img,params)

        return img, params

    # ---------------- init translation stuff ----------------
    def fill_processors_for_thread_chains(self, threads:int = 1, chain:str = None):
        if chain is None:
            chain = self.default_chain

        chain_ar = chain.split(",")
        # init all not inited processors first
        for processor_id in chain_ar:
            if processor_id != "":
                if self.processors_objects.get(processor_id) is None:
                    self.processors_objects[processor_id] = []
                while len(self.processors_objects[processor_id]) < threads:
                    self.add_processor_to_list(processor_id)

    def add_processor_to_list(self, processor_id: str):
        obj = self.processors[processor_id](self)
        obj.init_plugin()
        if self.processors_objects.get(processor_id) is None:
            self.processors_objects[processor_id] = []
        self.processors_objects[processor_id].append(obj)
    def init_processor(self, processor_id: str):
        if processor_id == "": # blank line case
            return

        if processor_id in self.inited_processors:
            # already inited
            return

        try:
            self.print_blue("TRY: init processor plugin '{0}'...".format(processor_id))
            #self.processors[processor_id][0](self)
            self.add_processor_to_list(processor_id)
            self.inited_processors.append(processor_id)
            self.print_blue("SUCCESS: '{0}' inited!".format(processor_id))

        except Exception as e:
            self.print_error("Error init processor plugin {0}...".format(processor_id), e)

    # ------------ formatting stuff -------------------
    def display_init_info(self):
        cprint("ChainImgProcessor v{0}:".format(version), "blue", end=' ')
        self.format_print_key_list("processors:", self.processors.keys())

    def format_print_key_list(self, key:str, value:list):
        print(colored(key+": ", "blue")+", ".join(value))

    def print_error(self,err_txt,e:Exception = None):
        cprint(err_txt,"red")
        # if e != None:
        #     cprint(e,"red")
        import traceback
        traceback.print_exc()

    def print_red(self,txt):
        cprint(txt,"red")

    def print_blue(self, txt):
        cprint(txt, "blue")

class ChainImgPlugin:
    def __init__(self, core: ChainImgProcessor):
        self.core = core

    def init_plugin(self): # here you can init something. Called once
        pass
    def process(self, img, params:dict): # process img. Called multiple
        return img

_img_processor:ChainImgProcessor = None
def get_single_image_processor() -> ChainImgProcessor:
    global _img_processor
    if _img_processor is None:
        _img_processor = ChainImgProcessor()
        _img_processor.init_with_plugins()
    return _img_processor
