from dataclasses import dataclass
from typing import List


@dataclass
class RuntimeConfiguration:
    use_proton: str = ""
    fork_commands: List[str] = []
    command: str = ""
    wine_tricks: List[str] = []
