# coding: utf-8

"""
    X-Road Security Server Admin API

    X-Road Security Server Admin API. Note that the error metadata responses described in some endpoints are subjects to change and may be updated in upcoming versions.  # noqa: E501

    OpenAPI spec version: 1.0.30
    Contact: info@niis.org
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ServiceDescriptionDisabledNotice(object):
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
        'disabled_notice': 'str'
    }

    attribute_map = {
        'disabled_notice': 'disabled_notice'
    }

    def __init__(self, disabled_notice=None):  # noqa: E501
        """ServiceDescriptionDisabledNotice - a model defined in Swagger"""  # noqa: E501
        self._disabled_notice = None
        self.discriminator = None
        if disabled_notice is not None:
            self.disabled_notice = disabled_notice

    @property
    def disabled_notice(self):
        """Gets the disabled_notice of this ServiceDescriptionDisabledNotice.  # noqa: E501

        disabled service notice  # noqa: E501

        :return: The disabled_notice of this ServiceDescriptionDisabledNotice.  # noqa: E501
        :rtype: str
        """
        return self._disabled_notice

    @disabled_notice.setter
    def disabled_notice(self, disabled_notice):
        """Sets the disabled_notice of this ServiceDescriptionDisabledNotice.

        disabled service notice  # noqa: E501

        :param disabled_notice: The disabled_notice of this ServiceDescriptionDisabledNotice.  # noqa: E501
        :type: str
        """

        self._disabled_notice = disabled_notice

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
        if issubclass(ServiceDescriptionDisabledNotice, dict):
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
        if not isinstance(other, ServiceDescriptionDisabledNotice):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
