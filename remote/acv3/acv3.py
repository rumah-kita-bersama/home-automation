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

# Protocol Timings (Microseconds) - Mitsubishi Heavy 88-bit (ZJS)
# Re-using the same timings as 152 bit because they share the same pulse lengths usually.
K_HEADER_MARK = 3140
K_HEADER_SPACE = 1630
K_BIT_MARK = 370
K_ONE_SPACE = 420
K_ZERO_SPACE = 1220

class ACV3:
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
        # 11 bytes for Mitsubishi Heavy 88-bit
        data = [0] * 11
        
        # ZJS Signature bytes
        data[0:5] = [0xAD, 0x51, 0x3C, 0xD9, 0x26]

        # Definitions based on ir_MitsubishiHeavy.h (88 bit struct)
        # Map SwingH properly: Auto (8) if swing, else Middle (9)
        swingh_val = 8 if swing else 9
        sH1 = swingh_val & 0x03
        sH2 = (swingh_val >> 2) & 0x03
        
        # SwingV modes: Auto=0b100 (4), Highest=0b110 (6)
        swingv_val = 0b100 if swing else 0b110
        sV5 = swingv_val & 0x01
        sV7 = (swingv_val >> 1) & 0x03
        
        # Clean: 0
        clean = 0
        
        # Byte 5: _:1, SwingV5:1, SwingH1:2, _:1, Clean:1, SwingH2:2
        data[5] = (sV5 << 1) | (sH1 << 2) | (clean << 5) | (sH2 << 6)
        
        # Byte 7: _:3, SwingV7:2, Fan:3
        # Fan: Auto=0, Low=2, Med=3, High=4, Turbo=6, Econo=7
        fan_val = 4 if fan else 0
        data[7] = (sV7 << 3) | ((fan_val & 0x07) << 5)
        
        # Byte 9: Mode:3, Power:1, Temp:4
        # Mode: Auto=0, Cool=1, Dry=2, Fan=3, Heat=4. defaulting to Cool.
        mode = 1
        power = 0 if off else 1
        temp_clamped = max(17, min(31, temp))
        temp_val = temp_clamped - 17
        data[9] = (mode & 0x07) | ((power & 0x01) << 3) | ((temp_val & 0x0F) << 4)

        # Checksum (Inverted Byte Pairs)
        for i in range(5, 10, 2):
            data[i+1] = (~data[i]) & 0xFF
        
        # --- 2. LOGIC PREPARATION ---
        q = [K_HEADER_MARK, K_HEADER_SPACE]
        
        for byte in data:
            q.extend(self._build_byte_chain(byte))
        
        # Final bit mark
        q.append(K_BIT_MARK)

        final_q = q

        # --- 3. FINAL EXECUTION LOOP ---
        try:
            chain = []
            for i, t in enumerate(final_q):
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
                time.sleep(0.002)
        
        finally:
            self.pi.write(self.pin, 0)

        return True
