from strategy.strategy_04_consecutive import ConsecutiveStrategy
from strategy_core.registry import register


@register('consecutive', '추세추종')
class ConsecutivePreset:
    strategy_class = ConsecutiveStrategy
    name = '연속 상승/하락'
    description = 'N일 연속 상승 시 매수'
    params = [
        {'name': 'consecutive_days', 'label': '연속 일수', 'min': 3, 'max': 10, 'default': 5, 'step': 1},
    ]
    param_map = {'consecutive_days': 'buy_days'}
    builder_state = {
        'metadata': {
            'id': 'consecutive',
            'name': '연속 상승/하락',
            'description': 'N일 연속 상승 시 매수',
            'category': 'pattern',
            'tags': ['consecutive', 'pattern'],
            'author': 'KIS',
        },
        'indicators': [
            {'id': 'consec_up', 'indicatorId': 'consecutive', 'alias': 'up_days', 'params': {'direction': 'up'}, 'output': 'value'},
            {'id': 'consec_down', 'indicatorId': 'consecutive', 'alias': 'down_days', 'params': {'direction': 'down'}, 'output': 'value'},
        ],
        'entry': {
            'logic': 'AND',
            'conditions': [{
                'id': 'entry_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'up_days', 'indicatorOutput': 'value'},
                'operator': 'greater_equal',
                'right': {'type': 'value', 'value': 5},
            }]
        },
        'exit': {
            'logic': 'OR',
            'conditions': [{
                'id': 'exit_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'down_days', 'indicatorOutput': 'value'},
                'operator': 'greater_equal',
                'right': {'type': 'value', 'value': 5},
            }]
        },
        'risk': {
            'stopLoss': {'enabled': True, 'percent': 5},
            'takeProfit': {'enabled': False, 'percent': 10},
            'trailingStop': {'enabled': False, 'percent': 3},
        },
    }
