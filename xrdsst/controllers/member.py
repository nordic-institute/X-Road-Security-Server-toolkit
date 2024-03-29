from cement import ex
from xrdsst.api import MemberNamesApi, MemberClassesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException


class MemberNameListMapper:
    @staticmethod
    def headers():
        return ['SECURITY-SERVER', 'MEMBER-NAME', 'MEMBER-CLASS', 'MEMBER-CODE']

    @staticmethod
    def as_list(member):
        return [member.get('security_server'), member.get('member_name'), member.get('member_class'), member.get('member_code')]

    @staticmethod
    def as_object(member):
        return {
            'security_server': member.get('security_server'),
            'member_name': member.get('member_name'),
            'member_class': member.get('member_class'),
            'member_code': member.get('member_code')
        }


class MemberClassListMapper:
    @staticmethod
    def headers():
        return ['SECURITY-SERVER', 'INSTANCE', 'MEMBER-CLASS']

    @staticmethod
    def as_list(member):
        return [member.get('security_server'), member.get('instance'), member.get('member_class')]

    @staticmethod
    def as_object(member):
        return {
            'security_server': member.get('security_server'),
            'instance': member.get('instance'),
            'member_class': member.get('member_class')
        }


class MemberController(BaseController):
    class Meta:
        label = 'member'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['member.controller.description']

    @ex(help="Find member name",
        arguments=[
            (['--class'], {'help': 'member class option', 'dest': 'mclass'}),
            (['--code'], {'help': 'member code option', 'dest': 'mcode'})
        ]
        )
    def find(self):
        active_config = self.load_config()

        missing_parameters = []
        if self.app.pargs.mclass is None:
            missing_parameters.append('class')
        if self.app.pargs.mcode is None:
            missing_parameters.append('code')
        if len(missing_parameters) > 0:
            BaseController.log_info('The following parameters missing for finding member names: %s' % missing_parameters)
            return

        self.find_name(active_config, self.app.pargs.mclass, self.app.pargs.mcode)

    @ex(help="List member classes", arguments=[(['--instance'], {'help': 'X-Road instance', 'dest': 'instance'})])
    def list_classes(self):
        active_config = self.load_config()
        self.list_member_classes(active_config, self.app.pargs.instance)

    def find_name(self, config, member_class, member_code):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_find_name(ss_api_config, security_server, member_class, member_code)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_find_name(self, ss_api_config, security_server, member_class, member_code):
        member_names_api = MemberNamesApi(ApiClient(ss_api_config))
        try:
            result = member_names_api.find_member_name(member_class=member_class, member_code=member_code)
            render_data = []
            member_data = {'security_server': security_server["name"],
                           'member_name': result.member_name,
                           'member_class': member_class,
                           'member_code': member_code}
            if self.is_output_tabulated():
                render_data = [MemberNameListMapper.headers()]
                render_data.extend(map(MemberNameListMapper.as_list, [member_data]))
            else:
                render_data.extend(map(MemberNameListMapper.as_object, [member_data]))
            self.render(render_data)
            return result
        except ApiException as err:
            BaseController.log_api_error('MemberNamesApi->find_member_name', err)

    def list_member_classes(self, config, instance):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            self.remote_list_classes(ss_api_config, security_server, instance)

        BaseController.log_keyless_servers(ss_api_conf_tuple)

    def remote_list_classes(self, ss_api_config, security_server, instance):
        member_classes_api = MemberClassesApi(ApiClient(ss_api_config))
        try:
            if instance is None:
                member_classes = member_classes_api.get_member_classes(current_instance=True)
            else:
                member_classes = member_classes_api.get_member_classes_for_instance(id=instance)
            member_class_list = []
            for member_class in member_classes:
                member_class_list.append({'security_server': security_server["name"], 'instance': instance, 'member_class': member_class})
            render_data = []
            if self.is_output_tabulated():
                render_data = [MemberClassListMapper.headers()]
                render_data.extend(map(MemberClassListMapper.as_list, member_class_list))
            else:
                render_data.extend(map(MemberClassListMapper.as_object, member_class_list))
            self.render(render_data)
            return member_classes
        except ApiException as err:
            BaseController.log_api_error('MemberClassesApi->get_member_classes', err)
