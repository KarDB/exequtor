import numpy as np
import ruamel.yaml
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from time import sleep
from math import log10, floor, lcm, log, exp


yaml = ruamel.yaml.YAML(typ = 'safe')
yaml.preserve_quotes = True

filename = 'optmeasurement.yml'
saveplace_busy_document = 'status.txt'   #'/home/karl/.qupyt/status.txt'

def wait_while_busy():
    wait = True
    while wait:
        with open(saveplace_busy_document, 'r') as f:
            text = f.read()
            if text == 'ready\n' or text == 'ready':
                wait = False
            sleep(1)

def round_to_n(value:float, n:int) -> float:
     value_rounded = round(value, -int(floor(log10(value))) + (n - 1))
     return value_rounded

def generate_values_for_string_function(expression:str, lower:float, upper:float, number_steps:int):
    x_values = np.linspace(lower, upper, number_steps)#np.arange(lower, upper + step, step)
    y_values = [eval(expression.replace('x', str(x))) for x in x_values]
    y_min = min(y_values)
    y_max = max(y_values)
    y_values_updated = [lower + ((value - y_min) / (y_max - y_min)) * (upper - lower) for value in y_values]
    return y_values_updated


class ExecutionBlock:
    def __init__(self, base_file: str, sweep_params: List[str], sweep_vals: List[str]):
        self.base_file = base_file
        self.sweep_params = sweep_params
        self.sweep_vals = sweep_vals
        self.params: Dict[str, Any]
        self.sweep_function: List[str]

    def assign_params(self,params):
        self.params = params

    def assign_functions(self, sweep_functions):
        self.sweep_functions = sweep_functions

    def generate_precise_name(self, value:str) -> str:
        param_name = ''
        for i in range(len(self.sweep_params)):
            param_name += '_' + self.sweep_params[i].split("']")[-2].split("['")[-1]
        savename = 'Sync-sweep' + param_name + value
        return savename

    def write_yaml_file(self, savename: str) -> None:
        with open('dumpjamls/'+savename, 'w', encoding='utf-8') as file:
            yaml.dump(self.params, file)

    def make_range_sweep_value_single(self, sweep_parameter_index:int) -> List[float]:
        rangevals = self.sweep_vals
        rangevals = rangevals[int(sweep_parameter_index)].split(';')
        return rangevals

    def make_range_sweep_value_all(self) -> np.ndarray:
        number_parallelsweepvals = len(self.sweep_params)
        sweep = np.zeros(number_parallelsweepvals, dtype=bool)
        max_sweep_number = [0] * number_parallelsweepvals
        for i in range(number_parallelsweepvals):
            if ";" in self.sweep_vals[i]:
                sweep[i] = True
                rangevals = self.make_range_sweep_value_single(i)
                max_sweep_number[i] = int(rangevals[2])
            else:
                max_sweep_number[i] = int(1)
        number_sweep_values = max(max_sweep_number)
        individual_sweep_vals = np.zeros((number_parallelsweepvals, number_sweep_values))

        for i in range(number_parallelsweepvals):
            if sweep[i] == True:
                rangevals = self.make_range_sweep_value_single(i)
                if hasattr(self, 'sweep_functions') and self.sweep_functions[i] != 'linear':
                    vals = generate_values_for_string_function(self.sweep_functions[i],
                                        float(rangevals[0]), float(rangevals[1]), number_sweep_values)
                    print('The function is taken into account')
                else:
                    vals = np.linspace(float(rangevals[0]), float(rangevals[1]), number_sweep_values)
                for k, val in enumerate(vals):
                    individual_sweep_vals[i,k] = val
            elif sweep[i] == False:
                vals = [float(self.sweep_vals[i])]*number_sweep_values
                for k, val in enumerate(vals):
                    individual_sweep_vals[i,k] = val
        print(individual_sweep_vals)
        return individual_sweep_vals



def make_yaml_files_for_sweeps(filename:str, saveplace_busy_document:str):
    with open(filename, 'r', encoding='utf-8') as file:
        filedata = yaml.load(file)
        for i, key in enumerate(filedata.keys()):
            if 'sweep_params' in filedata[key]:

                execution_block = ExecutionBlock(filedata[key]['base_file'],
                                                filedata[key]['sweep_params'],
                                                filedata[key]['sweep_vals'])
                if 'functions' in filedata[key]:
                    execution_block.assign_functions(filedata[key]['functions'])

                rangevals = execution_block.make_range_sweep_value_all()
                with open(execution_block.base_file, 'r', encoding='utf-8') as p:
                    params = yaml.load(p)
                    execution_block.assign_params(params)
                    for j in range(np.shape(rangevals)[1]): #loops through every value-update-block
                        wait_while_busy()
                        value_name_for_save = ''
                        for k in range(len(execution_block.sweep_params)): #loops through the different parameters to be updated
                            exec('execution_block.params'+execution_block.sweep_params[k]+f' = {rangevals[k,j]}')
                            value_name_for_save += '_' + str(round_to_n(rangevals[k,j], 8))
                        savename = execution_block.generate_precise_name(value_name_for_save)
                        execution_block.params['experiment_type'] = savename
                        execution_block.write_yaml_file(savename+'.yaml')
            else:
                with open(filedata[key]['base_file'], 'r', encoding='utf-8') as p:
                    params = yaml.load(p)
                    savename = filedata[key]['base_file']
                    with open('dumpjamls/'+savename, 'w', encoding='utf-8') as file:
                            yaml.dump(params, file)

if __name__ == '__main__':
    make_yaml_files_for_sweeps(filename, saveplace_busy_document)
