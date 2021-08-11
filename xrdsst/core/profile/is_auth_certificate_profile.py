from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class IsAuthCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": "IS",
            "CN": profile_data.security_server_dns,
            "serialNumber": profile_data.security_server_id
        }
