from strategy.strategy_10_trend_filter import TrendFilterStrategy
from strategy_core.registry import register


@register('trend_filter', '추세추종')
class TrendFilterPreset:
    strategy_class = TrendFilterStrategy
    name = '추세 필터'
    description = 'MA 위/아래 추세 방향 매매'
    params = [
        {'name': 'ma_period', 'label': 'MA 기간', 'min': 20, 'max': 120, 'default': 60, 'step': 10},
    ]
    param_map = {'ma_period': 'ma_period'}
    builder_state = {
        'metadata': {
            'id': 'trend_filter', 'name': '추세 필터', 'description': 'MA 위/아래 추세 방향 매매',
            'category': 'trend', 'tags': ['trend', 'ma', 'filter'], 'author': 'KIS',
        },
        'indicators': [
            {'id': 'sma_1', 'indicatorId': 'sma', 'alias': 'sma_1', 'params': {'period': 60}, 'output': 'value'},
            {'id': 'chg_1', 'indicatorId': 'change', 'alias': 'chg_1', 'params': {}, 'output': 'value'},
        ],
        'entry': {'logic': 'AND', 'conditions': [
            {'id': 'entry_1', 'left': {'type': 'price', 'priceField': 'close'}, 'operator': 'greater_than', 'right': {'type': 'indicator', 'indicatorAlias': 'sma_1', 'indicatorOutput': 'value'}},
            {'id': 'entry_2', 'left': {'type': 'indicator', 'indicatorAlias': 'chg_1', 'indicatorOutput': 'value'}, 'operator': 'greater_than', 'right': {'type': 'value', 'value': 0}},
        ]},
        'exit': {'logic': 'AND', 'conditions': [
            {'id': 'exit_1', 'left': {'type': 'price', 'priceField': 'close'}, 'operator': 'less_than', 'right': {'type': 'indicator', 'indicatorAlias': 'sma_1', 'indicatorOutput': 'value'}},
            {'id': 'exit_2', 'left': {'type': 'indicator', 'indicatorAlias': 'chg_1', 'indicatorOutput': 'value'}, 'operator': 'less_than', 'right': {'type': 'value', 'value': 0}},
        ]},
        'risk': {'stopLoss': {'enabled': True, 'percent': 5}, 'takeProfit': {'enabled': False, 'percent': 10}, 'trailingStop': {'enabled': False, 'percent': 3}},
    }
