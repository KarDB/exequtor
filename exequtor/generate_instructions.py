import yaml
import numpy as np
from pathlib import Path
from typing import Dict, Any
filename = 'optmeasurement.yml'


def writeyamlfile(params: Dict[str, Any], savename: str) -> None:
    with open(savename, 'w', encoding='utf-8') as file:
        yaml.dump(params, file)


with open(filename, 'r', encoding='utf-8') as file:
    filedata = yaml.safe_load(file)

    with open(filedata['M_1']['base_file'], 'r', encoding='utf-8') as p:
        params = yaml.safe_load(p)

        for i, key in enumerate(filedata.keys()):
            rangevals = filedata[key]['sweep_vals']
            rangevals = rangevals[0].split(',')
            for k in np.linspace(float(rangevals[0]), float(rangevals[1]), int(rangevals[2])):
                exec('params'+filedata['M_1']['sweep_params'][0]+f' = {k}')
                sweepvalue = eval('params'+filedata['M_1']['sweep_params'][0])
                print(i, k, sweepvalue)
                savename = 'File_' + str(k)
                writeyamlfile(params, savename)
    # make measurement nAot hardcoded for i in number Ms?
