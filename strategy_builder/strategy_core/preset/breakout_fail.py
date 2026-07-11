from strategy.strategy_06_breakout_fail import BreakoutFailStrategy
from strategy_core.registry import register


@register('breakout_fail', '손절')
class BreakoutFailPreset:
    strategy_class = BreakoutFailStrategy
    name = '돌파 실패'
    description = '전고점 돌파 실패 시 매도'
    params = [
        {'name': 'lookback_days', 'label': '전고점 기간', 'min': 10, 'max': 40, 'default': 20, 'step': 5},
        {'name': 'drop_pct', 'label': '하락 기준(%)', 'min': -10, 'max': -1, 'default': -3, 'step': 1},
    ]
    param_map = {'lookback_days': 'lookback_days', 'drop_pct': 'fail_threshold'}
    builder_state = {
        'metadata': {
            'id': 'breakout_fail', 'name': '돌파 실패', 'description': '전고점 돌파 실패 시 매도',
            'category': 'reversal', 'tags': ['breakout', 'fail', 'reversal'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'maximum_1', 'indicatorId': 'maximum', 'alias': 'prev_high', 'params': {'period': 20}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [{'id': 'entry_1', 'left': {'type': 'price', 'priceField': 'close'}, 'operator': 'less_than', 'right': {'type': 'indicator', 'indicatorAlias': 'prev_high', 'indicatorOutput': 'value'}}]},
        'exit': {'logic': 'OR', 'conditions': [{'id': 'exit_1', 'left': {'type': 'price', 'priceField': 'close'}, 'operator': 'greater_than', 'right': {'type': 'indicator', 'indicatorAlias': 'prev_high', 'indicatorOutput': 'value'}}]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 3}, 'takeProfit': {'enabled': False, 'percent': 10}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
