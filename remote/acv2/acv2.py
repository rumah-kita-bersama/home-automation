import time
import pigpio

################
## VIBE CODED ##
################

# Hardware Setup
GPIO_PIN = 18

# Carrier Constants
K_CARRIER_KHZ = 38000
K_CARRIER_PERIOD = (1000.0 * 1000.0) / K_CARRIER_KHZ  # ~26.315 microseconds
K_CARRIER_ON = int(K_CARRIER_PERIOD / 2.0)
K_CARRIER_OFF = K_CARRIER_PERIOD - K_CARRIER_ON

# Protocol Timings (Microseconds)
K_HEADER_MARK = 3400
K_HEADER_SPACE = 1680
K_BIT_MARK = 440
K_ONE_SPACE = 1260
K_ZERO_SPACE = 420
K_RPT_MARK = 440
K_RPT_SPACE = 12740

class ACV2:
    def __init__(self):
        self.pin = GPIO_PIN

        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.write(self.pin, 0)
        self.pi.wave_clear()

        self._marks = {}
        self._spaces = {}
    
    def _generate_mark(self, t):
        cycles = int(round(t / K_CARRIER_PERIOD))
        waveforms = []
        for c in range(cycles):
            waveforms.append(pigpio.pulse(1 << self.pin, 0, int(K_CARRIER_ON)))
            waveforms.append(pigpio.pulse(0, 1 << self.pin, int(K_CARRIER_OFF)))
        
        self.pi.wave_add_generic(waveforms)
        self._marks[t] = self.pi.wave_create()
        return self._marks[t]

    def _generate_space(self, t):
        self.pi.wave_add_generic([pigpio.pulse(0, 1 << self.pin, t)])
        self._spaces[t] = self.pi.wave_create()
        return self._spaces[t]

    def _build_byte_chain(self, byte):
        q = []
        for i in range(8):
            mark_t = K_BIT_MARK
            space_t = (K_ONE_SPACE if (byte >> i) & 1 else K_ZERO_SPACE)

            q.append(mark_t)
            q.append(space_t)

        return q

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
        q = [K_HEADER_MARK, K_HEADER_SPACE]
        
        for byte in data:
            q.extend(self._build_byte_chain(byte))
        
        q.extend(
            [
                K_RPT_MARK, K_RPT_SPACE,
                K_HEADER_MARK, K_HEADER_SPACE,
                K_BIT_MARK, K_ONE_SPACE,
                K_BIT_MARK, K_ONE_SPACE,
                K_BIT_MARK
            ]
        )
       
        # --- 3. FINAL EXECUTION LOOP ---
        try:
            chain = []
            for i, t in enumerate(q):
                if i & 1:
                    if t not in self._spaces:
                        self._generate_space(t)
                    chain.append(self._spaces[t])
                else:
                    if t not in self._marks:   
                        self._generate_mark(t)
                    chain.append(self._marks[t]) 

            self.pi.wave_chain(chain)
            while self.pi.wave_tx_busy():
                time.sleep(0.001)
        
        except Exception as e:
            print(e)
        
        finally:
            self.pi.write(self.pin, 0)

