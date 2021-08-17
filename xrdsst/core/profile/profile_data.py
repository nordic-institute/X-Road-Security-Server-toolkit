class ProfileData(object):
    def __init__(self, instance_identifier, member_class, member_code, security_server_code, security_server_dns, owner_class, owner_code, member_name):
        self._instance_identifier = instance_identifier
        self._member_class = member_class
        self._member_code = member_code
        self._security_server_code = security_server_code
        self._security_server_dns = security_server_dns
        self._owner_class = owner_class
        self._owner_code = owner_code
        self._member_name = member_name

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
        return "/%s/%s/%s" % (self._owner_class, self._owner_code, self._security_server_code)

    @property
    def security_server_code(self):
        return self._security_server_code

    @property
    def serial_number_auth(self):
        return '/'.join([self._instance_identifier, self._security_server_code, self._owner_class])

    @property
    def serial_number_sign(self):
        return '/'.join([self._instance_identifier, self._security_server_code, self._member_class])

    @property
    def security_server_dns(self):
        return self._security_server_dns

    @property
    def member_name(self):
        return self._member_name

    @property
    def owner_code(self):
        return self._owner_code
