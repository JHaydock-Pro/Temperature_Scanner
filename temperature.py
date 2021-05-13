import argparse
import json
import subprocess
from datetime import datetime

def load_rack(file, rack):
    with open(file) as json_file:
        data = json.load(json_file)
    return data[rack]

def get_temp(host):
    try:
        bashCmd = "ssh -l root %s 'hostname ; ipmitool sensor | grep \"Temp\"'" % host
        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        values = output.decode().split("|")

        temps = {
            "inlet": values[1],
            "temp1": values[10],
            "temp2": values[19],
            "exhaust": values[28],
            "gpu1": values[37],
            "gpu2": values[46]
        }
        return temps
    except:
        return None

def get_temps_by_rack(file, rack):
    hosts = {}
    rack_obj = load_rack(file, rack)
    i = 0
    for row in rack_obj:
        i += 1
        hosts[i] = {}
        for host in row:
            hosts[i][host] = get_temp(host)
    return hosts

def get_rack(file, rack):
    data = get_temps_by_rack(file, rack)
    now = datetime.now()
    time = now.strftime("%Y_%m_%d_%H_%M.json")
    filename = "rack%s_%s"%(rack, time)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

get_rack("rack_static_lookup.json", "406")
