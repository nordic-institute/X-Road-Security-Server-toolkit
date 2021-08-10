from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class FIVRKAuthCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": "FI",
            "O": "",
            "serialNumber": profile_data.serial_number
        }