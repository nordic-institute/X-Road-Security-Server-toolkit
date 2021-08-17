from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class FIVRKSignCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": "FI",
            "O": profile_data.member_name,
            "serialNumber": profile_data.serial_number_sign,
            "CN": profile_data.member_code
        }