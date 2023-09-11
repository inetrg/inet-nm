import argparse
import hashlib
import json
import tempfile

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

    # Possibly assert uids are unique for each available, used, missing
    uid_states = {}
    uid_states.update({node.uid: "available" for node in available})
    uid_states.update({node.uid: "used" for node in used})
    uid_states.update({node.uid: "missing" for node in missing})

    # get hash of tempfile name based on config path
    cfg_path = args.config
    cfg_hash = hashlib.md5(str(cfg_path).encode()).hexdigest()
    tmp_state_path = (
        tempfile.gettempdir() + "/" + "inet-nm-uid-states-" + cfg_hash + ".json"
    )
    tmp_changes_path = (
        tempfile.gettempdir() + "/" + "inet-nm-changes-" + cfg_hash + ".json"
    )

    # Try to read from tempfile if it exists for old uid_states
    try:
        with open(tmp_state_path, "r") as f:
            old_uid_states = json.load(f)
    except FileNotFoundError:
        old_uid_states = {}

    # If any old states differ from new states add to a changes state dict
    changes = {}
    board_changes = {}
    new_uids = set(uid_states.keys()) - set(old_uid_states.keys())
    for uid in new_uids:
        changes[uid] = uid_states[uid]
        # get board from uid
        board = [node.board for node in total if node.uid == uid][0]
        b_key = f"{board}_{uid_states[uid]}"
        if b_key not in board_changes:
            board_changes[b_key] = 0
        board_changes[b_key] += 1

    x_uids = set(uid_states.keys()).intersection(set(old_uid_states.keys()))
    for uid in x_uids:
        if uid_states[uid] != old_uid_states[uid]:
            changes[uid] = uid_states[uid]
            # get board from uid
            board = [node.board for node in total if node.uid == uid][0]
            b_key = f"{board}_{uid_states[uid]}"
            if b_key not in board_changes:
                board_changes[b_key] = 0
            board_changes[f"{board}_{uid_states[uid]}"] += 1
            b_key = f"{board}_{old_uid_states[uid]}"
            if b_key not in board_changes:
                board_changes[b_key] = 0
            board_changes[f"{board}_{old_uid_states[uid]}"] -= 1

    # Write new uid_states to tempfile
    if changes:
        with open(tmp_state_path, "w") as f:
            json.dump(uid_states, f, sort_keys=True, indent=2)
            if not print_json:
                print(f"Updated uid_states written to {tmp_state_path}")
        with open(tmp_changes_path, "w") as f:
            json.dump(board_changes, f, sort_keys=True, indent=2)
            if not print_json:
                print(f"Updated changes written to {tmp_changes_path}")
    else:
        try:
            with open(tmp_changes_path, "r") as f:
                board_changes = json.load(f)
        except FileNotFoundError:
            board_changes = {}

    boards = sorted(list(set(t_boards.keys())))

    info = [
        {
            "board": key,
            "available": a_boards.get(key, 0),
            "used": u_boards.get(key, 0),
            "missing": m_boards.get(key, 0),
            "total": t_boards.get(key, 0),
            "available_changes": board_changes.get(f"{key}_available", 0),
            "used_changes": board_changes.get(f"{key}_used", 0),
            "missing_changes": board_changes.get(f"{key}_missing", 0),
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
            state = " "
            if i["available_changes"] > 0:
                state = "+"
            elif i["available_changes"] < 0:
                state = "-"
            avl_str = f"|{state}{i['available']:>9} "
            state = " "
            if i["used_changes"] > 0:
                state = "+"
            elif i["used_changes"] < 0:
                state = "-"
            use_str = f"|{state}{i['used']:>9} "
            state = " "
            if i["missing_changes"] > 0:
                state = "+"
            elif i["missing_changes"] < 0:
                state = "-"
            mis_str = f"|{state}{i['missing']:>9} "
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
