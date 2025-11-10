from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuntimeConfiguration:
    use_proton: str = ""
    fork_commands: Optional[List[str]] = None
    command: str = ""
    wine_tricks: Optional[List[str]] = None
