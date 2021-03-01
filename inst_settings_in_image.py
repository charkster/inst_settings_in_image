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

def add_to_pnginfo(image_filename="", data_name="", data_dict={})
    targetImage = PngImageFile(image_filename)
    metadata = PngInfo()
    metadata.add_text(data_name, json.dumps(data_dict))
    targetImage.save(image_filename, pnginfo=metadata)

#instrum_dict = get_instrument_dict()
#print(instrum_dict)
#insert_instrument_settings(image_filename="C:/filename.png",instrument_dict=instrum_dict)
#restore_instrument_settings(image_filename="C:/filename.png",instrument_dict=instrum_dict)
#remove_all_pnginfo(image_filename="C:/filename.png")
#print_pnginfo(image_filename="C:/filename.png")

# Oscilloscope data example
analog_channels = {
    1: ('COOL_V1',      0.2,   -10,  '20MHz', 'DC1M'),
    2: ('NASTY_V2',     0.5,  -4.9,  '20MHz', 'DC1M'),
    3: ('FAVORITE_V3',    2,   -10,  '20MHz', 'DC1M'),
    4: ('OLD_V4',         2,    -8,  '20MHz', 'DC1M'),
    5: ('LITTLE_I1',      2,   3.0,  '20MHz', 'DC'),
    6: ('BIGGER_I2',      2,   1.0,  '20MHz', 'DC'),
    7: ('IMPORTANT_I3',   2,  -0.5,  '20MHz', 'DC'),
    8: ('ARB_I4',       0.5,  -1.5,  '20MHz', 'DC')
}

digital_channels = {
    0: 'cool_name_1',
    1: 'even_better_name_2',
    2: 'the_best_name_3',
    3: 'worst_name_4'
}

measurement_channels = { 1:  ('C1', 'max'),
                         2:  ('C1', 'level@x'),
                         3:  ('C2', 'max'),
                         4:  ('C2', 'level@x'),
                         5:  ('C3', 'max'),
                         6:  ('C3', 'level@x'),
                         7:  ('C5', 'max'),
                         8:  ('C6', 'max'),
                         9:  ('C7', 'max'),
                         10: ('C8', 'max'),
                         11: ('C8', 'level@x'),
                         12: ('C8', 'level@x') }


#add_to_pnginfo(image_filename="C:/filename.png", data_name="analog_channels",      data_dict=analog_channels)
#add_to_pnginfo(image_filename="C:/filename.png", data_name="digital_channels",     data_dict=digital_channels)
#add_to_pnginfo(image_filename="C:/filename.png", data_name="measurement_channels", data_dict=measurement_channels)
