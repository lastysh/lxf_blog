import config_default


configs = config_default.configs


def merge(cod, coo):
	try:
		conf = cod + coo
		return conf
	except TypeError:
		return coo

try:
	import config_override
	configs = merge(configs, config_override.configs)
except ImportError:
	pass