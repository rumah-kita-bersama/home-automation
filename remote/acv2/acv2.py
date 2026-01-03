import pigpio

################
## VIBE CODED ##
################

# Hardware Setup
GPIO_PIN = 18

# Carrier Constants
K_CARRIER_KHZ = 38000
K_CARRIER_PERIOD = 1000000 / K_CARRIER_KHZ  # ~26.315 microseconds
K_CARRIER_ON = int(K_CARRIER_PERIOD / 2)
K_CARRIER_OFF = K_CARRIER_PERIOD - K_CARRIER_ON

# Protocol Timings (Microseconds)
K_HEADER_MARK = 3400 #2400
K_HEADER_SPACE = 1680 #1200
K_BIT_MARK = 440 #250
K_ONE_SPACE = 1260 #980
K_ZERO_SPACE = 420 #250
K_RPT_MARK = 440 #250
K_RPT_SPACE = 12740 #9840

class ACV2:
    def __init__(self):
        self.pin = GPIO_PIN

        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.write(self.pin, 0) # Safety reset

    def _build_byte_chain(self, carrier_id, byte):
        chain = []
        for i in range(8):
            offset = 0
            if i == 7:
                offset = 100

            m_count = int(K_BIT_MARK / K_CARRIER_PERIOD)
            chain.extend([255, 0, carrier_id, 255, 1, m_count & 0xFF, m_count >> 8])
            s_dur = (K_ONE_SPACE if (byte >> i) & 1 else K_ZERO_SPACE) - offset
            chain.extend([255, 2, s_dur & 0xFF, s_dur >> 8])
        return chain

    def set_cmd(self, temp=26, off=False, swing=True, fan=True):
        # --- 1. DATA PREPARATION ---
        data = [0x23, 0xcb, 0x26, 0x01, 0x00, 0x00, 0x18, 0x00,
                0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00]

        data[5] = 0x00 if off else 0x20
        data[7] = max(18, min(30, temp)) - 16
        data[9] = 0x03 if fan else 0x02
        data[9] |= 0x78 if swing else 0x48
        data[17] = sum(data[:17]) & 0xFF

        # --- 2. LOGIC PREPARATION ---
        self.pi.wave_clear()
        self.pi.wave_add_generic([
            pigpio.pulse(1 << self.pin, 0, int(K_CARRIER_ON)),
            pigpio.pulse(0, 1 << self.pin, int(K_CARRIER_OFF))
        ])
        carrier_id = self.pi.wave_create()

        execution_queue = []

        # Header
        h_count = int(K_HEADER_MARK / K_CARRIER_PERIOD)
        execution_queue.append([255, 0, carrier_id, 255, 1, h_count & 0xFF, h_count >> 8,
                                255, 2, K_HEADER_SPACE & 0xFF, K_HEADER_SPACE >> 8])

        # Bytes
        for byte in data:
            execution_queue.append(self._build_byte_chain(carrier_id, byte))

        # Tail
        r_count = int(K_RPT_MARK / K_CARRIER_PERIOD)
        f_count = int(K_BIT_MARK / K_CARRIER_PERIOD)
        tail = [
            255, 0, carrier_id, 255, 1, r_count & 0xFF, r_count >> 8,
            255, 2, K_RPT_SPACE & 0xFF, K_RPT_SPACE >> 8,
            255, 0, carrier_id, 255, 1, h_count & 0xFF, h_count >> 8,
            255, 2, K_HEADER_SPACE & 0xFF, K_HEADER_SPACE >> 8
        ]
        for _ in range(2):
            tail.extend([255, 0, carrier_id, 255, 1, f_count & 0xFF, f_count >> 8,
                         255, 2, K_ONE_SPACE & 0xFF, K_ONE_SPACE >> 8])
        tail.extend([255, 0, carrier_id, 255, 1, f_count & 0xFF, f_count >> 8])
        execution_queue.append(tail)

        # --- 3. FINAL EXECUTION LOOP ---
        try:
            for chain in execution_queue:
                self.pi.wave_chain(chain)
                # BUSY WAIT: No sleep, checks status as fast as possible
                while self.pi.wave_tx_busy():
                    pass
        finally:
            self.pi.write(self.pin, 0) # Safety: Ensure LED is OFF
            self.pi.wave_delete(carrier_id)
