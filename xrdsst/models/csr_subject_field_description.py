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

class CsrSubjectFieldDescription(object):
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
        'label': 'str',
        'label_key': 'str',
        'default_value': 'str',
        'read_only': 'bool',
        'required': 'bool',
        'localized': 'bool'
    }

    attribute_map = {
        'id': 'id',
        'label': 'label',
        'label_key': 'label_key',
        'default_value': 'default_value',
        'read_only': 'read_only',
        'required': 'required',
        'localized': 'localized'
    }

    def __init__(self, id=None, label=None, label_key=None, default_value=None, read_only=None, required=None, localized=None):  # noqa: E501
        """CsrSubjectFieldDescription - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._label = None
        self._label_key = None
        self._default_value = None
        self._read_only = None
        self._required = None
        self._localized = None
        self.discriminator = None
        self.id = id
        if label is not None:
            self.label = label
        if label_key is not None:
            self.label_key = label_key
        if default_value is not None:
            self.default_value = default_value
        self.read_only = read_only
        self.required = required
        self.localized = localized

    @property
    def id(self):
        """Gets the id of this CsrSubjectFieldDescription.  # noqa: E501

        the identifier of the field (such as 'O', 'OU' etc)  # noqa: E501

        :return: The id of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this CsrSubjectFieldDescription.

        the identifier of the field (such as 'O', 'OU' etc)  # noqa: E501

        :param id: The id of this CsrSubjectFieldDescription.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def label(self):
        """Gets the label of this CsrSubjectFieldDescription.  # noqa: E501

        label of the field, used to display the field in the user interface  # noqa: E501

        :return: The label of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this CsrSubjectFieldDescription.

        label of the field, used to display the field in the user interface  # noqa: E501

        :param label: The label of this CsrSubjectFieldDescription.  # noqa: E501
        :type: str
        """

        self._label = label

    @property
    def label_key(self):
        """Gets the label_key of this CsrSubjectFieldDescription.  # noqa: E501

        localization key for label of the field, used to display the field in the user interface  # noqa: E501

        :return: The label_key of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: str
        """
        return self._label_key

    @label_key.setter
    def label_key(self, label_key):
        """Sets the label_key of this CsrSubjectFieldDescription.

        localization key for label of the field, used to display the field in the user interface  # noqa: E501

        :param label_key: The label_key of this CsrSubjectFieldDescription.  # noqa: E501
        :type: str
        """

        self._label_key = label_key

    @property
    def default_value(self):
        """Gets the default_value of this CsrSubjectFieldDescription.  # noqa: E501

        the default value of the field. Can be empty.  # noqa: E501

        :return: The default_value of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: str
        """
        return self._default_value

    @default_value.setter
    def default_value(self, default_value):
        """Sets the default_value of this CsrSubjectFieldDescription.

        the default value of the field. Can be empty.  # noqa: E501

        :param default_value: The default_value of this CsrSubjectFieldDescription.  # noqa: E501
        :type: str
        """

        self._default_value = default_value

    @property
    def read_only(self):
        """Gets the read_only of this CsrSubjectFieldDescription.  # noqa: E501

        if this field is read-only  # noqa: E501

        :return: The read_only of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: bool
        """
        return self._read_only

    @read_only.setter
    def read_only(self, read_only):
        """Sets the read_only of this CsrSubjectFieldDescription.

        if this field is read-only  # noqa: E501

        :param read_only: The read_only of this CsrSubjectFieldDescription.  # noqa: E501
        :type: bool
        """
        if read_only is None:
            raise ValueError("Invalid value for `read_only`, must not be `None`")  # noqa: E501

        self._read_only = read_only

    @property
    def required(self):
        """Gets the required of this CsrSubjectFieldDescription.  # noqa: E501

        if this field is required to be filled  # noqa: E501

        :return: The required of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: bool
        """
        return self._required

    @required.setter
    def required(self, required):
        """Sets the required of this CsrSubjectFieldDescription.

        if this field is required to be filled  # noqa: E501

        :param required: The required of this CsrSubjectFieldDescription.  # noqa: E501
        :type: bool
        """
        if required is None:
            raise ValueError("Invalid value for `required`, must not be `None`")  # noqa: E501

        self._required = required

    @property
    def localized(self):
        """Gets the localized of this CsrSubjectFieldDescription.  # noqa: E501

        if true, label key is in property \"label_key\". If false, actual label is in property \"label\"  # noqa: E501

        :return: The localized of this CsrSubjectFieldDescription.  # noqa: E501
        :rtype: bool
        """
        return self._localized

    @localized.setter
    def localized(self, localized):
        """Sets the localized of this CsrSubjectFieldDescription.

        if true, label key is in property \"label_key\". If false, actual label is in property \"label\"  # noqa: E501

        :param localized: The localized of this CsrSubjectFieldDescription.  # noqa: E501
        :type: bool
        """
        if localized is None:
            raise ValueError("Invalid value for `localized`, must not be `None`")  # noqa: E501

        self._localized = localized

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
        if issubclass(CsrSubjectFieldDescription, dict):
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
        if not isinstance(other, CsrSubjectFieldDescription):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
