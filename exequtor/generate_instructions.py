"""This file provides the code to handle the yaml file which defines the measurement blocks
and in these the kind of measurement, adjusted parameters and swept parameters and values.
"""
from typing import Dict, Any, List
from time import sleep
from math import log10, floor
import sympy as sp
from qupyt.set_up import get_waiting_room, get_home_dir
import ruamel.yaml
import numpy as np


yaml = ruamel.yaml.YAML(typ='safe')
yaml.preserve_quotes = True
waiting_room = get_waiting_room()
saveplace_busy_document = get_home_dir()/"status.txt"  # file
saveplace_optimization_status_document = 'status_optimization.txt'
saveplace_optimized_params = 'optimized_params.yaml'


def wait_while_busy() -> None:
    """ Wait until the measurement is finished before adding a new measurement
    instruction file to the qupit waiting room."""
    wait = True
    while wait:
        with open(saveplace_busy_document, 'r', encoding='utf-8') as file:
            text = file.read()
            if 'ready' in text:
                wait = False
            else:
                sleep(1)


def wait_while_optimization() -> None:
    """
    Wait until the optimization is finished before
    starting the measurements of a new execution block.
    """
    wait = True
    while wait:
        with open(saveplace_optimization_status_document,
                  'r', encoding='utf-8') as file:
            text = file.read()
            if 'finished' in text:
                wait = False
            else:
                sleep(1)


def change_status_optimization(new_status: str) -> None:
    """ Update the status regarding the optimization to any given string."""
    with open(saveplace_optimization_status_document,
              'w', encoding='utf-8') as file:
        file.write(new_status)


def round_to_n(value: float, n: int) -> float:
    """Rounds the input value to n significant digits."""
    value_rounded = round(value, -int(floor(log10(value))) + (n - 1))
    return value_rounded


def values_from_string_function(expression: str,
                                lower: float,
                                upper: float,
                                number_steps: int) -> List[float]:
    """ Generates a list with values from the lower and upper values
    in the specified number of steps following the provided function.
    The function has to be reversible for the provided data
    sets without returning complex values. Funtions have to have the
    variable x and can look as follows:
    log(x), exp(x), x**2, sin(x), ..."""
    x = sp.symbols('x')
    expr = sp.sympify(expression)
    # Find the inverse function
    inverse_expr = [0] * 2
    for i, y in enumerate([lower, upper]):
        try:
            inverse_expr[i] = sp.solve(sp.Eq(expr, y), x)
        except:
            print("No inverse solution could be found!")
    inverse_steps = np.linspace(float(
        inverse_expr[0][-1].evalf()), float(inverse_expr[1][-1].evalf()), number_steps)
    y_values = [expr.subs(x, val) for val in inverse_steps]
    return y_values


def update_params_between_two_notebooks(source: Dict[str, Any],
                                        target: Dict[str, Any]) -> None:
    """Recursive function to update values from a source dictionary to a
    target dictionary. The value will only be updated if the keys leading
    to it are the same fpr both yaml dictionaries."""
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            # Recursively update nested dictionaries
            update_params_between_two_notebooks(value, target[key])
        elif key in target:
            # Update parameter if the key exists in the target dictionary
            target[key] = value


class ExecutionBlock:
    """ExecutionBlock class containing all the parameters
    that a sweep measurement has to have."""

    def __init__(self,
                 base_file: str,
                 sweep_params: List[str],
                 sweep_vals: List[str]):
        """Initialization of a new ExecutionBlock"""
        self.base_file = base_file
        self.sweep_params = sweep_params
        self.sweep_vals = sweep_vals
        self.params: Dict[str, Any]
        self.sweep_functions: List[str]

    def assign_params(self, params: Dict[str, Any]) -> None:
        """Assign the measurement parameters"""
        self.params = params

    def assign_functions(self, sweep_functions: List[str]) -> None:
        """Assign the functions to """
        self.sweep_functions = sweep_functions

    def generate_unique_name(self, value: str) -> str:
        '''Generate unique file name to avoid overwriting files'''
        param_name = ''
        for param in self.sweep_params:
            param_name += '_' + param.split("']")[-2].split("['")[-1]
        savename = 'Sync-sweep' + param_name + value
        return savename

    def write_yaml_file(self, savename: str) -> None:
        with open(savename, 'w', encoding='utf-8') as file:
            yaml.dump(self.params, file)

    def make_range_sweep_value_single(self, sweep_parameter_index: int) -> List[str]:
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
                max_sweep_number[i] = 1
        number_sweep_values = max(max_sweep_number)
        individual_sweep_vals = np.zeros(
            (number_parallelsweepvals, number_sweep_values))
        for i in range(number_parallelsweepvals):
            if sweep[i]:
                rangevals = self.make_range_sweep_value_single(i)
                if hasattr(self, 'sweep_functions') and self.sweep_functions[i] != 'linear':
                    vals = values_from_string_function(self.sweep_functions[i],
                                                       float(
                        rangevals[0]),
                        float(
                        rangevals[1]),
                        number_sweep_values)
                else:
                    vals = np.linspace(float(rangevals[0]), float(
                        rangevals[1]), number_sweep_values)
                for k, val in enumerate(vals):
                    individual_sweep_vals[i, k] = val
            else:
                vals = [float(self.sweep_vals[i])] * number_sweep_values
                for k, val in enumerate(vals):
                    individual_sweep_vals[i, k] = val
        return individual_sweep_vals


def make_yaml_files_for_sweeps(filedata: Dict[str, Any],
                               key: str,
                               optimized_params: dict[str, Any]) -> None:
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
            update_params_between_two_notebooks(
                optimized_params, execution_block.params)
            # loops through every value-update-block
            for j in range(np.shape(rangevals)[1]):
                wait_while_busy()
                value_name_for_save = ''
                for k, block_param in enumerate(execution_block.sweep_params):
                    # loops through the different parameters to be updated
                    exec('execution_block.params' +
                         block_param + f' = {rangevals[k, j]}')
                    value_name_for_save += '_' + \
                        str(round_to_n(rangevals[k, j], 8))
                savename = execution_block.generate_unique_name(
                    value_name_for_save) + '.yaml'
                execution_block.params['experiment_type'] = savename
                execution_block.write_yaml_file(waiting_room/savename)
    else:
        with open(filedata[key]['base_file'], 'r', encoding='utf-8') as p:
            params = yaml.load(p)
            update_params_between_two_notebooks(optimized_params, params)
            savename = filedata[key]['base_file']
            with open(waiting_room/savename, 'w', encoding='utf-8') as file_save:
                yaml.dump(params, file_save)
    change_status_optimization('finished')  # change for final version!!
    print('Finished generating one execution block.')
