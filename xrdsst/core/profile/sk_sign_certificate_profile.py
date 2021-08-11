from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class SkSignCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "SN": profile_data.member_code,
            "CN": profile_data.member_name
        }