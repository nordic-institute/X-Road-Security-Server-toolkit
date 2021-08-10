from xrdsst.core.profile.abstract_certificate_profile import Profile
from xrdsst.core.profile.is_auth_certificate_profile import IsAuthCertificateProfile
from xrdsst.core.profile.is_sign_certificate_profile import IsSignCertificateProfile
from xrdsst.core.profile.fo_auth_certificate_profile import FoAuthCertificateProfile
from xrdsst.core.profile.fo_sign_certificate_profile import FoSignCertificateProfile
from xrdsst.core.profile.fivrk_sign_certificate_profile import FIVRKSignCertificateProfile
from xrdsst.core.profile.fivrk_auth_certificate_profile import FIVRKAuthCertificateProfile
from xrdsst.core.profile.ejbca_auth_certificate_profile import EjbcaAuthCertificateProfile
from xrdsst.core.profile.ejbca_sign_certificate_profile import EjbcaSignCertificateProfile
from xrdsst.core.profile.profile_types_enum import ProfileTypesEnum
from xrdsst.core.profile.certificate_types_enum import CertificateTypesEnum


class ProfileFactory:

    @staticmethod
    def get_profile_builder(certificate_type, profile_type=None):
        if certificate_type == CertificateTypesEnum.AUTH:
            if profile_type is None:
                return FIVRKAuthCertificateProfile()
            elif profile_type == ProfileTypesEnum.FO:
                return FoAuthCertificateProfile()
            elif profile_type == ProfileTypesEnum.IS:
                return IsAuthCertificateProfile()
            elif profile_type == ProfileTypesEnum.FIVRK:
                return FIVRKAuthCertificateProfile()
            elif profile_type == ProfileTypesEnum.EJBCA:
                return EjbcaAuthCertificateProfile()
            else:
                raise ValueError("Error getting profile builder, profile type '%s' not valid" % profile_type)
        elif certificate_type == CertificateTypesEnum.SIGN:
            if profile_type is None:
                return FIVRKSignCertificateProfile()
            elif profile_type == ProfileTypesEnum.FO:
                return FoSignCertificateProfile()
            elif profile_type == ProfileTypesEnum.IS:
                return IsSignCertificateProfile()
            elif profile_type == ProfileTypesEnum.FIVRK:
                return FIVRKSignCertificateProfile()
            elif profile_type == ProfileTypesEnum.EJBCA:
                return EjbcaSignCertificateProfile()
            else:
                raise ValueError("Error getting profile builder, profile type '%s' not valid" % profile_type)



