"""
Sending and receiving 433/315Mhz signals with low-cost GPIO RF Modules on a Raspberry Pi.
This is adjusted code for raspberry pi pico, original is from: https://github.com/milaq/rpi-rf
"""

import config
import time
from machine import Pin
from collections import namedtuple

MAX_CHANGES = 67

Protocol = namedtuple('Protocol',
                      ['pulselength',
                       'sync_high', 'sync_low',
                       'zero_high', 'zero_low',
                       'one_high', 'one_low',
                       'inverted'])
PROTOCOLS = (None,
             Protocol(350, 1, 31, 1, 3, 3, 1, False),
             Protocol(650, 1, 10, 1, 2, 2, 1, False),
             Protocol(100, 30, 71, 4, 11, 9, 6, False),
             Protocol(380, 1, 6, 1, 3, 3, 1, False),
             Protocol(500, 6, 14, 1, 2, 2, 1, False),
             Protocol(200, 1, 10, 1, 5, 1, 1, False),
             Protocol(275, 38, 1, 1, 3, 3, 1, False),
             Protocol(500, 6, 14, 1, 2, 2, 1, False),
             Protocol(200, 1, 10, 1, 5, 1, 1, False),
             Protocol(150, 2, 62, 1, 6, 6, 1, False),
             Protocol(270, 36, 1, 1, 2, 2, 1, True))


class RFDevice:
    """Representation of a GPIO RF device."""

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(self, gpio = None,
                 tx_proto=1, tx_pulselength=None, tx_repeat=10, tx_length=24, rx_tolerance=80, tx_inverted=None):
        """Initialize the RF device."""
        self.gpio = gpio
        self.tx_enabled = False
        self.tx_proto = tx_proto
        if tx_pulselength:
            self.tx_pulselength = tx_pulselength
        else:
            self.tx_pulselength = PROTOCOLS[tx_proto].pulselength
        self.tx_repeat = tx_repeat
        self.tx_length = tx_length
        if tx_inverted:
            self.tx_inverted = tx_inverted
        else:
            self.tx_inverted = PROTOCOLS[tx_proto].inverted
        self.rx_enabled = False
        self.rx_tolerance = rx_tolerance
        # internal values
        self._rx_timings = [0] * (MAX_CHANGES + 1)
        self._rx_last_timestamp = 0
        self._rx_change_count = 0
        self._rx_repeat_count = 0
        # successful RX values
        self.rx_code = None
        self.rx_code_timestamp = None
        self.rx_proto = None
        self.rx_bitlength = None
        self.rx_pulselength = None

    def cleanup(self):
        """Disable TX and RX and clean up GPIO."""
        if self.tx_enabled:
            self.disable_tx()
        if self.rx_enabled:
            self.disable_rx()
        print("Cleanup")

    def enable_tx(self):
        """Enable TX, set up GPIO."""
        if self.rx_enabled:
            print("RX is enabled, not enabling TX")
            return False
        if not self.tx_enabled:
            self.tx_enabled = True
            self.gpio = Pin(config.TX_PIN, Pin.OUT)
            print("TX enabled")
        return True

    def disable_tx(self):
        """Disable TX, reset GPIO."""
        if self.tx_enabled:
            # set up GPIO pin as input for safety
            self.gpio = Pin(config.TX_PIN, Pin.IN, Pin.PULL_DOWN)
            self.tx_enabled = False
            print("TX disabled")
        return True

    def tx_code(self, code, tx_proto=None, tx_pulselength=None, tx_length=None, tx_inverted=None):
        """
        Send a decimal code.
        Optionally set protocol, pulselength and code length.
        When none given reset to default protocol, default pulselength and set code length to 24 bits.
        """
        self.us_sleep = 0
        self.start = time.ticks_us()

        if tx_proto:
            self.tx_proto = tx_proto
        else:
            self.tx_proto = 1
        if tx_pulselength:
            self.tx_pulselength = tx_pulselength
        elif not self.tx_pulselength:
            self.tx_pulselength = PROTOCOLS[self.tx_proto].pulselength
        if tx_length:
            self.tx_length = tx_length
        elif self.tx_proto == 6:
            self.tx_length = 32
        elif self.tx_proto == 8:
            self.tx_length = 12
        elif (code > 16777216):
            self.tx_length = 32
        else:
            self.tx_length = 24
        if tx_inverted:
            self.tx_inverted = tx_inverted
        else:
            self.tx_inverted = PROTOCOLS[self.tx_proto].inverted
        rawcode = "{{0:0{}b}}".format(self.tx_length + 2).format(code)[2:]
        if self.tx_proto == 6:
            nexacode = ""
            for b in rawcode:
                if b == '0':
                    nexacode = nexacode + "01"
                if b == '1':
                    nexacode = nexacode + "10"
            rawcode = nexacode
            self.tx_length = 64
        print("TX code: ", str(code), " binary: ", rawcode)
        status = self.tx_bin(rawcode)

        # We must not transmit too often, we also need to make sure we don't corrupt our current message, so wait a bit more between messages if some are chained by caller
        # 500ms seems excessive, should test and reduce when time allows.
        self.us_sleep = self.us_sleep + 500000
        
        # finish up any pending sleep for 0 bytes - so next transmit code doesn't mess our currently sent one.
        while time.ticks_us() - self.start < self.us_sleep:
            time.sleep_us(1)
            
        return status


    def tx_bin(self, rawcode):
        """Send a binary code."""
        for _ in range(0, self.tx_repeat):
            if self.tx_proto == 6:
                if not self.tx_sync():
                    return False
            for byte in range(0, self.tx_length):
                if rawcode[byte] == '0':
                    if not self.tx_l0():
                        return False
                else:
                    if not self.tx_l1():
                        return False
            if not self.tx_sync():
                return False

        return True

    def tx_l0(self):
        """Send a '0' bit."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            print("Unknown TX protocol")
            return False
        return self.tx_waveform(PROTOCOLS[self.tx_proto].zero_high,
                                PROTOCOLS[self.tx_proto].zero_low)

    def tx_l1(self):
        """Send a '1' bit."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            print("Unknown TX protocol")
            return False
        return self.tx_waveform(PROTOCOLS[self.tx_proto].one_high,
                                PROTOCOLS[self.tx_proto].one_low)

    def tx_sync(self):
        """Send a sync."""
        if not 0 < self.tx_proto < len(PROTOCOLS):
            print("Unknown TX protocol")
            return False
        return self.tx_waveform(PROTOCOLS[self.tx_proto].sync_high,
                                PROTOCOLS[self.tx_proto].sync_low)

    def tx_waveform(self, highpulses, lowpulses):
        """Send basic waveform."""
        if not self.tx_enabled:
            print("TX is not enabled, not sending data")
            return False

        while time.ticks_us() - self.start < self.us_sleep:
            time.sleep_us(1)

        self.gpio.value(1)
        self.start = time.ticks_us()

        self.us_sleep = int(highpulses * self.tx_pulselength) # - int(int(highpulses * self.tx_pulselength)/100)
        while time.ticks_us() - self.start < self.us_sleep:
            time.sleep_us(1)
        
        self.gpio.value(0)
        self.start = time.ticks_us()
        self.us_sleep = int(lowpulses * self.tx_pulselength) # - int(int(lowpulses * self.tx_pulselength)/100)
        
        return True

    def enable_rx(self):
        """Enable RX, set up GPIO and add event detection."""
        if self.tx_enabled:
            print("TX is enabled, not enabling RX")
            return False
        if not self.rx_enabled:
            self.rx_enabled = True
            self.gpio = Pin(config.RX_PIN, Pin.IN, Pin.PULL_DOWN)
            self.gpio.irq(handler=self.rx_callback, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
            print("RX enabled, pin: " + str(config.RX_PIN))
        return True

    def disable_rx(self):
        """Disable RX, remove GPIO event detection."""
        if self.rx_enabled:
            self.gpio.irq(None)
            self.rx_enabled = False
            print("RX disabled")
        return True

    # pylint: disable=unused-argument
    def rx_callback(self, gpio):
        """RX callback for GPIO event detection. Handle basic signal detection."""
        timestamp = time.ticks_us()
        duration = timestamp - self._rx_last_timestamp
        if duration > 5000:
            if abs(duration - self._rx_timings[0]) < 200:
                self._rx_repeat_count += 1
                self._rx_change_count -= 1
                if self._rx_repeat_count == 2:
                    for pnum in range(1, len(PROTOCOLS)):
                        if self._rx_waveform(pnum, self._rx_change_count, timestamp):
                            break
                    self._rx_repeat_count = 0
            self._rx_change_count = 0

        if self._rx_change_count >= MAX_CHANGES:
            self._rx_change_count = 0
            self._rx_repeat_count = 0
        self._rx_timings[self._rx_change_count] = duration
        self._rx_change_count += 1
        self._rx_last_timestamp = timestamp

    def _rx_waveform(self, pnum, change_count, timestamp):
        """Detect waveform and format code."""
        code = 0
        delay = int(self._rx_timings[0] / PROTOCOLS[pnum].sync_low)
        delay_tolerance = delay * self.rx_tolerance / 100

        for i in range(1, change_count, 2):
            if (abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].zero_high) < delay_tolerance and
                abs(self._rx_timings[i+1] - delay * PROTOCOLS[pnum].zero_low) < delay_tolerance):
                code <<= 1
            elif (abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].one_high) < delay_tolerance and
                  abs(self._rx_timings[i+1] - delay * PROTOCOLS[pnum].one_low) < delay_tolerance):
                code <<= 1
                code |= 1
            else:
                return False

        if self._rx_change_count > 6 and code != 0:
            self.rx_code = code
            self.rx_code_timestamp = timestamp
            self.rx_bitlength = int(change_count / 2)
            self.rx_pulselength = delay
            self.rx_proto = pnum
            return True

        return False
