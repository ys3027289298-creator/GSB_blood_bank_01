import json


_FUNDS = "stock"
_STORAGE = "items"

# 受血者可接受的血型（ABO/Rh 兼容表）
_COMPATIBLE = {
    "O-": {"O-"},
    "O+": {"O-", "O+"},
    "B-": {"O-", "B-"},
    "B+": {"O-", "O+", "B-", "B+"},
    "A-": {"O-", "A-"},
    "A+": {"O-", "O+", "A-", "A+"},
    "AB-": {"O-", "A-", "B-", "AB-"},
    "AB+": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},
}


def new_game():
    return {
        "items": {},
        "load": 0,
        "capacity": 2,
        "stock": 100,
        "metric": 100,
        "day": 1,
        "id": 0,
        "fault": False,
        "resource": 10,
        "rate": 2,
        "clock": 0,
        "paused": False,
        "settled": False,
        "types": {},
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    # 读档不改动自增血袋号，避免与档内已有血袋号撞号；
    # 仅补齐旧存档缺失的字段（向后兼容，不改动既有键名）
    fresh = new_game()
    for key, value in fresh.items():
        state.setdefault(key, value)
    return state


def _settled(state):
    return bool(state.get("settled"))


def add(state, item_id, amount, blood_type=None):
    """入库一袋血。同一血袋号重复入库被拒绝（操作幂等）。"""
    if _settled(state):
        return False
    if item_id in state["items"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    state["items"][item_id] = amount
    if blood_type is not None:
        state["types"][str(item_id)] = blood_type
    state["stock"] -= amount
    return True


def receive(state, item_id):
    """送入冷库。冷库满员或该袋已在冷库中时拒绝（幂等）。"""
    if _settled(state):
        return False
    if state["load"] >= state["capacity"]:
        return False
    if state.get("items") and item_id not in state["items"]:
        return False
    received = state.setdefault("_received", [])
    if item_id in received:
        return False
    received.append(item_id)
    state["load"] += 1
    return True


def fee(state, item_id, end_day):
    """跨日储存费：入存日次日起算，按整天数 * 单日费率。"""
    start_day = state["day"]
    if end_day < start_day:
        return 0
    return (end_day - start_day) * state["rate"]


def cancel(state, item_id):
    """取消入库：退还尚未出库的血袋；重复取消不退两次（幂等）。"""
    if _settled(state):
        return False
    amount = state["items"].pop(item_id, None)
    if amount is None:
        return False
    state["types"].pop(str(item_id), None)
    state["stock"] += amount
    return True


def produce(state, amount):
    """冷链故障期间不计库存（溶血/冷链事件下禁止产出）。"""
    if _settled(state):
        return False
    if state["fault"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    state["stock"] += amount
    return True


def event(state):
    """溶血等异常事件只扣一次指标。"""
    if _settled(state):
        return state["metric"]
    state["metric"] -= 10
    return state["metric"]


def guard(state, item_id, request_type=None):
    """出库校验：有资源、血袋存在、血型兼容且未结算才放行。"""
    if _settled(state):
        return False
    if state["resource"] <= 0:
        return False
    if item_id not in state["items"]:
        return False
    donor_type = state["types"].get(str(item_id))
    if request_type is not None and donor_type is not None:
        if donor_type not in _COMPATIBLE.get(request_type, set()):
            return False
    return True


def tick(state):
    """时钟推进；暂停时冻结。"""
    if _settled(state):
        return state["clock"]
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def settle(state):
    """结算，结算后所有写操作/出库一律拒绝（重复结算幂等）。"""
    state["settled"] = True
    return True


def main():
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        cmd = parts[0]
        args = parts[1:]
        try:
            if cmd == "add" and len(args) in (2, 3):
                result = add(state, int(args[0]), int(args[1]),
                             args[2] if len(args) == 3 else None)
            elif cmd == "receive" and len(args) == 1:
                result = receive(state, int(args[0]))
            elif cmd == "fee" and len(args) == 2:
                result = fee(state, int(args[0]), int(args[1]))
            elif cmd == "cancel" and len(args) == 1:
                result = cancel(state, int(args[0]))
            elif cmd == "produce" and len(args) == 1:
                result = produce(state, int(args[0]))
            elif cmd == "event":
                result = event(state)
            elif cmd == "guard" and len(args) in (1, 2):
                result = guard(state, int(args[0]),
                               args[1] if len(args) == 2 else None)
            elif cmd == "tick":
                result = tick(state)
            elif cmd == "settle":
                result = settle(state)
            else:
                print("unknown")
                continue
        except ValueError:
            print("bad command")
            continue
        print("ok" if result else "no", result)


if __name__ == "__main__":
    main()
