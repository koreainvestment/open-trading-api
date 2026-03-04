from strategy.strategy_07_strong_close import StrongCloseStrategy
from strategy_core.registry import register


@register('strong_close', '모멘텀')
class StrongClosePreset:
    strategy_class = StrongCloseStrategy
    name = '강한 종가'
    description = '당일 고가 대비 종가 위치로 매수 (장마감 후 권장)'
    params = [
        {'name': 'min_close_ratio', 'label': '최소 종가 비율', 'min': 0.5, 'max': 1.0, 'default': 0.8, 'step': 0.05},
    ]
    param_map = {'min_close_ratio': 'min_close_ratio'}
    builder_state = {
        'metadata': {
            'id': 'strong_close', 'name': '강한 종가', 'description': '당일 고가 대비 종가 위치로 매수 (장마감 후 권장)',
            'category': 'momentum', 'tags': ['strong', 'close', 'momentum'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'ibs_1', 'indicatorId': 'ibs', 'alias': 'ibs_1', 'params': {}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [{'id': 'entry_1', 'left': {'type': 'indicator', 'indicatorAlias': 'ibs_1', 'indicatorOutput': 'value'}, 'operator': 'greater_equal', 'right': {'type': 'value', 'value': 0.8}}]},
        'exit': {'logic': 'OR', 'conditions': [{'id': 'exit_1', 'left': {'type': 'indicator', 'indicatorAlias': 'ibs_1', 'indicatorOutput': 'value'}, 'operator': 'less_than', 'right': {'type': 'value', 'value': 0.5}}]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 3}, 'takeProfit': {'enabled': True, 'percent': 5}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
