# Made by Deltaion Lee (MCMi460) on GitHub
from . import *

class Presence:
    def __init__(self, **fields) -> None:
        self._types:typing.List[typing.Tuple[str, type]] = [
            ('state', str),
            ('details', str),
            ('start', int),
            ('end', int),
            ('large_image', str),
            ('large_text', str),
            ('small_image', str),
            ('small_text', str),
            ('id', str),
            ('size', tuple),
            ('match', str),
            ('join', str),
            ('spectate', str),
            ('buttons', list),
            ('instance', bool),
        ]
        
        self._activity = self._fix_activity({
            'state': fields.get('state'),
            'details': fields.get('details'),
            'timestamps': {
                'start': fields.get('start'),
                'end': fields.get('end'),
            },
            'assets': {
                'large_image': fields.get('large_image'),
                'large_text': fields.get('large_text'),
                'small_image': fields.get('small_image'),
                'small_text': fields.get('small_text'),
            },
            'party': {
                'id': fields.get('party_id'),
                'size': fields.get('party_size'),
            },
            'secrets': {
                'match': fields.get('match'),
                'join': fields.get('join'),
                'spectate': fields.get('spectate'),
            },
            'buttons': fields.get('buttons'),
            'instance': fields.get('instance'),
        })
    
    def _fix_activity(self, dictionary:dict) -> typing.Optional[dict]:
        if all(x == None for x in dictionary.values()):
            return None
        for key in dictionary.copy():
            if isinstance(dictionary[key], dict):
                dictionary[key] = self._fix_activity(dictionary[key])
            if dictionary[key] is None:
                del dictionary[key]
            elif not isinstance(dictionary[key], dict) and not isinstance(dictionary[key], dict(self._types)[key]):
                try:
                    dictionary[key] = dict(self._types)[key](dictionary[key])
                except:
                    raise TypeError('Presence field \'%s\' does not match type \'%s\'' % (key, dict(self._types)[key]))
        return dictionary

    def to_JSON(self) -> str:
        return json.dumps(self._activity)
    
    def to_dict(self) -> dict:
        return self._activity
    
    def __str__(self) -> str:
        ret = []
        for key in self._activity:
            ret.append('%s: %s' % (key, self._activity[key]))
        return '\n'.join(ret)
