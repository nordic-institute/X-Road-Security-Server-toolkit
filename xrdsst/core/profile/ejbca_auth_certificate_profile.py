from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class EjbcaAuthCertificateProfile(Profile):
    @staticmethod
    def build_profile(profile_data: ProfileData):
        return {
            "C": profile_data.instance_identifier,
            "CN": profile_data.security_server_code
        }






