import pytest

import inet_nm.config as cfg
from inet_nm.data_types import NmNode


@pytest.mark.parametrize(
    "params",
    [
        (cfg.BoardInfoConfig, {"board": "board", "version": "1.0"}),
        (
            cfg.NodesConfig,
            [
                NmNode.from_dict(
                    {
                        "serial": "1",
                        "vendor_id": "vendor_id1",
                        "product_id": "product1",
                        "vendor": "vendor1",
                        "model": "model1",
                        "driver": "driver1",
                    }
                )
            ],
        ),
    ],
)
def test_save_load_config(tmp_path, params):
    """Test saving and loading the board info."""
    cfg_type, data = params
    cfg_inst = cfg_type(tmp_path)

    cfg_inst.save(data)
    loaded_data = cfg_inst.load()
    assert loaded_data == data

    res = cfg_type("does_not_exist").load()
    assert len(res) == 0
    assert isinstance(res, cfg_type._LOAD_TYPE)
