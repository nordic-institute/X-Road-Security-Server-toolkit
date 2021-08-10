class ProfileData(object):
    def __init__(self, instance_identifier, member_class, member_code, security_server_id, security_server_code):  # noqa: E501
        """Client - a model defined in Swagger"""  # noqa: E501

        self.instance_identifier = instance_identifier
        self.member_class = member_class
        self.member_code = member_code
        self.security_server_id = security_server_id
        self.security_server_code = security_server_code

    @property
    def instance_identifier(self):
        return self._instance_identifier

    @property
    def member_class(self):
        return self._member_class

    @property
    def member_code(self):
        return self._member_code

    @property
    def security_server_id(self):
        return self._security_server_id

    @property
    def security_server_code(self):
        return self._security_server_code

