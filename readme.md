# Temperature Reader

Script to fetch the temperatures of hosts in particular racks.

1. Start a ssh agent with a valid keypair for all the hosts in the rack(s).
```
eval `ssh-agent`
ssh-add path/to/private/key
```
2. Run script using the command line options below

| Option | Required? | Effect |
|--------|-----------|--------|
| -f, --file [filename] | Yes | Specify path to json file containing lookup tables for racks. E.g. '-f rack_static_lookup.json' |
| -r, --rack [keys] | Yes | Comma separated list of keys for racks in the lookup tables. E.g. '-r 406,407' |
| -j, --json | No | Export the output to a json file in Logs directory. |
| -s, --stdout | No | Export the output to console stdout in Logs directory. |
| -i, --influx | No | Export the output to influxDB, NOT YET IMPLEMENTED |

Note: Any hosts that are unreachable or otherwise fail to provide temperatures will simply use None values.

---
## TODO
- Output to long-term storage solution such as influxDB.
- Visualise data, or have something grafana do it.
- Explore more robust and efficient solutions than individually ssh'ing to each host.
- Explore more robust solution than grepping stdout.
