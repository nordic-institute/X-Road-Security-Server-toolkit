from xrdsst.core.profile.Profile import Profile

class FoSignCertificateProfile(Profile):
    def build_profile(self, profile_info):
        return{
            "C": "FO",
            "O": profile_info.instance_identifier,
            "OU": profile_info.member_class,
            "CN": profile_info.member_code,
            "serialNumber": self.to_short_string(profile_info.server_id)
        }