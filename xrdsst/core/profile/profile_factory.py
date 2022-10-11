from xrdsst.core.profile.is_auth_certificate_profile import IsAuthCertificateProfile
from xrdsst.core.profile.is_sign_certificate_profile import IsSignCertificateProfile
from xrdsst.core.profile.fo_auth_certificate_profile import FoAuthCertificateProfile
from xrdsst.core.profile.fo_sign_certificate_profile import FoSignCertificateProfile
from xrdsst.core.profile.fi_sign_certificate_profile import FISignCertificateProfile
from xrdsst.core.profile.fi_auth_certificate_profile import FIAuthCertificateProfile
from xrdsst.core.profile.ejbca_auth_certificate_profile import EjbcaAuthCertificateProfile
from xrdsst.core.profile.ejbca_sign_certificate_profile import EjbcaSignCertificateProfile
from xrdsst.core.profile.skklass3_auth_certificate_profile import SkKlass3AuthCertificateProfile
from xrdsst.core.profile.skklass3_sign_certificate_profile import SkKlass3SignCertificateProfile
from xrdsst.core.profile.profile_types_enum import ProfileTypesEnum
from xrdsst.core.profile.certificate_types_enum import CertificateTypesEnum


class ProfileFactory:

    @staticmethod
    def get_profile_builder(certificate_type, profile_type=None):
        if profile_type is None:
            return EjbcaAuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else EjbcaSignCertificateProfile()
        elif profile_type == ProfileTypesEnum.FO:
            return FoAuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else FoSignCertificateProfile()
        elif profile_type == ProfileTypesEnum.IS:
            return IsAuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else IsSignCertificateProfile()
        elif profile_type == ProfileTypesEnum.FI:
            return FIAuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else FISignCertificateProfile()
        elif profile_type == ProfileTypesEnum.EJBCA:
            return EjbcaAuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else EjbcaSignCertificateProfile()
        elif profile_type == ProfileTypesEnum.SKKLASS3:
            return SkKlass3AuthCertificateProfile() if certificate_type == CertificateTypesEnum.AUTH else SkKlass3SignCertificateProfile()
        else:
            raise ValueError("Error getting profile builder, profile type '%s' not valid" % profile_type)
