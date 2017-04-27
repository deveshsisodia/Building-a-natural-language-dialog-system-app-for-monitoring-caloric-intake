

class DialogTracer:
    def __init__(self, enable_sys_msg=False):
        self.enable_sys = enable_sys_msg

    # Print system message to console
    def sys_msg(self, message):
        if self.enable_sys:
            print("\n[SYSTEM]:")
            print(message)