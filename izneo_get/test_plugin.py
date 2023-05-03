import os
import importlib
import sys

to_test = "titi"
parser = None
# Load all modules in the plugin directory.
for module in os.listdir(f"{os.path.dirname(__file__)}/plugins"):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    # __import__(f'plugins.{module[:-3]}', locals(), globals())
    module = importlib.import_module(f"plugins.{module[:-3]}")
    parser = module.init()
    if parser.is_valid_url(to_test):
        break
    else:
        parser = None

if parser is None:
    sys.exit("No parser found for this URL")

parser.download()
