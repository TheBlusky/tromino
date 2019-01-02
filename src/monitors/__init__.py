import os

module = None
for module in os.listdir(f"{os.path.dirname(__file__)}/implems/"):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    __import__(f"monitors.implems.{module[:-3]}", locals(), globals())
if module:
    del module


def load_monitors():
    from monitors.implems import all_monitors

    return all_monitors
