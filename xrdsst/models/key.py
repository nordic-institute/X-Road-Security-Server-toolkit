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

class Key(object):
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
        'name': 'str',
        'label': 'str',
        'certificates': 'list[TokenCertificate]',
        'certificate_signing_requests': 'list[TokenCertificateSigningRequest]',
        'usage': 'KeyUsageType',
        'available': 'bool',
        'saved_to_configuration': 'bool',
        'possible_actions': 'PossibleActions'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'label': 'label',
        'certificates': 'certificates',
        'certificate_signing_requests': 'certificate_signing_requests',
        'usage': 'usage',
        'available': 'available',
        'saved_to_configuration': 'saved_to_configuration',
        'possible_actions': 'possible_actions'
    }

    def __init__(self, id=None, name=None, label=None, certificates=None, certificate_signing_requests=None, usage=None, available=None, saved_to_configuration=None, possible_actions=None):  # noqa: E501
        """Key - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._name = None
        self._label = None
        self._certificates = None
        self._certificate_signing_requests = None
        self._usage = None
        self._available = None
        self._saved_to_configuration = None
        self._possible_actions = None
        self.discriminator = None
        self.id = id
        self.name = name
        self.label = label
        self.certificates = certificates
        self.certificate_signing_requests = certificate_signing_requests
        if usage is not None:
            self.usage = usage
        if available is not None:
            self.available = available
        if saved_to_configuration is not None:
            self.saved_to_configuration = saved_to_configuration
        if possible_actions is not None:
            self.possible_actions = possible_actions

    @property
    def id(self):
        """Gets the id of this Key.  # noqa: E501

        key id  # noqa: E501

        :return: The id of this Key.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Key.

        key id  # noqa: E501

        :param id: The id of this Key.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this Key.  # noqa: E501

        key name  # noqa: E501

        :return: The name of this Key.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Key.

        key name  # noqa: E501

        :param name: The name of this Key.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def label(self):
        """Gets the label of this Key.  # noqa: E501

        key label  # noqa: E501

        :return: The label of this Key.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this Key.

        key label  # noqa: E501

        :param label: The label of this Key.  # noqa: E501
        :type: str
        """
        if label is None:
            raise ValueError("Invalid value for `label`, must not be `None`")  # noqa: E501

        self._label = label

    @property
    def certificates(self):
        """Gets the certificates of this Key.  # noqa: E501

        list of certificates for the key  # noqa: E501

        :return: The certificates of this Key.  # noqa: E501
        :rtype: list[TokenCertificate]
        """
        return self._certificates

    @certificates.setter
    def certificates(self, certificates):
        """Sets the certificates of this Key.

        list of certificates for the key  # noqa: E501

        :param certificates: The certificates of this Key.  # noqa: E501
        :type: list[TokenCertificate]
        """
        if certificates is None:
            raise ValueError("Invalid value for `certificates`, must not be `None`")  # noqa: E501

        self._certificates = certificates

    @property
    def certificate_signing_requests(self):
        """Gets the certificate_signing_requests of this Key.  # noqa: E501

        list of CSRs for the key  # noqa: E501

        :return: The certificate_signing_requests of this Key.  # noqa: E501
        :rtype: list[TokenCertificateSigningRequest]
        """
        return self._certificate_signing_requests

    @certificate_signing_requests.setter
    def certificate_signing_requests(self, certificate_signing_requests):
        """Sets the certificate_signing_requests of this Key.

        list of CSRs for the key  # noqa: E501

        :param certificate_signing_requests: The certificate_signing_requests of this Key.  # noqa: E501
        :type: list[TokenCertificateSigningRequest]
        """
        if certificate_signing_requests is None:
            raise ValueError("Invalid value for `certificate_signing_requests`, must not be `None`")  # noqa: E501

        self._certificate_signing_requests = certificate_signing_requests

    @property
    def usage(self):
        """Gets the usage of this Key.  # noqa: E501


        :return: The usage of this Key.  # noqa: E501
        :rtype: KeyUsageType
        """
        return self._usage

    @usage.setter
    def usage(self, usage):
        """Sets the usage of this Key.


        :param usage: The usage of this Key.  # noqa: E501
        :type: KeyUsageType
        """

        self._usage = usage

    @property
    def available(self):
        """Gets the available of this Key.  # noqa: E501

        if the key is available  # noqa: E501

        :return: The available of this Key.  # noqa: E501
        :rtype: bool
        """
        return self._available

    @available.setter
    def available(self, available):
        """Sets the available of this Key.

        if the key is available  # noqa: E501

        :param available: The available of this Key.  # noqa: E501
        :type: bool
        """

        self._available = available

    @property
    def saved_to_configuration(self):
        """Gets the saved_to_configuration of this Key.  # noqa: E501

        if the key is saved to configuration  # noqa: E501

        :return: The saved_to_configuration of this Key.  # noqa: E501
        :rtype: bool
        """
        return self._saved_to_configuration

    @saved_to_configuration.setter
    def saved_to_configuration(self, saved_to_configuration):
        """Sets the saved_to_configuration of this Key.

        if the key is saved to configuration  # noqa: E501

        :param saved_to_configuration: The saved_to_configuration of this Key.  # noqa: E501
        :type: bool
        """

        self._saved_to_configuration = saved_to_configuration

    @property
    def possible_actions(self):
        """Gets the possible_actions of this Key.  # noqa: E501


        :return: The possible_actions of this Key.  # noqa: E501
        :rtype: PossibleActions
        """
        return self._possible_actions

    @possible_actions.setter
    def possible_actions(self, possible_actions):
        """Sets the possible_actions of this Key.


        :param possible_actions: The possible_actions of this Key.  # noqa: E501
        :type: PossibleActions
        """

        self._possible_actions = possible_actions

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
        if issubclass(Key, dict):
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
        if not isinstance(other, Key):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
