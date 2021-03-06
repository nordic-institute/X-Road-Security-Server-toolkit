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

class OrphanInformation(object):
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
        'orphans_exist': 'bool'
    }

    attribute_map = {
        'orphans_exist': 'orphans_exist'
    }

    def __init__(self, orphans_exist=False):  # noqa: E501
        """OrphanInformation - a model defined in Swagger"""  # noqa: E501
        self._orphans_exist = None
        self.discriminator = None
        if orphans_exist is not None:
            self.orphans_exist = orphans_exist

    @property
    def orphans_exist(self):
        """Gets the orphans_exist of this OrphanInformation.  # noqa: E501


        :return: The orphans_exist of this OrphanInformation.  # noqa: E501
        :rtype: bool
        """
        return self._orphans_exist

    @orphans_exist.setter
    def orphans_exist(self, orphans_exist):
        """Sets the orphans_exist of this OrphanInformation.


        :param orphans_exist: The orphans_exist of this OrphanInformation.  # noqa: E501
        :type: bool
        """

        self._orphans_exist = orphans_exist

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
        if issubclass(OrphanInformation, dict):
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
        if not isinstance(other, OrphanInformation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
