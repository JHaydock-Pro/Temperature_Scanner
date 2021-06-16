import argparse
import jinja2
import json
import os
import pandas as pd
import subprocess
from datetime import datetime

def scan_racks(racks):
    for rack in racks:
        try:
            temps = get_temps_by_rack(args.file, rack)
            if args.json:
                output_to_json(temps, rack)
            if args.stdout:
                output_to_stdout(temps, rack)
            if args.influx:
                output_to_influx(temps, rack)
        except Exception as ex:
            print('Rack %s encountered and exception, some parts of the process may still have succeeded' % rack)
            print(ex)

def load_rack(file, rack):
    with open(file) as json_file:
        data = json.load(json_file)
    return data[rack]

#TODO: Research if there is a more robust/efficient method of doing this than ssh'ing each host individually and greping stdout
def get_temp(host):
    try:
        bashCmd = "ssh -l root %s 'hostname ; ipmitool sensor | grep \"Temp\"'" % host
        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        process.terminate()
        values = output.decode().split("|")

        temps = {
            "inlet": values[1].strip(),
            "temp1": values[10].strip(),
            "temp2": values[19].strip(),
            "exhaust": values[28].strip(),
            "gpu1": values[37].strip(),
            "gpu2": values[46].strip()
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
    if not os.path.exists('logs'):
        os.makedirs('logs')
    now = datetime.now()
    time = now.strftime('%Y_%m_%d_%H_%M')
    filename = os.path.join('logs', '%s_%s.json'%(rack, time))
    with open(filename, 'w') as outfile:
        json.dump(temps, outfile)

def output_to_stdout(temps, rack):
    values = []
    for i in temps:
        values.append([i])
        for j in temps[i]:
            if temps[i][j] != None:
                values[i-1].append(temps[i][j]['inlet'].strip())
                values[i-1].append(temps[i][j]['temp1'].strip())
                values[i-1].append(temps[i][j]['temp2'].strip())
                values[i-1].append(temps[i][j]['exhaust'].strip())
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
        "h2 exhaust"
        ])
    df.style.set_properties(**{'text-align': 'left'})
    df.reset_index(drop=True)
    print(df)

#TODO: Implement
def output_to_influx(temps, rack):
    print('INFLUXDB NOT YET IMPLEMENTED')

parser = argparse.ArgumentParser()
parser.add_argument(
    '-f', '--file',
    help="json file containing lookup tables",
    action='store',
    dest='file',
    required=True
    )
parser.add_argument(
    '-r', '--racks',
    help="comma seperated list of racks from lookup tables",
    action='store',
    dest='racks',
    required=True
    )
parser.add_argument(
    '-j', '--json',
    help="output to json file",
    action='store_true',
    dest='json'
    )
parser.add_argument(
    '-s', '--stdout',
    help="output to stdout",
    action='store_true',
    dest='stdout'
    )
parser.add_argument(
    '-i', '--influx',
    help="output to influxdDB",
    action='store_true',
    dest='influx'
    )
args = parser.parse_args()

racks = args.racks.split(',')
scan_racks(racks)
