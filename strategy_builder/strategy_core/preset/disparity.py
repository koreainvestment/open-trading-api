from strategy.strategy_05_disparity import DisparityStrategy
from strategy_core.registry import register


@register('disparity', '역추세')
class DisparityPreset:
    strategy_class = DisparityStrategy
    name = '이격도'
    description = 'MA 대비 이격 기준 매수/매도'
    params = [
        {'name': 'period', 'label': 'MA 기간', 'min': 5, 'max': 40, 'default': 20, 'step': 5},
        {'name': 'buy_threshold', 'label': '매수 기준', 'min': 80, 'max': 95, 'default': 90, 'step': 1},
        {'name': 'sell_threshold', 'label': '매도 기준', 'min': 105, 'max': 120, 'default': 110, 'step': 1},
    ]
    param_map = {'period': 'period', 'buy_threshold': 'oversold_threshold', 'sell_threshold': 'overbought_threshold'}
    builder_state = {
        'metadata': {
            'id': 'disparity', 'name': '이격도', 'description': 'MA 대비 이격 기준 매수/매도',
            'category': 'reversal', 'tags': ['disparity', 'ma', 'reversal'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'disp_1', 'indicatorId': 'disparity', 'alias': 'disp_20', 'params': {'period': 20}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [{'id': 'entry_1', 'left': {'type': 'indicator', 'indicatorAlias': 'disp_20', 'indicatorOutput': 'value'}, 'operator': 'less_than', 'right': {'type': 'value', 'value': 90}}]},
        'exit': {'logic': 'OR', 'conditions': [{'id': 'exit_1', 'left': {'type': 'indicator', 'indicatorAlias': 'disp_20', 'indicatorOutput': 'value'}, 'operator': 'greater_than', 'right': {'type': 'value', 'value': 110}}]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 5}, 'takeProfit': {'enabled': True, 'percent': 10}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
