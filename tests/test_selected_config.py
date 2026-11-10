from rag.retriever import MODES, load_selected


def test_selected_config_is_valid():
    mode, config = load_selected()
    assert mode in MODES
    assert config.pool >= 1
    assert config.list_depth >= config.pool
