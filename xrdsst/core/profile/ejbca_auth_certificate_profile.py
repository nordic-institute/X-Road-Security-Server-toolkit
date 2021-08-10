from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class EjbcaAuthCertificateProfile(Profile):
    def build_profile(self, profile_info: ProfileData):
        return {
            "C": profile_info.instance_identifier,
            "CN": self.to_short_string(profile_info.security_server_code)
        }






