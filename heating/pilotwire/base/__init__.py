# -*- coding: utf-8 -*-


ZONES = [1, 2, 3, 4]


class BaseControler(object):

    modes_out = {
        'C': '00',
        'E': '11',
        'H': '01',
        'A': '10',
    }

    @property
    def modes_dict(self):
        rev_modes_out = {v: k for k, v in self.modes_out.items()}
        shift = lambda x: (x - 1) * 2
        return {
            str(z): rev_modes_out.get(
                bin(
                    (self.output_value & (3 << shift(z))) >> (shift(z))
                ).split('b')[-1].zfill(2)
            )
            for z in ZONES
        }

    @modes_dict.setter
    def modes_dict(self, dct):
        zones_modes = [(z, dct.get(str(z), 'C')) for z in ZONES]
        zones_int = [
            int(self.modes_out.get(m, '00'), 2) << ((n - 1) * 2)
            for n, m in zones_modes
        ]
        self.output_value = sum(zones_int)

    def getModes(self):
        return self.modes_dict

    def setModes(self, modes_dict):
        if not isinstance(modes_dict, dict):
            raise TypeError("setModes: bad argument type (dict expected)")
        self.modes_dict = modes_dict
        return self.modes_dict
