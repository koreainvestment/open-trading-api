from strategy.strategy_02_momentum import MomentumStrategy
from strategy_core.registry import register


@register('momentum', '추세추종')
class MomentumPreset:
    strategy_class = MomentumStrategy
    name = '모멘텀'
    description = 'N일 수익률 기준 매수/매도'
    params = [
        {'name': 'lookback_days', 'label': '수익률 기간', 'min': 20, 'max': 120, 'default': 60, 'step': 10},
        {'name': 'buy_threshold', 'label': '매수 기준(%)', 'min': 10, 'max': 50, 'default': 30, 'step': 5},
        {'name': 'sell_threshold', 'label': '매도 기준(%)', 'min': -50, 'max': -5, 'default': -20, 'step': 5},
    ]
    param_map = {'lookback_days': 'lookback_days', 'buy_threshold': 'buy_threshold', 'sell_threshold': 'sell_threshold'}
    builder_state = {
        'metadata': {
            'id': 'momentum',
            'name': '모멘텀',
            'description': 'N일 수익률 기준 매수/매도',
            'category': 'momentum',
            'tags': ['momentum', 'rate_of_change'],
            'author': 'KIS',
        },
        'indicators': [
            {'id': 'roc_1', 'indicatorId': 'roc', 'alias': 'roc_1', 'params': {'period': 60}, 'output': 'value'},
        ],
        'entry': {
            'logic': 'AND',
            'conditions': [{
                'id': 'entry_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'roc_1', 'indicatorOutput': 'value'},
                'operator': 'greater_than',
                'right': {'type': 'value', 'value': 30},
            }]
        },
        'exit': {
            'logic': 'OR',
            'conditions': [{
                'id': 'exit_1',
                'left': {'type': 'indicator', 'indicatorAlias': 'roc_1', 'indicatorOutput': 'value'},
                'operator': 'less_than',
                'right': {'type': 'value', 'value': -20},
            }]
        },
        'risk': {
            'stopLoss': {'enabled': True, 'percent': 5},
            'takeProfit': {'enabled': False, 'percent': 10},
            'trailingStop': {'enabled': False, 'percent': 3},
        },
    }
