import copy

from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.controllers.status import StatusController
from xrdsst.core.conf_keys import ConfKeysRoot, ConfKeysSecurityServer
from xrdsst.core.util import op_node_to_ctr_cmd_text
from xrdsst.resources.texts import texts


class AutoController(BaseController):
    class Meta:
        label = 'apply'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['auto.controller.description']

    @ex(help='autoconfig', hide=True)
    def _default(self):
        active_config = self.load_config()
        self._auto(active_config)

    def _auto(self, active_config):
        all_server_config = copy.deepcopy(active_config)
        for i in range(0, len(all_server_config[ConfKeysRoot.CONF_KEY_ROOT_SERVER])):
            single_server_config = all_server_config[ConfKeysRoot.CONF_KEY_ROOT_SERVER][i:(i+1)]
            active_config[ConfKeysRoot.CONF_KEY_ROOT_SERVER] = single_server_config
            self._single_server_auto(active_config)
        status_controller = StatusController()
        status_controller.app = self.app
        status_controller.load_config = (lambda: all_server_config)
        status_controller._default()

    def _single_server_auto(self, active_config):
        self.app.auto_apply = True
        ssn = active_config[ConfKeysRoot.CONF_KEY_ROOT_SERVER][0][ConfKeysSecurityServer.CONF_KEY_NAME]

        self.update_op_statuses(active_config)

        ss_api_config = self.app.OP_GRAPH.nodes[self.app.OP_DEPENDENCY_LIST[0]]['servers'][ssn]['api_config']
        if not ss_api_config:
            self.log_info("SKIPPED AUTO ->'" + ssn + "'. " + texts['message.server.keyless'].format(ssn))
            return

        first_status = self.app.OP_GRAPH.nodes[self.app.OP_DEPENDENCY_LIST[0]]['servers'][ssn]['status']
        if not first_status.connectivity_status[0]:
            self.log_info("SKIPPED AUTO ->'" + ssn + "' no connectivity, (" + first_status.connectivity_status[1] + ").")
            return

        for dep_op in self.app.OP_DEPENDENCY_LIST:
            op_node = self.app.OP_GRAPH.nodes[dep_op]
            if op_node.get('operation'):
                if not op_node['controller'] in self.app.Meta.handlers:
                    raise Exception("No registered controller " + str(op_node['controller']) + " found.")

                # Prep
                op_text = op_node_to_ctr_cmd_text(self.app.OP_GRAPH, dep_op)
                done_at_start = op_node['is_done'](ssn)
                self.log_info("AUTO ['" + op_text + "']->'" + ssn + "'" + (" (redo) " if done_at_start else ''))

                # Exec
                ctr = op_node['controller']()
                ctr.app = self.app
                ctr.load_config = (lambda: active_config)
                op_node['operation'](ctr)

                # Eval outcome
                self.update_op_statuses(active_config)
                done_at_end = op_node['is_done'](ssn)

                if not done_at_end:
                    self.log_info(
                        "AUTO ['" + op_text + "'] completion was NOT detected.\n"
                        "Some operations require waiting for global configuration renewal.")
                    o_ix = self.app.OP_DEPENDENCY_LIST.index(dep_op)
                    next_op = self.app.OP_DEPENDENCY_LIST[o_ix+1:o_ix+2]
                    if next_op:
                        self.log_info("Next AUTO operation would have been ['" + op_node_to_ctr_cmd_text(self.app.OP_GRAPH, next_op[0]) + "'].")
                    break

        self.log_info("AUTO ['status']->'" + ssn + "' AT THE END OF AUTOCONFIGURATION.")
