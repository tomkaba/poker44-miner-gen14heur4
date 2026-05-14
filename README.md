# poker44-miner-gen14heur4

Minimal release repository for model gen14heur4.

## Quick start

```bash
git clone https://github.com/tomkaba/poker44-miner-gen14heur4.git
cd poker44-miner-gen14heur4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run Miner

```bash
WALLET_NAME=my_cold \
HOTKEY=my_poker44_hotkey \
AXON_PORT=8091 \
ALLOWED_VALIDATOR_HOTKEYS="validator_hotkey_1 validator_hotkey_2" \
python neurons/miner.py
```

Or via shell script:

```bash
./start_miner.sh HOTKEY_ID[,HOTKEY_ID2,...]
```
