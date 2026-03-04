from strategy.strategy_09_mean_reversion import MeanReversionStrategy
from strategy_core.registry import register


@register('mean_reversion', '역추세')
class MeanReversionPreset:
    strategy_class = MeanReversionStrategy
    name = '평균회귀'
    description = 'N일 평균 대비 이탈 시 매매'
    params = [
        {'name': 'period', 'label': '평균 기간', 'min': 3, 'max': 20, 'default': 5, 'step': 1},
        {'name': 'buy_threshold', 'label': '매수 이탈(%)', 'min': -10, 'max': -1, 'default': -3, 'step': 1},
        {'name': 'sell_threshold', 'label': '매도 이탈(%)', 'min': 1, 'max': 10, 'default': 3, 'step': 1},
    ]
    param_map = {'period': 'period', 'buy_threshold': 'buy_threshold', 'sell_threshold': 'sell_threshold'}
    builder_state = {
        'metadata': {
            'id': 'mean_reversion', 'name': '평균회귀', 'description': 'N일 평균 대비 이탈 시 매매',
            'category': 'reversal', 'tags': ['mean_reversion', 'reversal'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'disp_1', 'indicatorId': 'disparity', 'alias': 'disp_5', 'params': {'period': 5}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [{'id': 'entry_1', 'left': {'type': 'indicator', 'indicatorAlias': 'disp_5', 'indicatorOutput': 'value'}, 'operator': 'less_equal', 'right': {'type': 'value', 'value': 97}}]},
        'exit': {'logic': 'OR', 'conditions': [{'id': 'exit_1', 'left': {'type': 'indicator', 'indicatorAlias': 'disp_5', 'indicatorOutput': 'value'}, 'operator': 'greater_equal', 'right': {'type': 'value', 'value': 103}}]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 3}, 'takeProfit': {'enabled': True, 'percent': 3}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
