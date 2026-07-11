from strategy.strategy_08_volatility import VolatilityStrategy
from strategy_core.registry import register


@register('volatility', '돌파매매')
class VolatilityPreset:
    strategy_class = VolatilityStrategy
    name = '변동성 확장'
    description = '변동성 최저에서 돌파 시 매수'
    params = [
        {'name': 'lookback_days', 'label': '변동성 기간', 'min': 5, 'max': 30, 'default': 10, 'step': 5},
        {'name': 'breakout_pct', 'label': '돌파 기준(%)', 'min': 1, 'max': 10, 'default': 3, 'step': 1},
    ]
    param_map = {'lookback_days': 'lookback_days', 'breakout_pct': 'breakout_pct'}
    builder_state = {
        'metadata': {
            'id': 'volatility', 'name': '변동성 확장', 'description': '변동성 최저에서 돌파 시 매수',
            'category': 'volatility', 'tags': ['volatility', 'breakout', 'atr'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'vol_1', 'indicatorId': 'volatility_ind', 'alias': 'vol_10', 'params': {'period': 10}, 'output': 'value'},
            {'id': 'chg_1', 'indicatorId': 'change', 'alias': 'chg_1', 'params': {}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [
            {'id': 'entry_1', 'left': {'type': 'indicator', 'indicatorAlias': 'vol_10', 'indicatorOutput': 'value'}, 'operator': 'less_than', 'right': {'type': 'value', 'value': 0.02}},
            {'id': 'entry_2', 'left': {'type': 'indicator', 'indicatorAlias': 'chg_1', 'indicatorOutput': 'value'}, 'operator': 'greater_equal', 'right': {'type': 'value', 'value': 3}},
        ]},
        'exit': {'logic': 'OR', 'conditions': [{'id': 'exit_1', 'left': {'type': 'indicator', 'indicatorAlias': 'chg_1', 'indicatorOutput': 'value'}, 'operator': 'less_equal', 'right': {'type': 'value', 'value': -3}}]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 3}, 'takeProfit': {'enabled': False, 'percent': 10}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
