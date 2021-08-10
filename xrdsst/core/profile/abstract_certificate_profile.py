from abc import ABC, abstractmethod


class Profile(ABC):

    @abstractmethod
    def build_profile(self):
        pass

    def to_short_string(self, param):
        return param