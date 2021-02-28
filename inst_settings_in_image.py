import pyvisa
from hmp4040              import hmp4040
from keithley_2308        import keithley_2308
from tektronics_afg3000   import tektronics_afg3000
import json
from PIL.PngImagePlugin   import PngImageFile, PngInfo
import time

def remove_all_pnginfo(image_filename=""):
    targetImage = PngImageFile(image_filename)
    metadata = ""
    targetImage.save(image_filename, pnginfo=metadata)

def print_pnginfo(image_filename=""):
    targetImage = PngImageFile(image_filename)
    all_settings_list = targetImage.text
    for settings_key in all_settings_list:
        print(settings_key)
        print(json.loads(all_settings_list[settings_key]))

def get_instrument_dict():
    # this dictionary is the IDN string as the key and the instrument address as the value
    instrument_dict = {}
    rm = pyvisa.ResourceManager()
    # rm = pyvisa.ResourceManager('@py')
    for inst in rm.list_resources():
        handle = rm.open_resource(inst)
        try:
            instrument_idn = handle.query("*IDN?")
        except:
            pass
        else:
            instrument_dict[instrument_idn] = inst
    return instrument_dict

def insert_instrument_settings(image_filename="",instrument_dict=[]):
    targetImage = PngImageFile(image_filename)
    metadata = PngInfo()
    rm = pyvisa.ResourceManager()

    for key in instrument_dict:
        if (key.startswith("HAMEG,HMP4040")):
            hmp4040 = hmp4040_power_supply(pyvisa_instr=rm.open_resource(instrument_dict[key]))
            hmp4040_unique_scpi = hmp4040.get_unique_scpi_list()
            metadata.add_text("hmp4040_unique_scpi", json.dumps(hmp4040_unique_scpi))
        if (key.startswith("KEITHLEY INSTRUMENTS INC.,MODEL 2308")):
            k2308 = keithley_2308(pyvisa_instr=rm.open_resource(instrument_dict[key]))
            k2308_unique_scpi = k2308.get_unique_scpi_list()
            metadata.add_text("k2308_unique_scpi", json.dumps(k2308_unique_scpi))
        if (key.startswith("TEKTRONIX,AFG3102")):
            tek_afg3000 = tektronics_afg3000(pyvisa_instr=rm.open_resource(instrument_dict[key]))
            tek_afg3000_unique_scpi = tek_afg3000.get_unique_scpi_list()
            metadata.add_text("tek_afg3000_unique_scpi", json.dumps(tek_afg3000_unique_scpi))
	
	targetImage.save(image_filename, pnginfo=metadata)

def restore_instrument_settings(image_filename="",instrument_dict=[]):
    targetImage = PngImageFile(image_filename)
    all_settings_dict = targetImage.text
    rm = pyvisa.ResourceManager()
    supported_inst_dict = {'k2308_unique_scpi'       : "KEITHLEY INSTRUMENTS INC.,MODEL 2308",
                           'hmp4040_unique_scpi'     : "HAMEG,HMP4040",
                           'tek_afg3000_unique_scpi' : "TEKTRONIX,AFG3102" }

    for settings_key in all_settings_dict:                                         # loop thru all settings inside image
        if (settings_key in supported_inst_dict):                                  # only process supported instruments
            unique_scpi = json.loads(all_settings_dict[settings_key])              # get the unique scpi state of the instrument
            for instrument_key in instrument_dict:                                 # loop thru all connected instruments
                if (instrument_key.startswith(supported_inst_dict[settings_key])): # only process connected instruments that match supported instruments
                    instrument = rm.open_resource(instrument_dict[instrument_key])
                    instrument.write('*RST')
                    time.sleep(2)
                    for scpi_cmd in unique_scpi:
                        instrument.write(scpi_cmd)

#instrum_dict = get_instrument_dict()
#print(instrum_dict)
#insert_instrument_settings(image_filename="C:/filename.png",instrument_dict=instrum_dict)
#restore_instrument_settings(image_filename="C:/filename.png",instrument_dict=instrum_dict)
#remove_all_pnginfo(image_filename="C:/filename.png")
#print_pnginfo(image_filename="C:/filename.png")
