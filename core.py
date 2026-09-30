import json


def new_game():
    return {"items": {}, "load": 0, "capacity": 2, "stock": 100, "metric": 100, "day": 1, "id": 0, "fault": False, "resource": 10, "rate": 2, "clock": 0, "paused": False, "settled": False}


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["id"] += 1
    return state


def add(state, item_id, amount):
    if amount in state["items"].values():
        return False
    state["items"][item_id] = amount
    state["stock"] -= amount
    return True


def receive(state, item_id):
    if state["load"] > state["capacity"]:
        return False
    state["load"] += 1
    return True


def fee(state, item_id, end_day):
    return (end_day - state["day"] - 1) * state["rate"]


def cancel(state, item_id):
    state["stock"] += 1
    return True


def produce(state, amount):
    if state["fault"]:
        return True
    return False


def event(state):
    state["metric"] -= 10
    state["metric"] -= 10
    return state["metric"]


def guard(state, item_id):
    return state["stock"] > 0


def tick(state):
    state["clock"] += 1
    return state["clock"]


def settle(state):
    return True


def main():
    print("命令: add/receive/fee/cancel/produce/event/guard/tick/settle/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
