from YamJam import yamjam

class YamJamConfig(object):
    def __init__(self):
        self._project = __package__.split('.')[0]
        self._yjdict = yamjam('~/.yamjam/config.yaml').get(self._project)

    def __nonzero__(self):
        return self._yjdict is not None

    def getValue(self, keypath):
        _val = self._yjdict
        for k in keypath.split('.'):
            _val = _val[k]
        return _val

yjcfg = YamJamConfig()

yj_present = bool(yjcfg)
yjval = yjcfg.getValue

