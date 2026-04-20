class Tradfri:
    def __init__(self, host, identity, psk):
        api_factory = APIFactory(host=host, psk_id=identity, psk=psk)
        self.request = api_factory.request
        self.gateway = Gateway()

        self._light_cache = {}

    def set_light_dimmer_value(self, light_id, value):
        light = self._get_light(light_id)
        cmd = light.light_control.set_dimmer(value)
        self.request(cmd)

    def _get_light(self, id):
        light = self._light_cache.get(id)
        if light:
            return light

        devices_command = self.gateway.get_devices()
        devices_commands = self.request(devices_command)
        devices = self.request(devices_commands)
        for device in devices:
            if device.has_light_control:
                self._light_cache[device.id] = device

        return self._light_cache.get(id)