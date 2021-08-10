from xrdsst.core.profile.Profile import Profile
from xrdsst.core.profile.ProfileData import ProfileData

class EjbcaAuthCertificateProfile(Profile):
    def build_profile(self, profile_info: ProfileData):
        return {
            "C": profile_info.instance_identifier,
            "CN": self.to_short_string(profile_info.)
        }






