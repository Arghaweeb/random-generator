class ControlLoop:
    def __init__(self):
        self.state = "IDLE"
        self.mode = "always_on"
        self.surplus_allowed = True

    def is_allowed_to_generate(self) -> bool:
        if self.mode == "manual":
            return self.state == "GENERATING"
        if self.mode == "surplus_only":
            return self.surplus_allowed
        return True

    def update_from_server(self, control: dict | None) -> None:
        if not control:
            return

        if "surplus_allowed" in control:
            self.surplus_allowed = control["surplus_allowed"]

        if "target_state" in control:
            target = control["target_state"]
            if target in ("IDLE", "GENERATING", "ERROR"):
                self.state = target
