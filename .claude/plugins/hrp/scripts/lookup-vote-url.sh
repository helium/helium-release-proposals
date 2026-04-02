#!/bin/bash
# Look up a Helium Release Proposal's heliumvote.com URL and vote results
# by querying the on-chain proposal account via Solana RPC.
#
# Usage:
#   lookup-vote-url.sh --month 2026-04
#   lookup-vote-url.sh --month 2026-04 --results   # also output vote percentages
#
# Output (JSON):
#   {"url": "https://www.heliumvote.com/hnt/proposals/AHJ6...", "publicKey": "AHJ6..."}
#   With --results:
#   {"url": "...", "publicKey": "...", "forPercent": 97.53, "againstPercent": 2.46}
#
# Requires: curl, python3

set -euo pipefail

SOLANA_RPC="${SOLANA_RPC:-https://api.mainnet-beta.solana.com}"
PROGRAM_ID="propFYxqmVcufMhk5esNMrexq2ogHbbC2kP9PU1qxKs"

# Anchor discriminator for ProposalV0 accounts
DISCRIMINATOR_HEX="fec210abd614c051"

# Helium HNT organization key (bytes 8-40 of any known HNT proposal)
ORG_KEY_HEX="2ad9925b84ab17b7b1f3ddab7b5a008cac47b55faa0ebb2a172fdd413a7bf895"

usage() {
  echo "Usage: $0 --month YYYY-MM [--results]" >&2
  exit 1
}

MONTH="" WITH_RESULTS=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --month)    MONTH="$2"; shift 2 ;;
    --results)  WITH_RESULTS=true; shift ;;
    *)          usage ;;
  esac
done

if [[ -z "$MONTH" ]]; then
  usage
fi

PROPOSAL_NAME="Helium Release Proposal: $MONTH"

# Build base64-encoded filter values for Solana RPC
DISC_B64=$(python3 -c "import base64; print(base64.b64encode(bytes.fromhex('$DISCRIMINATOR_HEX')).decode())")
ORG_B64=$(python3 -c "import base64; print(base64.b64encode(bytes.fromhex('$ORG_KEY_HEX')).decode())")

RPC_BODY='{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getProgramAccounts",
  "params": [
    "'"$PROGRAM_ID"'",
    {
      "encoding": "base64",
      "filters": [
        {"memcmp": {"offset": 0, "bytes": "'"$DISC_B64"'", "encoding": "base64"}},
        {"memcmp": {"offset": 8, "bytes": "'"$ORG_B64"'", "encoding": "base64"}}
      ]
    }
  ]
}'

# Write RPC response to a temp file to avoid shell argument length limits (~48KB response)
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

MAX_RETRIES=3
for attempt in $(seq 1 $MAX_RETRIES); do
  curl -s "$SOLANA_RPC" -X POST -H "Content-Type: application/json" -d "$RPC_BODY" -o "$TMPFILE"

  # Check if we got a valid response with results
  if python3 -c "import json; d=json.load(open('$TMPFILE')); assert len(d.get('result',[])) > 0" 2>/dev/null; then
    break
  fi

  if [ "$attempt" -lt "$MAX_RETRIES" ]; then
    # Back off longer on each retry (429 rate limits need more time)
    DELAY=$((attempt * 3))
    echo "RPC returned empty or rate-limited, retrying in ${DELAY}s ($attempt/$MAX_RETRIES)..." >&2
    sleep "$DELAY"
  fi
done

# Find the proposal matching our name and extract vote data
python3 -c "
import json, base64, sys

target_name = sys.argv[1]
with_results = sys.argv[2] == 'true'
tmpfile = sys.argv[3]

try:
    with open(tmpfile) as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    print(json.dumps({'error': 'Solana RPC returned invalid response (possible rate limit)'}))
    sys.exit(1)

if 'error' in data:
    print(json.dumps({'error': f'Solana RPC error: {data[\"error\"]}'}))
    sys.exit(1)

accounts = data.get('result', [])
if not accounts:
    print(json.dumps({'error': 'No proposals found (RPC may be rate-limiting)'}))
    sys.exit(1)

for acc in accounts:
    raw = base64.b64decode(acc['account']['data'][0])

    # Scan for the proposal name string (4-byte length prefix + UTF-8)
    # Uses prefix match to handle '- No Changes' suffix variants
    name = None
    for i in range(120, min(250, len(raw) - 4)):
        length = int.from_bytes(raw[i:i+4], 'little')
        if length < len(target_name) or length > len(target_name) + 30:
            continue
        try:
            s = raw[i+4:i+4+length].decode('utf-8')
            if s.startswith(target_name):
                name = s
                break
        except:
            pass

    if name is None:
        continue

    pubkey = acc['pubkey']
    result = {
        'url': f'https://www.heliumvote.com/hnt/proposals/{pubkey}',
        'publicKey': pubkey,
    }

    if with_results:
        # Parse choices to extract vote weights
        # Each choice: weight(u128, 16 bytes) + name_len(u32) + name(bytes) + uri_option(1 byte)
        # Scan for the choices array by finding num_choices=2 followed by 'For ...' / 'Against ...'
        for i in range(100, len(raw) - 4):
            num = int.from_bytes(raw[i:i+4], 'little')
            if num != 2:
                continue
            try:
                off = i + 4
                w0 = int.from_bytes(raw[off:off+16], 'little')
                off += 16
                n0_len = int.from_bytes(raw[off:off+4], 'little')
                off += 4
                n0 = raw[off:off+n0_len].decode('utf-8')
                off += n0_len
                if not n0.startswith('For '):
                    continue
                off += 1  # uri option byte (0 = None)
                w1 = int.from_bytes(raw[off:off+16], 'little')
                off += 16
                n1_len = int.from_bytes(raw[off:off+4], 'little')
                off += 4
                n1 = raw[off:off+n1_len].decode('utf-8')
                if not n1.startswith('Against '):
                    continue
                # Valid parse — compute percentages using heliumvote.com's truncating math:
                # new BN(weight).mul(new BN(10000)).div(totalVotes).toNumber() * (100/10000)
                total = w0 + w1
                if total > 0:
                    result['forPercent'] = (w0 * 10000 // total) * 100 / 10000
                    result['againstPercent'] = (w1 * 10000 // total) * 100 / 10000
                    result['totalVeHNT'] = round(total / 1e8, 2)
                else:
                    result['forPercent'] = 0
                    result['againstPercent'] = 0
                    result['totalVeHNT'] = 0
                break
            except:
                continue

    print(json.dumps(result))
    sys.exit(0)

print(json.dumps({'error': f'No proposal found matching \"{target_name}\"'}))
sys.exit(1)
" "$PROPOSAL_NAME" "$WITH_RESULTS" "$TMPFILE"
