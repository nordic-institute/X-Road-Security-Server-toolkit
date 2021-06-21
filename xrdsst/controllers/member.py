from cement import ex
from xrdsst.api import MemberNamesApi
from xrdsst.api_client.api_client import ApiClient
from xrdsst.controllers.base import BaseController
from xrdsst.resources.texts import texts
from xrdsst.rest.rest import ApiException


class MemberNameListMapper:
    @staticmethod
    def headers():
        return ['MEMBER-NAME', 'MEMBER-CLASS', 'MEMBER-CODE']

    @staticmethod
    def as_list(member):
        return [member.get('member_name'), member.get('member_class'), member.get('member_code')]

    @staticmethod
    def as_object(member):
        return {
            'member_name': member.get('member_name'),
            'member_class': member.get('member_class'),
            'member_code': member.get('member_code')
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

        if self.app.pargs.mclass is None:
            self.log_info('Member class parameter is required for searching member names')
            return
        if self.app.pargs.mcode is None:
            self.log_info('Member code parameter is required for searching member names')
            return

        self.find_name(active_config, self.app.pargs.mclass, self.app.pargs.mcode)

    def find_name(self, config, member_class, member_code):
        ss_api_conf_tuple = list(zip(config["security_server"], map(lambda ss: self.create_api_config(ss, config), config["security_server"])))

        for security_server in config["security_server"]:
            ss_api_config = self.create_api_config(security_server, config)
            member_names_api = MemberNamesApi(ApiClient(ss_api_config))
            try:
                result = {'member_name':'NIIS'} # member_names_api.find_member_name(member_class=member_class, member_code=member_code)
                render_data = []
                if self.is_output_tabulated():
                    render_data = [MemberNameListMapper.headers()]
                    render_data.extend(map(MemberNameListMapper.as_list, [{'member_name': result.member_name,
                                                                           'member_class': member_class,
                                                                           'member_code': member_code}]))
                else:
                    render_data.extend(map(MemberNameListMapper.as_object, [{'member_name': result.member_name,
                                                                             'member_class': member_class,
                                                                             'member_code': member_code}]))
                self.render(render_data)
            except ApiException as err:
                BaseController.log_api_error('MemberNamesApi->find_member_name', err)

        BaseController.log_keyless_servers(ss_api_conf_tuple)
