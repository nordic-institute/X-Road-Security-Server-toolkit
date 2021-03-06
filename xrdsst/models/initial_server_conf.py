# coding: utf-8

"""
    X-Road Security Server Admin API

    X-Road Security Server Admin API. Note that the error metadata responses described in some endpoints are subjects to change and may be updated in upcoming versions.  # noqa: E501

    OpenAPI spec version: 1.0.31
    Contact: info@niis.org
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class InitialServerConf(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'owner_member_class': 'str',
        'owner_member_code': 'str',
        'security_server_code': 'str',
        'software_token_pin': 'str',
        'ignore_warnings': 'bool'
    }

    attribute_map = {
        'owner_member_class': 'owner_member_class',
        'owner_member_code': 'owner_member_code',
        'security_server_code': 'security_server_code',
        'software_token_pin': 'software_token_pin',
        'ignore_warnings': 'ignore_warnings'
    }

    def __init__(self, owner_member_class=None, owner_member_code=None, security_server_code=None, software_token_pin=None, ignore_warnings=False):  # noqa: E501
        """InitialServerConf - a model defined in Swagger"""  # noqa: E501
        self._owner_member_class = None
        self._owner_member_code = None
        self._security_server_code = None
        self._software_token_pin = None
        self._ignore_warnings = None
        self.discriminator = None
        if owner_member_class is not None:
            self.owner_member_class = owner_member_class
        if owner_member_code is not None:
            self.owner_member_code = owner_member_code
        if security_server_code is not None:
            self.security_server_code = security_server_code
        if software_token_pin is not None:
            self.software_token_pin = software_token_pin
        if ignore_warnings is not None:
            self.ignore_warnings = ignore_warnings

    @property
    def owner_member_class(self):
        """Gets the owner_member_class of this InitialServerConf.  # noqa: E501

        member class  # noqa: E501

        :return: The owner_member_class of this InitialServerConf.  # noqa: E501
        :rtype: str
        """
        return self._owner_member_class

    @owner_member_class.setter
    def owner_member_class(self, owner_member_class):
        """Sets the owner_member_class of this InitialServerConf.

        member class  # noqa: E501

        :param owner_member_class: The owner_member_class of this InitialServerConf.  # noqa: E501
        :type: str
        """

        self._owner_member_class = owner_member_class

    @property
    def owner_member_code(self):
        """Gets the owner_member_code of this InitialServerConf.  # noqa: E501

        member code  # noqa: E501

        :return: The owner_member_code of this InitialServerConf.  # noqa: E501
        :rtype: str
        """
        return self._owner_member_code

    @owner_member_code.setter
    def owner_member_code(self, owner_member_code):
        """Sets the owner_member_code of this InitialServerConf.

        member code  # noqa: E501

        :param owner_member_code: The owner_member_code of this InitialServerConf.  # noqa: E501
        :type: str
        """

        self._owner_member_code = owner_member_code

    @property
    def security_server_code(self):
        """Gets the security_server_code of this InitialServerConf.  # noqa: E501

        security server code  # noqa: E501

        :return: The security_server_code of this InitialServerConf.  # noqa: E501
        :rtype: str
        """
        return self._security_server_code

    @security_server_code.setter
    def security_server_code(self, security_server_code):
        """Sets the security_server_code of this InitialServerConf.

        security server code  # noqa: E501

        :param security_server_code: The security_server_code of this InitialServerConf.  # noqa: E501
        :type: str
        """

        self._security_server_code = security_server_code

    @property
    def software_token_pin(self):
        """Gets the software_token_pin of this InitialServerConf.  # noqa: E501

        pin code for the initial software token  # noqa: E501

        :return: The software_token_pin of this InitialServerConf.  # noqa: E501
        :rtype: str
        """
        return self._software_token_pin

    @software_token_pin.setter
    def software_token_pin(self, software_token_pin):
        """Sets the software_token_pin of this InitialServerConf.

        pin code for the initial software token  # noqa: E501

        :param software_token_pin: The software_token_pin of this InitialServerConf.  # noqa: E501
        :type: str
        """

        self._software_token_pin = software_token_pin

    @property
    def ignore_warnings(self):
        """Gets the ignore_warnings of this InitialServerConf.  # noqa: E501

        if true, any ignorable warnings are ignored. if false (or missing), any warnings cause request to fail  # noqa: E501

        :return: The ignore_warnings of this InitialServerConf.  # noqa: E501
        :rtype: bool
        """
        return self._ignore_warnings

    @ignore_warnings.setter
    def ignore_warnings(self, ignore_warnings):
        """Sets the ignore_warnings of this InitialServerConf.

        if true, any ignorable warnings are ignored. if false (or missing), any warnings cause request to fail  # noqa: E501

        :param ignore_warnings: The ignore_warnings of this InitialServerConf.  # noqa: E501
        :type: bool
        """

        self._ignore_warnings = ignore_warnings

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(InitialServerConf, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, InitialServerConf):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
