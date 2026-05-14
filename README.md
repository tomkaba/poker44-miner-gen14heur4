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

### Method 1: Direct Python (Recommended)

```bash
WALLET_NAME=my_cold \
HOTKEY=my_poker44_hotkey \
AXON_PORT=8091 \
ALLOWED_VALIDATOR_HOTKEYS="validator_hotkey_1 validator_hotkey_2" \
python neurons/miner.py
```

Or via `.env` file:

```bash
cp .env.example .env
# edit .env
python neurons/miner.py
```

### Method 2: Shell script wrapper

```bash
./start_miner.sh HOTKEY_ID[,HOTKEY_ID2,...]
```

## Notes

- Scorer is hardcoded to `gen14heur4`.
- Trained on miner logs 75, 161, 201 with benchmark data.
- This repository is single-model and model-specific.
- Manifest `implementation_sha256` is computed over the full request-flow file set.
