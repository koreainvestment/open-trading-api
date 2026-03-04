from strategy.strategy_01_golden_cross import GoldenCrossStrategy
from strategy_core.registry import register


@register('golden_cross', '추세추종')
class GoldenCrossPreset:
    strategy_class = GoldenCrossStrategy
    name = '골든크로스'
    description = '단기 MA가 장기 MA를 상향 돌파 시 매수'
    params = [
        {'name': 'short_period', 'label': '단기 MA', 'min': 3, 'max': 50, 'default': 5, 'step': 1},
        {'name': 'long_period', 'label': '장기 MA', 'min': 10, 'max': 200, 'default': 20, 'step': 5},
    ]
    param_map = {'short_period': 'short_period', 'long_period': 'long_period'}
    builder_state = {
        'metadata': {
            'id': 'golden_cross',
            'name': '골든크로스',
            'description': '단기 MA가 장기 MA를 상향 돌파 시 매수',
            'category': 'trend',
            'tags': ['ma', 'crossover', 'trend'],
            'author': 'KIS',
        },
        'indicators': [
            {'id': 'sma_1', 'indicatorId': 'sma', 'alias': 'sma_fast', 'params': {'period': 5}, 'output': 'value'},
            {'id': 'sma_2', 'indicatorId': 'sma', 'alias': 'sma_slow', 'params': {'period': 20}, 'output': 'value'},
        ],
        'entry': {
            'logic': 'AND',
            'conditions': [{
                'id': 'entry_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'sma_fast', 'indicatorOutput': 'value'},
                'operator': 'cross_above',
                'right': {'type': 'indicator', 'indicatorAlias': 'sma_slow', 'indicatorOutput': 'value'},
            }]
        },
        'exit': {
            'logic': 'AND',
            'conditions': [{
                'id': 'exit_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'sma_fast', 'indicatorOutput': 'value'},
                'operator': 'cross_below',
                'right': {'type': 'indicator', 'indicatorAlias': 'sma_slow', 'indicatorOutput': 'value'},
            }]
        },
        'risk': {
            'stopLoss': {'enabled': True, 'percent': 5},
            'takeProfit': {'enabled': False, 'percent': 10},
            'trailingStop': {'enabled': False, 'percent': 3},
        },
    }
