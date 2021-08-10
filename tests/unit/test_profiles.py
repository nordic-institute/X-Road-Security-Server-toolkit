import unittest
from xrdsst.core.profile.profile_data import ProfileData
from xrdsst.core.profile.profile_types_enum import ProfileTypesEnum
from xrdsst.core.profile.certificate_types_enum import CertificateTypesEnum
from xrdsst.core.profile.profile_factory import ProfileFactory
import pytest


class TestMember(unittest.TestCase):
    profile_data = ProfileData(
        instance_identifier="DEV",
        member_class="COM",
        member_code="12345",
        security_server_dns="ssX_dns",
        security_server_code="ssX_code",
        owner_code="111",
        owner_class="ORG",
        member_name="NIIS"
    )

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_profile_data_construct(self):
        assert self.profile_data.serial_number_auth == "DEV/ssX_code/ORG"
        assert self.profile_data.serial_number_sign == "DEV/ssX_code/COM"
        assert self.profile_data.security_server_id == "/ORG/111/ssX_code"

    def test_ejbca_auth_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.AUTH, profile_type=ProfileTypesEnum.EJBCA)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 2
        assert result["C"] == self.profile_data.instance_identifier
        assert result["CN"] == self.profile_data.security_server_code

    def test_ejbca_sign_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.SIGN, profile_type=ProfileTypesEnum.EJBCA)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 3
        assert result["C"] == self.profile_data.instance_identifier
        assert result["O"] == self.profile_data.member_class
        assert result["CN"] == self.profile_data.member_code

    def test_fivrk_auth_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.AUTH, profile_type=ProfileTypesEnum.FIVRK)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 4
        assert result["C"] == "FI"
        assert result["O"] == self.profile_data.member_name
        assert result["serialNumber"] == self.profile_data.serial_number_auth
        assert result["CN"] == self.profile_data.security_server_dns

    def test_fivrk_sign_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.SIGN, profile_type=ProfileTypesEnum.FIVRK)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 4
        assert result["C"] == "FI"
        assert result["O"] == self.profile_data.member_name
        assert result["serialNumber"] == self.profile_data.serial_number_sign
        assert result["CN"] == self.profile_data.member_code

    def test_fo_auth_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.AUTH, profile_type=ProfileTypesEnum.FO)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 3
        assert result["C"] == "FO"
        assert result["O"] == self.profile_data.instance_identifier
        assert result["CN"] == self.profile_data.security_server_id

    def test_fo_sign_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.SIGN, profile_type=ProfileTypesEnum.FO)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 5
        assert result["C"] == "FO"
        assert result["O"] == self.profile_data.instance_identifier
        assert result["OU"] == self.profile_data.member_class
        assert result["CN"] == self.profile_data.member_code
        assert result["serialNumber"] == self.profile_data.security_server_id

    def test_is_auth_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.AUTH, profile_type=ProfileTypesEnum.IS)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 3
        assert result["C"] == "IS"
        assert result["CN"] == self.profile_data.security_server_dns
        assert result["serialNumber"] == self.profile_data.security_server_id

    def test_is_sign_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.SIGN, profile_type=ProfileTypesEnum.IS)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 5
        assert result["C"] == "IS"
        assert result["O"] == self.profile_data.instance_identifier
        assert result["OU"] == self.profile_data.member_class
        assert result["CN"] == self.profile_data.member_code
        assert result["serialNumber"] == self.profile_data.security_server_id

    def test_default_auth_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.AUTH, profile_type=None)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 4
        assert result["C"] == "FI"
        assert result["O"] == self.profile_data.member_name
        assert result["serialNumber"] == self.profile_data.serial_number_auth
        assert result["CN"] == self.profile_data.security_server_dns

    def test_default_sign_certificate_profile(self):
        profile = ProfileFactory().get_profile_builder(certificate_type=CertificateTypesEnum.SIGN, profile_type=None)
        result = profile.build_profile(profile_data=self.profile_data)

        assert len(result) == 4
        assert result["C"] == "FI"
        assert result["O"] == self.profile_data.member_name
        assert result["serialNumber"] == self.profile_data.serial_number_sign
        assert result["CN"] == self.profile_data.member_code
