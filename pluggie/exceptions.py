class PluggieError(Exception):
    pass


class SignatureError(PluggieError):
    pass


class PluginLoadError(PluggieError):
    pass


class EventTriggerError(PluggieError):
    pass
