from abc import ABC, abstractmethod
from typing import List
from layer3.canonical import CanonicalMachine
from layer3.launchplan import LaunchPlan

class EmulatorAdapter(ABC):

    @abstractmethod
    def supports(self, system_profile) -> bool:
        """
        Whether this backend can attempt execution for the given profile.
        """
        pass

    @abstractmethod
    def generate_variants(
        self,
        machine_or_intent,
        system_profile
    ) -> List[LaunchPlan]:
        pass
