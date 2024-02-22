import argparse

import inet_nm.config as cfg
import inet_nm.location as loc
from inet_nm._helpers import nm_print
from inet_nm.power_control import DEFAULT_MAX_ALLOWED_NODES, PowerControl


def _main():
    parser = argparse.ArgumentParser(description="Update the location cache")
    cfg.config_arg(parser)

    args = parser.parse_args()
    loc_mapping = cfg.LocationConfig(config_dir=args.config).load()
    nodes = cfg.NodesConfig(config_dir=args.config).load()
    loc_cache = cfg.LocationCache(config_dir=args.config)
    loc_cache.check_file(writable=True)
    caches = []
    with PowerControl(
        locations=loc_mapping,
        nodes=nodes,
        max_powered_devices=DEFAULT_MAX_ALLOWED_NODES,
    ) as pc:
        while not pc.power_on_complete:
            pc.power_on_chunk()
            caches.append(loc.get_location_cache(nodes, loc_mapping))
            pc.power_off_unused()
    cache = loc.merge_location_cache_chunks(caches)
    loc_cache.save(cache)
    nm_print(f"Updated {loc_cache.file_path}")


def main():
    """Updates the current state of board locations."""
    try:
        _main()
    except KeyboardInterrupt:
        nm_print("\nUser aborted...")


if __name__ == "__main__":
    main()
