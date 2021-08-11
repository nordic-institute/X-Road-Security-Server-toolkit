from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class FoSignCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": "FO",
            "O": profile_data.instance_identifier,
            "OU": profile_data.member_class,
            "CN": profile_data.member_code,
            "serialNumber": profile_data.security_server_id
        }
