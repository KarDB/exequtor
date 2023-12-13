#import yaml
import numpy as np
import ruamel.yaml
#from ruamel.yaml import YAML, YAMLError
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from time import sleep
from math import log10, floor

yaml = ruamel.yaml.YAML(typ = 'safe')
yaml.preserve_quotes = True

#filename = 'optmeasurement.yml'
#saveplace_busy_document = 'status.txt'   #'/home/karl/.qupyt/status.txt'

def wait_while_busy():
    wait = True
    while wait:
        with open(saveplace_busy_document, 'r') as f:
            text = f.read()
            if text == 'ready\n' or text == 'ready':
                wait = False
            sleep(1)

def round_to_n(value:float, n:int) -> float:
     x_rounded = round(value, -int(floor(log10(value))) + (n - 1))
     return x_rounded


class ExecutionBlock:
    def __init__(self, base_file: str, sweep_params: List[str], sweep_vals: List[str]):
        self.base_file = base_file
        self.sweep_params = sweep_params
        self.sweep_vals = sweep_vals
        self.params: Dict[str, Any]

    def assign_params(self,params):
        self.params = params

    def generate_precise_name(self, value:str) -> str:
        param_name = ''
        for i in range(len(self.sweep_params)):
            param_name += '_' + self.sweep_params[i].split("']")[-2].split("['")[-1]
        savename = 'Sync-sweep' + param_name + value
        return savename

    def write_yaml_file(self, savename: str) -> None:
        with open(savename, 'w', encoding='utf-8') as file:
            yaml.dump(self.params, file)

    def make_range_sweep_value_single(self, sweep_parameter_index:int) -> List[float]:
        rangevals = self.sweep_vals
        rangevals = rangevals[int(sweep_parameter_index)].split(',')
        vals = np.linspace(float(rangevals[0]), float(rangevals[1]), int(rangevals[2]))
        return vals

    def make_range_sweep_value_all(self) -> np.ndarray:
        number_parallelsweepvals = len(self.sweep_params)
        number_sweep_values = len(self.make_range_sweep_value_single(0))
        individual_sweep_vals = np.zeros((number_parallelsweepvals, number_sweep_values))
        for i in range(number_parallelsweepvals):
            vals = self.make_range_sweep_value_single(i)
            for k, val in enumerate(vals):
                individual_sweep_vals[i,k] = val
        return individual_sweep_vals


#if __name__ == '__main__:'
def make_yaml_files_for_sweeps(filename:str, saveplace_busy_document:str):
    with open(filename, 'r', encoding='utf-8') as file:
        filedata = yaml.load(file)
        for i, key in enumerate(filedata.keys()):
            execution_block = ExecutionBlock(filedata[key]['base_file'],
                                    filedata[key]['sweep_params'],
                                    filedata[key]['sweep_vals'])
            rangevals = execution_block.make_range_sweep_value_all()
            with open(execution_block.base_file, 'r', encoding='utf-8') as p:
                params = yaml.load(p)
                execution_block.assign_params(params)
                for j in range(np.shape(rangevals)[1]):
                    wait_while_busy()
                    value_name_for_save = ''
                    for k in range(len(execution_block.sweep_params)):
                        exec('execution_block.params'+execution_block.sweep_params[k]+f' = {rangevals[k,j]}')
                        value_name_for_save += '_' + str(round_to_n(rangevals[k,j], 8))
                    savename = execution_block.generate_precise_name(value_name_for_save)
                    execution_block.params['experiment_type'] = savename
                    execution_block.write_yaml_file(savename+'.yaml')
