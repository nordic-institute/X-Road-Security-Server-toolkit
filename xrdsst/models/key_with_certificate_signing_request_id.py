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

class KeyWithCertificateSigningRequestId(object):
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
        'key': 'Key',
        'csr_id': 'str'
    }

    attribute_map = {
        'key': 'key',
        'csr_id': 'csr_id'
    }

    def __init__(self, key=None, csr_id=None):  # noqa: E501
        """KeyWithCertificateSigningRequestId - a model defined in Swagger"""  # noqa: E501
        self._key = None
        self._csr_id = None
        self.discriminator = None
        self.key = key
        self.csr_id = csr_id

    @property
    def key(self):
        """Gets the key of this KeyWithCertificateSigningRequestId.  # noqa: E501


        :return: The key of this KeyWithCertificateSigningRequestId.  # noqa: E501
        :rtype: Key
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this KeyWithCertificateSigningRequestId.


        :param key: The key of this KeyWithCertificateSigningRequestId.  # noqa: E501
        :type: Key
        """
        if key is None:
            raise ValueError("Invalid value for `key`, must not be `None`")  # noqa: E501

        self._key = key

    @property
    def csr_id(self):
        """Gets the csr_id of this KeyWithCertificateSigningRequestId.  # noqa: E501

        CSR id  # noqa: E501

        :return: The csr_id of this KeyWithCertificateSigningRequestId.  # noqa: E501
        :rtype: str
        """
        return self._csr_id

    @csr_id.setter
    def csr_id(self, csr_id):
        """Sets the csr_id of this KeyWithCertificateSigningRequestId.

        CSR id  # noqa: E501

        :param csr_id: The csr_id of this KeyWithCertificateSigningRequestId.  # noqa: E501
        :type: str
        """
        if csr_id is None:
            raise ValueError("Invalid value for `csr_id`, must not be `None`")  # noqa: E501

        self._csr_id = csr_id

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
        if issubclass(KeyWithCertificateSigningRequestId, dict):
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
        if not isinstance(other, KeyWithCertificateSigningRequestId):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
