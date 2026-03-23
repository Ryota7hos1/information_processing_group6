import time
import random
import threading
from decimal import Decimal

import boto3
from pynq import Overlay, MMIO
from ipywidgets import Button, VBox, HBox, Output, SelectMultiple, Label
from IPython.display import display, clear_output

# =============================================================
# Per-board config
# =============================================================

THIS_PLAYER      = 1     
AUTO_REFRESH_SEC = 0.25 #This can be modified to change responsiveness or stability

TABLE_NAME = "BattleTable"
GAME_ID    = "GAME_0001"

TURN_TIMEOUT_MS   = 15000
SHIELD_TIMEOUT_MS = 10000

# =============================================================
# Stop any older poll thread if this cell/script is re-run
# =============================================================

try:
    _stop_poll = True
    time.sleep(0.3)
except NameError:
    pass

_stop_poll = False

# =============================================================
# Overlay + MMIO
# =============================================================

overlay = Overlay("pg_block_sprite_t35.bit")
IP_BASE = 0x43C00000
mmio    = MMIO(IP_BASE, 0x1000)

CTRL      = 0x00
STATE_IN  = [0x04, 0x08, 0x0C, 0x10]
STATE_OUT = [0x14, 0x18, 0x1C, 0x20]

# Actions (must match battle_engine)
ACTION_ATTACK  = 0
ACTION_SPECIAL = 1
ACTION_SWITCH  = 2
ACTION_RESOLVE = 3

POKEMON_STATS = {
    0: {"name": "Dragonite",    "hp": 100, "atk": 15, "special": 40, "cost": 50},
    1: {"name": "Venusaur",  "hp": 105, "atk": 14, "special": 38, "cost": 45},
    2: {"name": "Charzard", "hp": 110, "atk": 18, "special": 45, "cost": 60},
    3: {"name": "Blastoise",   "hp": 120, "atk": 12, "special": 35, "cost": 40},
}

# =============================================================
# DynamoDB
# =============================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id="********************",
    aws_secret_access_key="**************************"
)
table = dynamodb.Table(TABLE_NAME)

# =============================================================
# Utility functions
# =============================================================

def write_display_state(item):
    state = pack_state(item)
    for i in range(4):
        mmio.write(STATE_IN[i], (state >> (32 * i)) & 0xFFFFFFFF)

def now_ms() -> int:
    return int(time.time() * 1000)

def deep_intify(x):
    if isinstance(x, Decimal):
        return int(x)
    if isinstance(x, dict):
        return {k: deep_intify(v) for k, v in x.items()}
    if isinstance(x, list):
        return [deep_intify(v) for v in x]
    return x

def fmt_state128_hex(state_int: int) -> str:
    return "0x%032X" % (state_int & ((1 << 128) - 1))

def winner_text(w):
    return {0: "None", 1: "Player 0", 2: "Player 1"}.get(w, f"Unknown({w})")

def state_signature(item):
    return (
        item["phase"],
        item["game_over"],
        item["winner"],
        item["player_turn"],
        item["pending_special"]["active"],
        item["pending_special"]["attacker"],
        item["pending_special"]["shield_used"],
        item["pending_special"]["defender_responded"],
        item.get("updated_at_ms", 0),
        item.get("packed_state_128", ""),
    )

def log_latency(msg: str):
    with debug_out:
        print(msg)

# =============================================================
# DB IO
# =============================================================

def load_game():
    t0 = time.perf_counter_ns()
    r  = table.get_item(Key={"GameID": GAME_ID})
    t1 = time.perf_counter_ns()
    item = deep_intify(r["Item"])
    return item, (t1 - t0)

def save_game(item):
    ms = now_ms()
    if item.get("created_at_ms", 0) == 0:
        item["created_at_ms"] = ms
    item["updated_at_ms"] = ms

    try:
        state_int = pack_state(item)
        item["packed_state_128"] = fmt_state128_hex(state_int)
    except Exception:
        pass

    t0 = time.perf_counter_ns()
    table.put_item(Item=item)
    t1 = time.perf_counter_ns()
    return (t1 - t0)

# =============================================================
# 128-bit pack/unpack
# =============================================================

def pack_state(item) -> int:
    state = 0
    state |= (item["game_over"] & 1) << 127
    state |= (item["winner"] & 3) << 125
    state |= (item["player_turn"] & 1) << 124

    ps = item["pending_special"]
    state |= (ps["active"] & 1) << 123
    state |= (ps["attacker"] & 1) << 122
    state |= (ps["shield_used"] & 1) << 121

    def pack_player(p_battle) -> int:
        block = 0
        block |= (p_battle["shields"] & 3) << 56
        block |= (p_battle["active_index"] & 3) << 54
        for i, slot in enumerate(p_battle["slots"]):
            base = 36 - i * 18
            block |= (slot["pokemon_id"] & 3) << (base + 16)
            block |= (slot["hp"] & 0xFF) << (base + 8)
            block |= (slot["energy"] & 0xFF) << base
        return block

    p0 = item["players"]["0"]["battle"]
    p1 = item["players"]["1"]["battle"]
    state |= pack_player(p0) << 60
    state |= pack_player(p1) << 0
    return state

def unpack_state(state: int, item):
    item["game_over"]   = (state >> 127) & 1
    item["winner"]      = (state >> 125) & 3
    item["player_turn"] = (state >> 124) & 1

    ps = item["pending_special"]
    ps["active"]      = (state >> 123) & 1
    ps["attacker"]    = (state >> 122) & 1
    ps["shield_used"] = (state >> 121) & 1

    def unpack_player(off_bits, p_battle):
        block = (state >> off_bits) & ((1 << 60) - 1)
        p_battle["shields"]      = (block >> 56) & 3
        p_battle["active_index"] = (block >> 54) & 3
        for i in range(3):
            base = 36 - i * 18
            slot = p_battle["slots"][i]
            slot["pokemon_id"] = (block >> (base + 16)) & 3
            slot["hp"]         = (block >> (base + 8)) & 0xFF
            slot["energy"]     = (block >> base) & 0xFF

    unpack_player(60, item["players"]["0"]["battle"])
    unpack_player(0,  item["players"]["1"]["battle"])

# =============================================================
# FPGA call
# =============================================================

def run_fpga(state: int, action: int, switch_idx: int, this_player: int):
    t0 = time.perf_counter_ns()

    for i in range(4):
        mmio.write(STATE_IN[i], (state >> (32 * i)) & 0xFFFFFFFF)

    ctrl = ((action & 3) << 2) | ((switch_idx & 3) << 4) | ((this_player & 1) << 8)

    mmio.write(CTRL, ctrl | (1 << 1))
    mmio.write(CTRL, ctrl)
    mmio.write(CTRL, ctrl | 1)
    mmio.write(CTRL, ctrl)

    while ((mmio.read(CTRL) >> 1) & 1) == 0:
        pass

    out = 0
    for i in range(4):
        out |= (mmio.read(STATE_OUT[i]) & 0xFFFFFFFF) << (32 * i)

    mmio.write(CTRL, ctrl | (1 << 1))
    mmio.write(CTRL, ctrl)

    t1 = time.perf_counter_ns()
    return out, (t1 - t0)

# =============================================================
# Initialisation + flow helpers
# =============================================================

def both_locked(item) -> bool:
    return (
        item["players"]["0"]["team_select"]["locked"] == 1 and
        item["players"]["1"]["team_select"]["locked"] == 1
    )

def init_battle_from_team_select(item):
    # Keep random first turn, but boards themselves are hardcoded by THIS_PLAYER
    item["player_turn"] = random.randint(0, 1)
    item["turn_started_at_ms"] = now_ms()

    ps = item["pending_special"]
    ps["active"] = 0
    ps["attacker"] = 0
    ps["shield_used"] = 0
    ps["defender_responded"] = 0
    ps["timestamp_ms"] = 0

    for pid in ["0", "1"]:
        chosen = item["players"][pid]["team_select"]["chosen_ids"]
        battle = item["players"][pid]["battle"]

        battle["shields"] = 2
        battle["active_index"] = 0

        for i in range(3):
            pokemon_id = int(chosen[i])
            battle["slots"][i]["pokemon_id"] = pokemon_id
            battle["slots"][i]["hp"] = POKEMON_STATS[pokemon_id]["hp"]
            battle["slots"][i]["energy"] = 0

    item["phase"] = "IN_BATTLE"
    item["game_over"] = 0
    item["winner"] = 0

def alive_bench_slots(item, pid: str):
    battle = item["players"][pid]["battle"]
    active = battle["active_index"]
    return [i for i, s in enumerate(battle["slots"]) if i != active and s["hp"] > 0]

def active_energy_and_cost(item, pid: str):
    battle = item["players"][pid]["battle"]
    aidx = battle["active_index"]
    slot = battle["slots"][aidx]
    pid_ = slot["pokemon_id"]
    return slot["energy"], POKEMON_STATS[pid_]["cost"]

def active_hp(item, pid: str):
    battle = item["players"][pid]["battle"]
    return battle["slots"][battle["active_index"]]["hp"]

def auto_switch_on_timeout(item) -> bool:
    turn = item["player_turn"]
    pid = str(turn)

    battle = item["players"][pid]["battle"]
    aidx = battle["active_index"]
    if battle["slots"][aidx]["hp"] > 0:
        return False

    bench = alive_bench_slots(item, pid)
    if len(bench) == 0:
        return False

    battle["active_index"] = int(bench[0])
    item["player_turn"] ^= 1
    item["turn_started_at_ms"] = now_ms()
    return True

# =============================================================
# Timeouts
# =============================================================

def compute_turn_remaining_ms(item):
    if item["phase"] != "IN_BATTLE" or item["game_over"] == 1:
        return None
    elapsed = now_ms() - item.get("turn_started_at_ms", 0)
    return max(0, TURN_TIMEOUT_MS - elapsed)

def apply_turn_timeout_pass(item):
    rem = compute_turn_remaining_ms(item)
    if rem is None:
        return False
    if rem == 0:
        item["player_turn"] ^= 1
        item["turn_started_at_ms"] = now_ms()
        return True
    return False

# =============================================================
# UI widgets
# =============================================================

state_out = Output()
debug_out = Output()

title = Label(f"Pokémon FPGA Battle (Board = Player {THIS_PLAYER})")
timer_label = Label("")
refresh_btn = Button(description="Refresh", button_style="info")

restart_btn = Button(description="Restart Game", button_style="info")
forfeit_btn = Button(description=f"Forfeit P{THIS_PLAYER}", button_style="danger")

p0_select = SelectMultiple(
    options=[(f"{POKEMON_STATS[i]['name']} ({i})", i) for i in range(4)],
    description="P0 picks",
)
p1_select = SelectMultiple(
    options=[(f"{POKEMON_STATS[i]['name']} ({i})", i) for i in range(4)],
    description="P1 picks",
)

lock_p0_btn = Button(description="Lock P0 Team", button_style="warning")
lock_p1_btn = Button(description="Lock P1 Team", button_style="warning")

attack_btn  = Button(description="Attack", button_style="success")
special_btn = Button(description="Special", button_style="success")

shield_btn    = Button(description="Use Shield", button_style="warning")
no_shield_btn = Button(description="No Shield", button_style="warning")

switch_box = HBox([])
controls_box = VBox([])

ui_lock = threading.Lock()
last_item = None
_last_sig = None

# =============================================================
# State printout
# =============================================================

def print_state(item):
    print(
        f"\nGameID: {GAME_ID} | phase={item['phase']} | turn=P{item['player_turn']} "
        f"| game_over={item['game_over']} winner={winner_text(item['winner'])}"
    )
    ps = item["pending_special"]
    print(
        f"pending_special: active={ps['active']} attacker=P{ps['attacker']} "
        f"shield_used={ps.get('shield_used', 0)} defender_responded={ps.get('defender_responded', 0)}"
    )
    for pid in ["0", "1"]:
        battle = item["players"][pid]["battle"]
        print(f"\nPlayer {pid}: shields={battle['shields']} active={battle['active_index']}")
        for i, s in enumerate(battle["slots"]):
            name = POKEMON_STATS[s["pokemon_id"]]["name"]
            tag = "<ACTIVE>" if i == battle["active_index"] else ""
            faint = "(fainted)" if s["hp"] == 0 else ""
            print(f"  Slot{i}: {name} id={s['pokemon_id']} HP={s['hp']} EN={s['energy']} {faint} {tag}")

# =============================================================
# Game reset / forfeit
# =============================================================

def reset_game():
    with ui_lock:
        item, _ = load_game()

        item["phase"] = "TEAM_SELECT"
        item["game_over"] = 0
        item["winner"] = 0
        item["player_turn"] = 0
        item["turn_started_at_ms"] = 0

        ps = item["pending_special"]
        ps["active"] = 0
        ps["attacker"] = 0
        ps["shield_used"] = 0
        ps["defender_responded"] = 0
        ps["timestamp_ms"] = 0

        for pid in ["0", "1"]:
            item["players"][pid]["team_select"]["locked"] = 0
            item["players"][pid]["team_select"]["chosen_ids"] = []
            battle = item["players"][pid]["battle"]
            battle["shields"] = 2
            battle["active_index"] = 0
            for i in range(3):
                battle["slots"][i]["pokemon_id"] = 0
                battle["slots"][i]["hp"] = 0
                battle["slots"][i]["energy"] = 0

        item["packed_state_128"] = "0x00000000000000000000000000000000"
        save_game(item)
        write_display_state(item)

    with debug_out:
        clear_output()
        print("Restarted game (DB reset).")

def forfeit(player_id: int):
    with ui_lock:
        item, _ = load_game()
        item["game_over"] = 1
        item["winner"] = 2 if player_id == 0 else 1
        item["phase"] = "GAME_OVER"
        save_game(item)
        write_display_state(item)
        log_latency(f"FORFEIT: P{player_id} forfeited -> winner={winner_text(item['winner'])}")

# =============================================================
# Render
# =============================================================

def render(item):
    children = []

    top = [refresh_btn, restart_btn, forfeit_btn]
    children.append(HBox(top))

    if item["phase"] == "TEAM_SELECT":
        my_pid = str(THIS_PLAYER)
        my_locked = item["players"][my_pid]["team_select"]["locked"]

        children.append(Label(f"TEAM_SELECT: You are Player {THIS_PLAYER}. Pick 3 Pokémon and lock your team."))

        my_select = p0_select if THIS_PLAYER == 0 else p1_select
        my_lock_btn = lock_p0_btn if THIS_PLAYER == 0 else lock_p1_btn
        my_lock_btn.disabled = bool(my_locked)

        if my_locked:
            children.append(Label("Your team is locked. Waiting for the other player..."))
        else:
            children.append(HBox([my_select, my_lock_btn]))

        if both_locked(item):
            children.append(Label("Both teams locked. Starting battle..."))

        controls_box.children = children
        return

    if item["phase"] == "GAME_OVER" or item["game_over"] == 1:
        children.append(Label(f"GAME OVER — Winner: {winner_text(item['winner'])}"))
        controls_box.children = children
        return

    if item["phase"] == "PENDING_SPECIAL":
        ps = item["pending_special"]
        attacker = ps["attacker"]
        defender = 1 - attacker

        if THIS_PLAYER == defender:
            children.append(Label("Opponent used a special attack. Use a shield?"))
            d_shields = item["players"][str(defender)]["battle"]["shields"]
            shield_btn.disabled = (d_shields == 0)
            children.append(HBox([shield_btn, no_shield_btn]))
        else:
            children.append(Label(f"Waiting for Player {defender} to respond to the special attack..."))

        controls_box.children = children
        return

    if item["phase"] == "IN_BATTLE":
        turn = item["player_turn"]
        my_pid = str(THIS_PLAYER)

        if turn != THIS_PLAYER:
            children.append(Label(f"Waiting for Player {turn}..."))
            controls_box.children = children
            return

        children.append(Label("It is your turn."))

        hp = active_hp(item, my_pid)
        active_alive = (hp > 0)

        en, cost = active_energy_and_cost(item, my_pid)
        special_btn.disabled = (not active_alive) or (en < cost)
        attack_btn.disabled  = (not active_alive)

        bench = alive_bench_slots(item, my_pid)
        switch_buttons = []
        for idx in bench:
            b = Button(description=f"Switch → Slot{idx}", button_style="primary")
            b.on_click(lambda _b, t=idx: do_fpga_action(ACTION_SWITCH, t))
            switch_buttons.append(b)
        switch_box.children = switch_buttons

        if not active_alive:
            children.append(Label("Your active Pokémon fainted — you must switch."))

        children.append(HBox([attack_btn, special_btn]))
        if len(switch_buttons) > 0:
            children.append(Label("Switch options:"))
            children.append(switch_box)

        controls_box.children = children
        return

    children.append(Label(f"Unknown phase: {item['phase']}"))
    controls_box.children = children

# =============================================================
# Core action helpers
# =============================================================

def postprocess_after_fpga(item, action):
    ms = now_ms()

    if item["game_over"] == 1:
        item["phase"] = "GAME_OVER"
        return

    if action == ACTION_SPECIAL and item["pending_special"]["active"] == 1:
        item["phase"] = "PENDING_SPECIAL"
        item["pending_special"]["shield_used"] = 0
        item["pending_special"]["defender_responded"] = 0
        item["pending_special"]["timestamp_ms"] = ms

    if action in (ACTION_ATTACK, ACTION_SWITCH, ACTION_RESOLVE):
        item["turn_started_at_ms"] = ms

    if item["pending_special"]["active"] == 0 and item["phase"] != "TEAM_SELECT":
        item["phase"] = "IN_BATTLE"

def run_and_commit_fpga_action_locked(item, action, switch_idx, acting_player, db_read_ns=0):
    state_in = pack_state(item)
    state_out_int, hw_ns = run_fpga(state_in, action, switch_idx, acting_player)
    unpack_state(state_out_int, item)
    postprocess_after_fpga(item, action)
    db_write_ns = save_game(item)
    write_display_state(item)

    e2e_ns = db_read_ns + hw_ns + db_write_ns
    log_latency(
        f"LATENCY: action={action} player={acting_player} "
        f"db_read={db_read_ns} ns, hw={hw_ns} ns, db_write={db_write_ns} ns, sum~={e2e_ns} ns"
    )
    return item

# =============================================================
# User-triggered actions
# =============================================================

def do_fpga_action(action, switch_idx=0):
    global last_item

    with ui_lock:
        item, db_read_ns = load_game()

        if item["phase"] == "PENDING_SPECIAL":
            with state_out:
                clear_output()
                print("Pending special in progress. Waiting for defender response / resolve.")
            return

        if item["phase"] != "IN_BATTLE":
            with state_out:
                clear_output()
                print("Not in IN_BATTLE.")
            return

        if item["game_over"] == 1:
            with state_out:
                clear_output()
                print("Game is over.")
            return

        if item["player_turn"] != THIS_PLAYER:
            with state_out:
                clear_output()
                print(f"It is not your turn. Waiting for Player {item['player_turn']}.")
            return

        item = run_and_commit_fpga_action_locked(item, action, switch_idx, THIS_PLAYER, db_read_ns=db_read_ns)
        last_item = item

        with state_out:
            clear_output()
            print_state(item)

    render(item)

def set_defender_shield(use_shield: int):
    global last_item

    with ui_lock:
        item, db_read_ns = load_game()

        if item["phase"] != "PENDING_SPECIAL":
            with state_out:
                clear_output()
                print("Not in PENDING_SPECIAL.")
            return

        ps = item["pending_special"]
        attacker = ps["attacker"]
        defender = 1 - attacker

        if THIS_PLAYER != defender:
            with state_out:
                clear_output()
                print("This board is not the defending player.")
            return

        if use_shield == 1:
            d_shields = item["players"][str(defender)]["battle"]["shields"]
            if d_shields == 0:
                use_shield = 0

        ps["shield_used"] = 1 if use_shield else 0
        ps["defender_responded"] = 1
        db_write_ns = save_game(item)
        write_display_state(item)
        last_item = item

        log_latency(
            f"SHIELD_DECISION: defender=P{defender} use_shield={use_shield} "
            f"(db_read={db_read_ns} ns, db_write={db_write_ns} ns)"
        )

        with state_out:
            clear_output()
            print_state(item)

    render(item)

# =============================================================
# Refresh helpers
# =============================================================

def refresh(_btn=None):
    global last_item
    item, _ = load_game()
    last_item = item
    write_display_state(item)

    rem = compute_turn_remaining_ms(item)
    if rem is None:
        timer_label.value = ""
    else:
        timer_label.value = f"Turn timer: {rem/1000:.1f}s"

    with state_out:
        clear_output()
        print_state(item)

    render(item)

# =============================================================
# Button wiring
# =============================================================

refresh_btn.on_click(refresh)
attack_btn.on_click(lambda _b: do_fpga_action(ACTION_ATTACK, 0))
special_btn.on_click(lambda _b: do_fpga_action(ACTION_SPECIAL, 0))

shield_btn.on_click(lambda _b: set_defender_shield(1))
no_shield_btn.on_click(lambda _b: set_defender_shield(0))

restart_btn.on_click(lambda _b: (reset_game(), refresh()))
forfeit_btn.on_click(lambda _b: (forfeit(THIS_PLAYER), refresh()))

def lock_team(pid: str, picked):
    global last_item

    if int(pid) != THIS_PLAYER:
        with state_out:
            clear_output()
            print("This board can only lock its own team.")
        return

    with ui_lock:
        item, _ = load_game()

        picked = list(picked)
        if len(picked) != 3 or len(set(picked)) != 3:
            with state_out:
                clear_output()
                print("Pick exactly 3 distinct Pokémon.")
            return

        item["players"][pid]["team_select"]["chosen_ids"] = [int(x) for x in picked]
        item["players"][pid]["team_select"]["locked"] = 1
        save_game(item)
        write_display_state(item)
        last_item = item

        log_latency(f"TEAM_LOCK: P{pid} locked {picked}")

    refresh()

lock_p0_btn.on_click(lambda _b: lock_team("0", p0_select.value))
lock_p1_btn.on_click(lambda _b: lock_team("1", p1_select.value))

# =============================================================
# Display
# =============================================================

display(VBox([
    title,
    timer_label,
    state_out,
    controls_box,
    Label("Latency log (persistent):"),
    debug_out,
]))

refresh()

# =============================================================
# Poll thread:
# - auto refreshes the board from DynamoDB
# - P0 initialises battle once both teams are locked
# - attacker board auto-resolves special once defender responds
# - attacker board also handles shield timeout as no-shield
# - current-turn board handles turn timeout
# =============================================================

def _poll_loop():
    global last_item, _last_sig, _stop_poll

    while not _stop_poll:
        try:
            rerender_item = None

            with ui_lock:
                item, db_read_ns = load_game()

                # -------------------------------------------------
                # Auto-start battle once both teams are locked
                # Only P0 board performs this to avoid race
                # -------------------------------------------------
                if item["phase"] == "TEAM_SELECT" and both_locked(item):
                    if THIS_PLAYER == 0:
                        init_battle_from_team_select(item)
                        save_game(item)
                        item, _ = load_game()

                # -------------------------------------------------
                # Pending special handling:
                # attacker board resolves after defender responds
                # attacker board also applies timeout -> no shield
                # -------------------------------------------------
                if item["phase"] == "PENDING_SPECIAL" and item["game_over"] == 0:
                    ps = item["pending_special"]
                    attacker = ps["attacker"]

                    if THIS_PLAYER == attacker:
                        if ps["active"] == 1 and ps.get("defender_responded", 0) == 0:
                            if (now_ms() - ps.get("timestamp_ms", 0)) >= SHIELD_TIMEOUT_MS:
                                ps["shield_used"] = 0
                                ps["defender_responded"] = 1
                                save_game(item)
                                log_latency("TIMEOUT: shield -> auto no-shield")

                        if ps["active"] == 1 and ps.get("defender_responded", 0) == 1:
                            item = run_and_commit_fpga_action_locked(
                                item,
                                ACTION_RESOLVE,
                                0,
                                attacker,
                                db_read_ns=db_read_ns
                            )
                            log_latency(f"RESOLVE: attacker board P{attacker} resolved pending special")

                # -------------------------------------------------
                # Turn timeout handling:
                # only current-turn board mutates DB
                # -------------------------------------------------
                if item["phase"] == "IN_BATTLE" and item["game_over"] == 0:
                    rem = compute_turn_remaining_ms(item)
                    if rem == 0 and item["player_turn"] == THIS_PLAYER:
                        if auto_switch_on_timeout(item):
                            save_game(item)
                            log_latency("TIMEOUT: active fainted -> AUTO-SWITCH + FLIP")
                        else:
                            if apply_turn_timeout_pass(item):
                                save_game(item)
                                log_latency("TIMEOUT: turn -> PASS")
                        item, _ = load_game()

                last_item = item
                write_display_state(item)

                rem = compute_turn_remaining_ms(item)
                if rem is None:
                    timer_label.value = ""
                else:
                    timer_label.value = f"Turn timer: {rem/1000:.1f}s"

                sig = state_signature(item)
                if sig != _last_sig:
                    _last_sig = sig
                    rerender_item = item

            if rerender_item is not None:
                with state_out:
                    clear_output()
                    print_state(rerender_item)
                render(rerender_item)

            time.sleep(AUTO_REFRESH_SEC)

        except Exception as e:
            with debug_out:
                print(f"Poll loop error: {e}")
            time.sleep(AUTO_REFRESH_SEC)

_poll_thread = threading.Thread(target=_poll_loop, daemon=True)
_poll_thread.start()
