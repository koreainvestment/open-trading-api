from strategy.strategy_03_week52_high import Week52HighStrategy
from strategy_core.registry import register


@register('week52_high', '돌파매매')
class Week52HighPreset:
    strategy_class = Week52HighStrategy
    name = '52주 신고가'
    description = '52주 최고가 돌파 시 매수'
    params = [
        {'name': 'breakout_margin', 'label': '돌파 마진(%)', 'min': 0, 'max': 5, 'default': 0, 'step': 0.5},
    ]
    param_map = {'breakout_margin': 'breakout_margin'}
    builder_state = {
        'metadata': {
            'id': 'week52_high',
            'name': '52주 신고가',
            'description': '52주 최고가 돌파 시 매수',
            'category': 'breakout',
            'tags': ['52week', 'high', 'breakout'],
            'author': 'KIS',
        },
        'indicators': [
            {'id': 'maximum_1', 'indicatorId': 'maximum', 'alias': 'high_52w', 'params': {'period': 252}, 'output': 'value'},
        ],
        'entry': {
            'logic': 'AND',
            'conditions': [{
                'id': 'entry_1',
                'left': {'type': 'price', 'priceField': 'close'},
                'operator': 'greater_than',
                'right': {'type': 'indicator', 'indicatorAlias': 'high_52w', 'indicatorOutput': 'value'},
            }]
        },
        'exit': {
            'logic': 'OR',
            'conditions': [{
                'id': 'exit_1',
                'left': {'type': 'price', 'priceField': 'close'},
                'operator': 'less_than',
                'right': {'type': 'indicator', 'indicatorAlias': 'high_52w', 'indicatorOutput': 'value'},
            }]
        },
        'risk': {
            'stopLoss': {'enabled': True, 'percent': 5},
            'takeProfit': {'enabled': True, 'percent': 15},
            'trailingStop': {'enabled': False, 'percent': 3},
        },
    }
