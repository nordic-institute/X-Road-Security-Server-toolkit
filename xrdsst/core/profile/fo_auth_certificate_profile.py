from xrdsst.core.profile.Profile import Profile


class FoAuthCertificateProfile(Profile):
    def build_profile(self, profile_info):
        return {
            "C": "FO",
            "O": profile_info.instance_identifier,
            "CN": self.to_short_string(profile_info.member_code)
        }
