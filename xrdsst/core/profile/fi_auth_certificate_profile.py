from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class FIAuthCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": "FI",
            "O": profile_data.member_name,
            "serialNumber": profile_data.serial_number_auth,
            "CN": profile_data.security_server_dns
        }
