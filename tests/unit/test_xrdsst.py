from xrdsst.main import opdep_init


def test_opdep_init_adds_app_opdep():
    class JustObject(object):
        pass

    mock_app = JustObject
    opdep_init(mock_app)
    assert mock_app.OP_GRAPH
    assert mock_app.OP_DEPENDENCY_LIST
    assert mock_app.OP_GRAPH.number_of_nodes() == len(mock_app.OP_DEPENDENCY_LIST)

