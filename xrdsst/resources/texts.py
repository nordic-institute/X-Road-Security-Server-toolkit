texts = {
    # App
    'app.description': 'A toolkit for configuring security server',
    'app.label': 'xrdsst',

    # Root application parameters
    'root.parameter.configfile.description': "Specify configuration file to use instead of default 'config/xrdsst.yml'",

    # Controllers
    'auto.controller.description': 'Automatically performs all operations possible with configuration.',
    'cert.controller.description': 'Commands for performing certificate operations.',
    'client.controller.description': 'Commands for performing client management operations.',
    'init.controller.description': 'Initializes security server with configuration anchor.',
    'timestamp.controller.description': 'Commands for performing timestamping service operations.',
    'token.controller.description': 'Commands for performing token operations.',
    'service.controller.description': 'Commands for performing service operations.',
    'status.controller.description': 'Query for server configuration statuses.',

    # Messages
    'message.file.not.found': "File '{}' not found.",
    'message.file.unreadable': "Could not read file '{}'.",
    'message.config.unparsable': "Error parsing config: {}",
    'message.config.serverless': "No security servers defined in '{}'.",
    'message.server.keyless': "No API key available/acquired for '{}'.",
    'message.skipped': "SKIPPED '{}'"
}

server_error_map = {
    'core.Server.ClientProxy.CannotCreateSignature.Signer.TokenNotActive': 'Indicates that CLIENT proxy token has not been logged in.',
    'core.Server.ClientProxy.IOError': "No valid sign certificate on the CLIENT proxy. The sign certificate may not exist, it may be disabled or it may not have a valid OCSP status.",
    'core.Server.ClientProxy.LoggingFailed.InternalError': 'Writing messages to the message log database fails on the CLIENT proxy.',
    'core.Server.ClientProxy.LoggingFailed.TimestamperFailed': "Timestamping service of CLIENT proxy currently unavailable, unconfigured or unconnectable.",
    'core.Server.ClientProxy.NetworkError': 'CLIENT Proxy is not able to establish a network connection to provider side SERVER Proxy.',
    'core.Server.ClientProxy.OutdatedGlobalConf': 'CLIENT proxy is not able to download global configuration from the Central Server and local copy of the global configuration has expired.',
    'core.Server.ClientProxy.ServiceFailed.InternalError': 'Processing the request failed because of an internal error on the CLIENT proxy.',
    'core.Server.ClientProxy.SslAuthenticationFailed': 'Security server (CLIENT Proxy) has no valid authentication certificate.',
    'core.Server.ClientProxy.UnknownMember': 'The request contains invalid client or service identifier.',

    'core.Server.ServerProxy.CannotCreateSignature.Signer.TokenNotActive': 'SERVER proxy token has not been logged in, contact service PROVIDER administrator.',
    'core.Server.ServerProxy.LoggingFailed.InternalError': 'Processing the request failed because of an internal error on the SERVER proxy.',
    'core.Server.ServerProxy.LoggingFailed.TimestamperFailed': 'Timestamping service of SERVER proxy currently unavailable, unconfigured or unconnectable.',
    'core.Server.ServerProxy.OutdatedGlobalConf': 'SERVER proxy is not able to download global configuration from the Central Server and local copy of the global configuration has expired.',
    'core.Server.ServerProxy.ServiceFailed.CannotCreateSignature': "There's a problem with signer on the PROVIDER SERVER proxy.",
    'core.Server.ServerProxy.ServiceFailed.HttpError': 'SERVER proxy was not able to successfully connect to the service PROVIDER information system.',
    'core.Server.ServerProxy.ServiceFailed.InvalidSoap': 'The service PROVIDER information system returned a malformed SOAP message to SERVER proxy.',
    'core.Server.ServerProxy.ServiceFailed.InternalError': 'Processing the request failed because of an internal error on the PROVIDER SERVER proxy.',
    'core.Server.ServerProxy.ServiceFailed.MissingHeaderField': 'The response returned by the service PROVIDER information system is missing some mandatory SOAP headers.',
    'core.Server.ServerProxy.ServiceDisabled': 'Security server (SERVER Proxy) has disabled the service, maybe temporarily.',
    'core.Server.ServerProxy.SslAuthenticationFailed': 'Security server (SERVER Proxy) has no valid authentication certificate.',
    'core.Server.ServerProxy.UnknownService': 'Service identified by the service code included in the request does not exist on the SERVER proxy.'
}

server_hint_map = {
    'core.Server.ClientProxy.IOError': [
    """    The sign certificate may not exist, it may be disabled or it may not have a valid OCSP status.
      * Make sure the sign certificate is imported into the Security Server.
      * Make sure the sign certificate is active.
      * Make sure the token holding the sign certificate is available and logged in.
      * If the OCSP status of the sign certificate is not in the 'good' state, then
        the Security Server cannot use the certificate.
    """
    ],
    'core.Server.ClientProxy.NetworkError': [
    """    On the CLIENT proxy, outgoing traffic to the provider SERVER proxy ports 5500 and 5577
    must be allowed.
    PROVIDER side server lookup might be failing because it is registered with wrong public FQDN.
    """
    ],
    'core.Server.ClientProxy.OutdatedGlobalConf': [
    """    It is possible that CLIENT proxy is unable to connect to the Central Server.
    Firewall configurations need to be rechecked.
    Restart of "xroad-confclient" process can be tried, if having shell access to CLIENT proxy.
        $ systemctl restart xroad-confclient
    """
    ],
    'core.Server.ClientProxy.SslAuthenticationFailed': [
    """    The authentication certificate may not exist, it may be disabled, it may not be
    registered or it may not have a valid OCSP status.
      * Make sure the authentication certificate is imported into the Security Server.
      * Make sure the authentication certificate is active.
      * Make sure the authentication certificate is registered.
      * Make sure the token holding the authentication certificate is available and logged in.
      * If the OCSP status of the authentication certificate is not in the 'good' state, then
        the Security Server cannot use the certificate.
    """
    ],
    'core.Server.ClientProxy.UnknownMember': [
    """    In case the client is not found, the client specified in the request is not registered at CLIENT proxy.
    In case addresses for service provider are not found, there's an error in the service identifier.
    """
    ],

    # For the SERVER PROXY the helpful hints are not so many, unless the error in fact originates from the
    # other security server of the end-user, there is not much that can be done, contacting PROVIDER administrators
    # is almost always necessary.
    'core.Server.ServerProxy.AccessDenied': [
    """    The error message indicates that the client subsystem does not have sufficient permissions to invoke the
    service. Contact the service PROVIDER about the issue and request access permissions to the service.
    Don't forget to mention the subsystem that you want to use for accessing the service.
    """
    ]
}

ascii_art = {
    'message_flow': [
        '╒═Trusted Network═╕                          . INTERNET .                         ╒═Trusted Network══╕',
        '│                 │      ╒══════════╕       .             .     ╒══════════╕      │                  │',
        '│                 │      │ Security │      |               |    │ Security │      │/ Service (REST)  │',
        '│  xrdsst (REST) -│- ->- │\\ Server /│- ->- | - - ->- - - - | ->-│\\ Server /│- ->- │                  │',
        '│                 │      │ - ->- -  │       .             .     │ - ->- -  │      │\\ Service (SOAP)  │',
        '│                 │      ╘══════════╛        .          .       ╘══════════╛      │                  │',
        '╘═════════════════╛                            INTRANET                           ╘══════════════════╛',
        '',
        ' Service CONSUMER        CLIENT Proxy                           SERVER Proxy        Service PROVIDER'
    ]
}
