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

class Endpoint(object):
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
        'id': 'str',
        'service_code': 'str',
        'method': 'str',
        'path': 'str',
        'generated': 'bool'
    }

    attribute_map = {
        'id': 'id',
        'service_code': 'service_code',
        'method': 'method',
        'path': 'path',
        'generated': 'generated'
    }

    def __init__(self, id=None, service_code=None, method=None, path=None, generated=None):  # noqa: E501
        """Endpoint - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._service_code = None
        self._method = None
        self._path = None
        self._generated = None
        self.discriminator = None
        if id is not None:
            self.id = id
        self.service_code = service_code
        self.method = method
        self.path = path
        if generated is not None:
            self.generated = generated

    @property
    def id(self):
        """Gets the id of this Endpoint.  # noqa: E501

        unique identifier  # noqa: E501

        :return: The id of this Endpoint.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Endpoint.

        unique identifier  # noqa: E501

        :param id: The id of this Endpoint.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def service_code(self):
        """Gets the service_code of this Endpoint.  # noqa: E501


        :return: The service_code of this Endpoint.  # noqa: E501
        :rtype: str
        """
        return self._service_code

    @service_code.setter
    def service_code(self, service_code):
        """Sets the service_code of this Endpoint.


        :param service_code: The service_code of this Endpoint.  # noqa: E501
        :type: str
        """
        if service_code is None:
            raise ValueError("Invalid value for `service_code`, must not be `None`")  # noqa: E501

        self._service_code = service_code

    @property
    def method(self):
        """Gets the method of this Endpoint.  # noqa: E501

        http method mapped to this endpoint  # noqa: E501

        :return: The method of this Endpoint.  # noqa: E501
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """Sets the method of this Endpoint.

        http method mapped to this endpoint  # noqa: E501

        :param method: The method of this Endpoint.  # noqa: E501
        :type: str
        """
        if method is None:
            raise ValueError("Invalid value for `method`, must not be `None`")  # noqa: E501
        allowed_values = ["*", "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]  # noqa: E501
        if method not in allowed_values:
            raise ValueError(
                "Invalid value for `method` ({0}), must be one of {1}"  # noqa: E501
                .format(method, allowed_values)
            )

        self._method = method

    @property
    def path(self):
        """Gets the path of this Endpoint.  # noqa: E501

        relative path where this endpoint is mapped to  # noqa: E501

        :return: The path of this Endpoint.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this Endpoint.

        relative path where this endpoint is mapped to  # noqa: E501

        :param path: The path of this Endpoint.  # noqa: E501
        :type: str
        """
        if path is None:
            raise ValueError("Invalid value for `path`, must not be `None`")  # noqa: E501

        self._path = path

    @property
    def generated(self):
        """Gets the generated of this Endpoint.  # noqa: E501

        has endpoint been generated from openapi3 description  # noqa: E501

        :return: The generated of this Endpoint.  # noqa: E501
        :rtype: bool
        """
        return self._generated

    @generated.setter
    def generated(self, generated):
        """Sets the generated of this Endpoint.

        has endpoint been generated from openapi3 description  # noqa: E501

        :param generated: The generated of this Endpoint.  # noqa: E501
        :type: bool
        """

        self._generated = generated

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
        if issubclass(Endpoint, dict):
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
        if not isinstance(other, Endpoint):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
