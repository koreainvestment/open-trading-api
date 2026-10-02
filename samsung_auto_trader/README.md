# Samsung Auto Trader

## Run

1. Set environment variables
	- `GH_ACCOUNT`
	- `GH_APPKEY`
	- `GH_APPSECRET`
2. Install dependencies
	- `pip install -r requirements.txt`
3. Start
	- `python main.py`

## Notes

- Mock trading only
- Trading window is evaluated in KST (`Asia/Seoul`)
- Current price endpoint uses:
  - endpoint: `/uapi/domestic-stock/v1/quotations/inquire-price`
  - tr_id: `FHKST01010100`

