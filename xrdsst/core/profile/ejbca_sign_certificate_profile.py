from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.profile_data import ProfileData


class EjbcaSignCertificateProfile(Profile):
    def build_profile(self, profile_data: ProfileData):
        return {
            "C": profile_data.instance_identifier,
            "O": profile_data.member_class,
            "CN": profile_data.member_code
        }




