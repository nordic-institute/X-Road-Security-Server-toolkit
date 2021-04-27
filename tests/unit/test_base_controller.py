import os
import sys
import tempfile
import unittest

import pytest
import yaml

from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from xrdsst.core.definitions import ROOT_DIR
from xrdsst.configuration.configuration import Configuration
from xrdsst.controllers.base import BaseController
from xrdsst.core.util import convert_swagger_enum
from xrdsst.main import XRDSSTTest
from xrdsst.models import ConnectionType


class TestBaseController(unittest.TestCase):
    configuration_anchor = os.path.join(ROOT_DIR, "tests/resources/configuration-anchor.xml")
    _ss_config = {
        'admin_credentials': 'TOOLKIT_ADMIN_CREDENTIALS',
        'logging': {'file': str(Path.home()) + '/xrdsst_tests.log', 'level': 'INFO'},
        'ssh_access': {'user': 'TOOLKIT_SSH_USER', 'private_key': 'TOOLKIT_SSH_PRIVATE_KEY'},
        'security_server':
            [{'name': 'ss',
              'url': 'https://ss:4000/api/v1',
              'api_key': 'TOOLKIT_SS1_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS',
              'software_token_pin': '1234'},
             {'name': 'ss2',
              'url': 'https://ss2:4000/api/v1',
              'api_key': 'TOOLKIT_SS2_API_KEY',
              'api_key_url': 'https://localhost:4000/api/v1/api-keys',
              'configuration_anchor': configuration_anchor,
              'owner_member_class': 'GOV',
              'owner_member_code': '1234',
              'security_server_code': 'SS2',
              'software_token_pin': '1234'}
             ]}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def get_ss_config(self):
        return self._ss_config

    def create_temp_conf(self, base_controller, temp_file_name):
        config_file = open(temp_file_name, "w")
        config_file.close()
        with open(temp_file_name, "w") as yml_file:
            yaml.dump(self.get_ss_config(), yml_file)
        return base_controller.load_config(temp_file_name)

    def test_load_config(self):
        tmpfile = tempfile.NamedTemporaryFile(mode="wb", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.close()

        temp_file_name = tmpfile.name
        with open(temp_file_name, "w") as yml_file:
            yaml.dump(TestBaseController._ss_config, yml_file)
        base_controller = BaseController()
        with open(temp_file_name, "r") as yml_file:
            cfg = yaml.safe_load(yml_file)

        assert cfg is not None

        ctr_config = base_controller.load_config(temp_file_name)
        os.remove(temp_file_name)

        assert ctr_config == cfg

    def test_load_config_access_exception(self):
        base_controller = BaseController()
        base_controller.app = Mock()
        config_file = "/etc/shadow"
        base_controller.load_config(config_file)

        out, err = self.capsys.readouterr()
        assert out.count("ermission") > 0
        assert out.count("ould not read file") > 0

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

    def test_load_config_malformed_yaml(self):
        # Setup
        tmpfile = tempfile.NamedTemporaryFile(mode="wb", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.write(bytes("{a", "utf-8"))
        tmpfile.close()

        # Given
        config_file = tmpfile.name
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.close = Mock(return_value=None)

        # When
        base_controller.load_config(config_file)

        # Cleanup
        os.remove(config_file)

        # Then
        out, err = self.capsys.readouterr()
        assert out.count("Error parsing config") > 0
        assert out.count("line 1") > 0

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_load_config_spelunked_keys(self):
        # Setup
        tmpfile = tempfile.NamedTemporaryFile(mode="w", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.writelines([
            'kogging:\n',
            '  file: asdqwe\n',
            'security_server:\n',
            '  name: xnnn\n',
            '  ull: http://somesite.com'
        ])
        tmpfile.close()

        # Given
        config_file = tmpfile.name
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.close = Mock(return_value=None)

        # When
        base_controller.load_config(config_file)

        # Cleanup
        os.remove(config_file)

        # Then
        out, err = self.capsys.readouterr()
        assert err.count("kogging NOT AMONG") > 0
        assert err.count("ull NOT AMONG") > 0
        assert out.count("Invalid configuration keys encountered") > 0

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_load_config_serverless(self):
        # Setup
        config_data = [
            'logging:\n',
            '  file: logfile-test.log\n',
            'security_server:\n'
        ]

        tmpfile = tempfile.NamedTemporaryFile(mode="w", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.writelines(config_data)
        tmpfile.close()

        # Given
        config_file = tmpfile.name
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.close = Mock(return_value=None)
        base_controller.is_output_tabulated = Mock(return_value=True)

        # When
        base_controller.load_config(config_file)

        # Cleanup
        os.remove(config_file)

        # Then
        out, err = self.capsys.readouterr()
        assert err.count("No security servers defined") > 0

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_load_config_servers_without_name_or_url(self):
        # Setup
        config_data = [
            'logging:\n',
            '  file: logfile-test.log\n',
            'security_server:\n',
            '  - name: first\n',
            '    url: first_url\n',
            '  - name: second\n',
            '  - url: third_url\n',
            '  - name: fourth\n',
            '    url: fourth_url\n',
            '    security_server_code: ASD\n'
        ]

        tmpfile = tempfile.NamedTemporaryFile(mode="w", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.writelines(config_data)
        tmpfile.close()

        # Given
        config_file = tmpfile.name
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.close = Mock(return_value=None)
        base_controller.is_output_tabulated = Mock(return_value=True)

        # When
        base_controller.load_config(config_file)

        # Cleanup
        os.remove(config_file)

        # Then
        out, err = self.capsys.readouterr()
        assert err.count("security_server[2] missing required 'url'") == 1
        assert err.count("security_server[3] missing required 'name'") == 1

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_load_config_servers_name_or_url_non_unique(self):
        # Setup
        config_data = [
            'logging:\n',
            '  file: logfile-test.log\n',
            'security_server:\n',
            '  - name: first\n',
            '    url: first_url\n',
            '  - name: second\n',
            '    url: second_url\n',
            '  - url: third_url\n',
            '    name: third\n',
            '  - name: fourth\n',
            '    url: third_url\n',
            '    security_server_code: QED\n',
            '  - name: fifth\n',
            '    url: second_url\n',
            '  - name: first\n',
            '    url: faraway.com\n'
        ]

        tmpfile = tempfile.NamedTemporaryFile(mode="w", prefix="xrdsst-", suffix='.yaml', delete=False)
        tmpfile.writelines(config_data)
        tmpfile.close()

        # Given
        config_file = tmpfile.name
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.close = Mock(return_value=None)
        base_controller.is_output_tabulated = Mock(return_value=True)

        # When
        base_controller.load_config(config_file)

        # Cleanup
        os.remove(config_file)

        # Then
        out, err = self.capsys.readouterr()
        assert err.count("security_server[1] 'name' value 'first' is non-unique") == 1
        assert err.count("security_server[6] 'name' value 'first' is non-unique") == 1
        assert err.count("security_server[2] 'url' value 'second_url' is non-unique") == 1
        assert err.count("security_server[5] 'url' value 'second_url' is non-unique") == 1
        assert err.count("security_server[3] 'url' value 'third_url' is non-unique") == 1
        assert err.count("security_server[4] 'url' value 'third_url' is non-unique") == 1

        with self.capsys.disabled():
            sys.stdout.write(out)
            sys.stderr.write(err)

        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_init_logging(self):
        temp_file_name = "temp.log"

        import logging
        logging.getLogger().handlers.clear()
        assert not logging.getLogger().handlers

        if os.path.exists(temp_file_name) and not os.path.isdir(temp_file_name):
            os.remove(temp_file_name)

        self._ss_config["logging"]["file"] = temp_file_name
        base_controller = BaseController()
        base_controller._init_logging(self.get_ss_config())
        assert len(logging.getLogger().handlers) == 1
        assert os.path.exists(temp_file_name)

        logging.shutdown()
        os.remove(temp_file_name)

    def test_init_logging_no_write_access(self):
        temp_file_name = "/root/nocanwrite.log"

        import logging
        logging.getLogger().handlers.clear()
        assert not logging.getLogger().handlers

        self._ss_config["logging"]["file"] = temp_file_name
        base_controller = BaseController()
        base_controller._init_logging(self.get_ss_config())
        assert len(logging.getLogger().handlers) == 1

    def test_init_logging_directory(self):
        temp_file_name = str(Path.home())

        import logging
        logging.getLogger().handlers.clear()
        assert not logging.getLogger().handlers

        self._ss_config["logging"]["file"] = temp_file_name
        base_controller = BaseController()
        base_controller._init_logging(self.get_ss_config())
        assert len(logging.getLogger().handlers) == 1

    def test_no_plain_api_key_logging(self):
        # Given
        temp_log_file = tempfile.NamedTemporaryFile(mode="wb", prefix="xrdsst-", suffix='.yaml', delete=False)
        temp_log_file.close()

        logfile_name = temp_log_file.name

        import logging
        logging.getLogger().handlers.clear()
        assert not logging.getLogger().handlers

        self._ss_config["logging"]["file"] = logfile_name
        base_controller = BaseController()
        base_controller._init_logging(self.get_ss_config())

        the_api_key = '460ad0b9-d023-4087-a291-dc97eddcb7d8'

        # When
        BaseController.log_info("printf style with dict: API key '%(api_key)s' for security server %(ssn)s revoked." %
                                {'api_key': the_api_key, 'ssn': 'madeup-ss'})
        BaseController.log_info("plain concatenated string style: API key '" + the_api_key + "' for security server " + 'madeup-ss' + " revoked.")
        BaseController.log_info("percent style string formation: API key '%s' for revoked." % the_api_key)
        logging.info("direct log of api_key (info) " + the_api_key)
        logging.warning("direct log of api_key (warning)" + the_api_key)

        # Then
        with open(logfile_name, "r") as log_file_r:
            log_lines = log_file_r.readlines()
            assert 5 == len(log_lines)
            assert all(map(lambda s: s.count('********-****-4087-****-************') == 1, log_lines))
            assert all(map(lambda s: s.count(the_api_key) == 0, log_lines))

    def test_get_api_key(self):
        with XRDSSTTest() as app:
            with patch.object(BaseController, 'create_api_key', return_value='88888888-8000-4000-a000-727272727272'):
                base_controller = BaseController()
                base_controller.app = app
                temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
                config = self.create_temp_conf(base_controller, temp_file_name)
                for security_server in config["security_server"]:
                    security_server["api_key"] = 'some key'
                    key = base_controller.get_api_key(config, security_server)
                    assert key != 'api-key-123'
                    os.environ["TOOLKIT_API_KEY"] = ""
                    security_server["api_key"] = 'TOOLKIT_API_KEY'
                    key = base_controller.get_api_key(config, security_server)
                    assert key == '88888888-8000-4000-a000-727272727272'
                os.remove(temp_file_name)

    def test_get_api_key_ssh_key_exception(self):
        with XRDSSTTest() as app:
            base_controller = BaseController()
            base_controller.app = app
            temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
            config = self.create_temp_conf(base_controller, temp_file_name)
            for security_server in config["security_server"]:
                security_server["api_key"] = 'TOOLKIT_API_KEY'
                base_controller.get_api_key(config, security_server)
            os.remove(temp_file_name)
            self.assertRaises(Exception)

    def test_get_api_key_json_exception(self):
        with XRDSSTTest() as app:
            base_controller = BaseController()
            base_controller.app = app
            temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
            config = self.create_temp_conf(base_controller, temp_file_name)
            temp_key_file = open("my_key", "w")
            temp_key_file.close()
            ssh_access = config["ssh_access"]
            for security_server in config["security_server"]:
                ssh_access["private_key"] = 'my_key'
                security_server["api_key"] = 'TOOLKIT_API_KEY'
                base_controller.get_api_key(config, security_server)
            os.remove(temp_file_name)
            os.remove("my_key")
            self.assertRaises(Exception)

    def test_create_api_config(self):
        with XRDSSTTest() as app:
            base_controller = BaseController()
            base_controller.app = app
            temp_file_name = os.path.join(ROOT_DIR, "conf.yaml")
            config = self.create_temp_conf(base_controller, temp_file_name)
            os.environ["TOOLKIT_SS1_API_KEY"] = "f13d5108-7799-426d-a024-1300f52f4a51"
            os.environ["TOOLKIT_SS2_API_KEY"] = "a13d5108-7799-426d-a024-1300f52f4a51"
            for security_server in config["security_server"]:
                configuration = Configuration()
                configuration.api_key['Authorization'] = os.getenv(security_server["api_key"], "")
                configuration.host = security_server["url"]
                configuration.verify_ssl = False
                response = base_controller.create_api_config(security_server)
                assert response.api_key == configuration.api_key
                assert response.host == configuration.host
                assert response.verify_ssl == configuration.verify_ssl
            os.remove(temp_file_name)

    def test_configfile_argument_added(self):
        base_controller = BaseController()
        base_controller._parser = Mock()
        base_parser = base_controller._parser
        base_parser.add_argument = Mock(return_value=None)
        base_controller._pre_argument_parsing()
        base_parser.add_argument.assert_called_once()

    def test_unsuccessful_app_exit_with_nonexistant_config_spec(self):
        base_controller = BaseController()
        base_controller.app = Mock()
        base_controller.app.pargs = Mock()
        base_controller.app.pargs.configfile = 'just/not/there/at/all'
        base_controller.app.close = Mock(return_value=None)
        base_controller.load_config(baseconfig=None)
        base_controller.app.close.assert_called_once_with(os.EX_CONFIG)

    def test_conversion_of_text_to_swagger_enum_succeeds(self):
        assert 'HTTP' == convert_swagger_enum(ConnectionType, "HTTP")
        assert 'HTTPS' == convert_swagger_enum(ConnectionType, "HTTPS")
        assert 'HTTPS_NO_AUTH' == convert_swagger_enum(ConnectionType, "HTTPS_NO_AUTH")

    def test_conversion_of_text_to_swagger_enum_fails(self):
        try:
            convert_swagger_enum(ConnectionType, "HTTPX")
            raise AssertionError("Conversion of 'HTTPX' to ConnectionType should have failed.")
        except SyntaxWarning:
            pass
