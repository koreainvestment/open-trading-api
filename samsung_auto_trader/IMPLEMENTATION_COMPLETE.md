# Samsung Auto Trader - Implementation Summary

## Current Status

- Project folder restored and runnable.
- Trading window and log presentation are both KST-based.
- Quote endpoint 404 issue fixed.
- Token cache reuse confirmed in runtime logs.

## Key Technical Decisions

1. Environment variables are mandatory:
	- `GH_ACCOUNT`
	- `GH_APPKEY`
	- `GH_APPSECRET`
2. Token is cached in `token_cache.json` and reused until expiry.
3. Quote API uses:
	- endpoint: `/uapi/domestic-stock/v1/quotations/inquire-price`
	- `tr_id`: `FHKST01010100`
4. Trading loop time check uses KST window `09:10 ~ 15:30`.

## Files Included

- `main.py` - startup and orchestration entrypoint
- `config.py` - runtime constants and KST helpers
- `auth.py` - authentication and token cache
- `api_client.py` - HTTP wrapper and retry/error handling
- `market_data.py` - current price retrieval
- `account.py` - holdings and balance query parsing
- `orders.py` - buy/sell order API calls
- `trader.py` - polling loop and step-by-step trade flow
- `logger_config.py` - file/console logging (KST timestamp)
- `verify.py` - quick health check script

## Quick Commands

```bash
cd /workspaces/open-trading-api/samsung_auto_trader
python verify.py
python main.py
```

## Notes

- On weekends/holidays, mock order APIs can return:
  - `40100000`, message: `모의투자 영업일이 아닙니다.`
- That response is expected and does not mean code is broken.

