from abc import ABC, abstractmethod
from xrdsst.core.profile.profile_data import ProfileData

class Profile(ABC):

    @abstractmethod
    def build_profile(self, profile_data: ProfileData):
        pass
