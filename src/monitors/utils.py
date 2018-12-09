from monitors.implems import all_monitors


def monitor_register(name):
    def monitor_register_ret(original_class):
        all_monitors[name] = original_class
        return original_class

    return monitor_register_ret
