import yaml
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
filename = 'optmeasurement.yml'


class ExecutionBlock:
    def __init__(self, base_file: str, sweep_params: List[str], sweep_vals: List[str]):
        self.base_file = base_file
        self.sweep_params = sweep_params
        self.sweep_vals = sweep_vals
        self.params: Dict[str, Any]

    def write_yaml_file(self, savename: str) -> None:
        with open(savename, 'w', encoding='utf-8') as file:
            yaml.dump(self.params, file)

    def make_range_sweep_value(self, sweep_parameter_index):
        pass


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
                # write_yaml_file(params, savename)
    # make measurement nAot hardcoded for i in number Ms?

execution_block = ExecutionBlock(filedata['M_1']['base_file'],
                                 filedata['M_1']['sweep_params'],
                                 filedata['M_1']['sweep_vals']),
