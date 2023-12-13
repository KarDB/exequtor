"""
Users my provide their own analysis script when using executor.
While standard analysis will be provided, some users may which to perform
custom analysis on their measurements.

This module facilitates loading user analysis scripts at runtime.
Please mind the security implications of this when using exequtor.
"""
import importlib.util
from types import ModuleType
from pathlib import Path
from typing import Dict, Any, Optional, Protocol, cast


# pylint: disable=too-few-public-methods
class UserPulseSeqProtocol(Protocol):
    """
    Protocol to define that every generate_sequence
    function takes a dict as input and returns either
    None or another dict.
    """

    def analyse_data(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        :param params: Inputs needed to run the analysis.
        :type params: dict[str, any]
        :return: Returns a dictionary containing the extracted values.
        :rtype: "dict[str, any] | None"
        """


def _load_module_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location('user_analysis', path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Module user_analysis cannot be loaded from path {path}")
    module = importlib.util.module_from_spec(spec)
    # Ensure the loader can execute the module
    if hasattr(spec.loader, 'exec_module'):
        spec.loader.exec_module(module)
    else:
        raise ImportError(
            "The loader for user_analysis doesn't support execution")
    return module


def run_user_analysis(path: Path,
                      params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Load and execute analysis module definition provided by the user.
    """
    user_ps = cast(UserPulseSeqProtocol, _load_module_from_path(path))
    dependent_parameters = user_ps.analyse_data(params)
    return dependent_parameters
