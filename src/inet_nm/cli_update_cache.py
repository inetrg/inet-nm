import argparse

import inet_nm.config as cfg
import inet_nm.location as loc
from inet_nm._helpers import nm_print


def _main():
    parser = argparse.ArgumentParser(description="Update the location cache")
    cfg.config_arg(parser)

    args = parser.parse_args()
    loc_mapping = cfg.LocationConfig(config_dir=args.config).load()
    nodes = cfg.NodesConfig(config_dir=args.config).load()
    loc_cache = cfg.LocationCache(config_dir=args.config)
    loc_cache.check_file(writable=True)

    cache = loc.get_location_cache(nodes, loc_mapping)

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
