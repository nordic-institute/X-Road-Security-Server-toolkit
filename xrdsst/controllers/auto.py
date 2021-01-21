from cement import ex
from xrdsst.controllers.base import BaseController
from xrdsst.resources.texts import texts


class AutoController(BaseController):
    class Meta:
        label = 'apply'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = texts['auto.controller.description']

    @ex(help='autoconfig', hide=True)
    def _default(self):
        config_file = self.load_config()
        self._doit(config_file)

    def _doit(self, config_file):
        self.init_logging(config_file)
        self.auto_ss()

    def auto_ss(self):
        for dep_op in self.app.OP_DEPENDENCY_LIST:
            op_node = self.app.OP_GRAPH.nodes[dep_op]
            if op_node.get('operation'):
                if not op_node['controller'] in self.app.Meta.handlers:
                    raise Exception("No registered controller " + str(op_node['controller']) + " found.")

                ctr = op_node['controller']()
                ctr.app = self.app
                op_node['operation'](ctr)
