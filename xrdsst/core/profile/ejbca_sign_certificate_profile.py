from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class EjbcaSignCertificateProfile(Profile):
    def build_profile(self, profile_info: ProfileData):
        return {
            "C": profile_info.instance_identifier,
            "O": profile_info.member_class,
            "CN": profile_info.member_code
        }




