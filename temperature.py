import argparse
import json
import subprocess
from datetime import datetime
import pandas as pd
import jinja2

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

def output_to_json(temps, rack):
    now = datetime.now()
    time = now.strftime("%Y_%m_%d_%H_%M.json")
    filename = "rack%s_%s"%(rack, time)
    with open(filename, 'w') as outfile:
        json.dump(temps, outfile)

def output_to_stdout(temps, rack):
    values = []
    for i in temps:
        values.append([i])
        for j in temps[i]:
            if temps[i][j] != None:
                values[i-1].append(temps[i][j]['inlet'])
                values[i-1].append(temps[i][j]['temp1'])
                values[i-1].append(temps[i][j]['temp2'])
                values[i-1].append(temps[i][j]['exhaust'])
    pd.set_option('display.max_columns', 9)
    pd.set_option('display.width', 0)
    values.reverse()
    df = pd.DataFrame(values, columns=[
        "row",
        "h1 inlet",
        "h1 temp1",
        "h1 temp2",
        "h1 exhaust",
        "h2 inlet",
        "h2 temp1",
        "h2 temp2",
        "h2 exhaust"])
    df.style.set_properties(**{'text-align': 'left'})
    print(df)


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help="json file containing lookup tables", action='store', dest='file')
parser.add_argument('-r', '--rack', help="number or name of rack", action='store', dest='rack')
parser.add_argument('-j', '--json', help="output to json file", action='store_true', dest='json')
parser.add_argument('-s', '--stdout', help="output to stdout", action='store_true', dest='stdout')
args = parser.parse_args()

temps = get_temps_by_rack(args.file, args.rack)
if args.json:
    output_to_json(temps, args.rack)

if args.stdout:
    output_to_stdout(temps, args.rack)
