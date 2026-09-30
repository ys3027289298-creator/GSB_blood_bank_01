import json


def new_game():
    return {"items": {}, "load": 0, "capacity": 2, "stock": 100, "metric": 100, "day": 1, "id": 0, "fault": False, "resource": 10, "rate": 2, "clock": 0, "paused": False, "settled": False}


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    return json.loads(text)


def add(state, item_id, amount):
    if state["settled"]:
        return False
    if amount <= 0 or amount > state["stock"]:
        return False
    if item_id in state["items"]:
        return False
    state["items"][item_id] = amount
    state["stock"] -= amount
    return True


def receive(state, item_id):
    if state["settled"]:
        return False
    if state["load"] >= state["capacity"]:
        return False
    state["load"] += 1
    return True


def fee(state, item_id, end_day):
    days = end_day - state["day"]
    if days < 0:
        days = 0
    return days * state["rate"]


def cancel(state, item_id):
    if state["settled"]:
        return False
    amount = state["items"].pop(item_id, None)
    if amount is None:
        return False
    state["stock"] += amount
    return True


def produce(state, amount):
    if state["settled"] or state["fault"]:
        return False
    return True


def event(state):
    if state["settled"]:
        return state["metric"]
    state["metric"] -= 10
    return state["metric"]


def guard(state, item_id):
    if state["settled"]:
        return False
    if state["resource"] <= 0 or state["stock"] <= 0:
        return False
    return item_id in state["items"]


def tick(state):
    if state["paused"] or state["settled"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def settle(state):
    state["settled"] = True
    return True


def _parse_id(text):
    try:
        return int(text)
    except ValueError:
        return text


def main():
    state = new_game()
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "add":
                result = add(state, _parse_id(args[0]), int(args[1]))
            elif cmd == "receive":
                result = receive(state, _parse_id(args[0]))
            elif cmd == "fee":
                result = fee(state, _parse_id(args[0]), int(args[1]))
            elif cmd == "cancel":
                result = cancel(state, _parse_id(args[0]))
            elif cmd == "produce":
                result = produce(state, int(args[0]))
            elif cmd == "event":
                result = event(state)
            elif cmd == "guard":
                result = guard(state, _parse_id(args[0]))
            elif cmd == "tick":
                result = tick(state)
            elif cmd == "settle":
                result = settle(state)
            else:
                print("unknown command")
                continue
        except (IndexError, ValueError):
            print("bad arguments")
            continue
        print(result)


if __name__ == "__main__":
    main()
