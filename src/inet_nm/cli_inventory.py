import argparse
import json

import inet_nm.check as chk
import inet_nm.config as cfg


def main():
    """CLI entrypoint for counting the inventory of boards."""
    parser = argparse.ArgumentParser(description="Check the state of the boards")
    cfg.config_arg(parser)
    chk.check_filter_args(parser)
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()
    kwargs = vars(args)
    print_json = kwargs.pop("json")

    (available, used, missing, total) = chk.get_inventory_nodes(**kwargs)

    a_boards = chk.nodes_to_boards(available)
    u_boards = chk.nodes_to_boards(used)
    m_boards = chk.nodes_to_boards(missing)
    t_boards = chk.nodes_to_boards(total)

    boards = sorted(list(set(t_boards.keys())))

    info = [
        {
            "board": key,
            "available": a_boards.get(key, 0),
            "used": u_boards.get(key, 0),
            "missing": m_boards.get(key, 0),
            "total": t_boards.get(key, 0),
        }
        for key in boards
    ]
    if print_json:
        out = json.dumps(info, indent=2, sort_keys=True)
        print(out)
    elif len(info) > 0:
        # Get the longest str len of boards
        max_board_len = max([len(i["board"]) for i in info])
        brd_str = f"| {'Board':<{max_board_len + 1}}"
        avl_str = f"| {'Available':<10}"
        use_str = f"| {'Used':<10}"
        mis_str = f"| {'Missing':<10}"
        tot_str = f"| {'Total':<10}|"
        full_str = brd_str + avl_str + use_str + mis_str + tot_str
        print("-" * len(full_str))
        print(full_str)
        print("-" * len(full_str))
        avail_count = 0
        used_count = 0
        missing_count = 0
        total_count = 0
        for i in info:
            brd_str = f"| {i['board']:<{max_board_len + 1}}"
            avl_str = f"| {i['available']:>9} "
            use_str = f"| {i['used']:>9} "
            mis_str = f"| {i['missing']:>9} "
            tot_str = f"| {i['total']:>9} |"
            full_str = brd_str + avl_str + use_str + mis_str + tot_str
            print(full_str)

            avail_count += i["available"]
            used_count += i["used"]
            missing_count += i["missing"]
            total_count += i["total"]
        print("-" * len(full_str))
        brd_str = "| " + " " * (max_board_len + 1)
        avl_str = f"| {avail_count:>9} "
        use_str = f"| {used_count:>9} "
        mis_str = f"| {missing_count:>9} "
        tot_str = f"| {total_count:>9} |"
        full_str = brd_str + avl_str + use_str + mis_str + tot_str
        print(full_str)
        print("-" * len(full_str))


if __name__ == "__main__":
    main()
