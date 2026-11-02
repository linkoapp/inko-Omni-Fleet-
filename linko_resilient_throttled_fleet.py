import os
import sys
import time
import socket
import json
import hashlib
import base58
import coincurve
import random
from multiprocessing import Process, Value, Array, cpu_count
from bit import Key

# 🔱 LINKO RESILIENT THROTTLED SOVEREIGN FLEET (ANTI-BAN & SAFE CPU PACING) 🔱
# Balanced speed with smart throttling to prevent cloud platform bans and socket rate-limits.
# Sovereign Destination Wallet: bc1p3jlr9wskycdg0fnfwk0fjjumy5f25s8h04e5ms6lm862rs09du8s6tjsxa

TG_PART1 = "8936479076:"
TG_PART2 = "AAE_nWzWFrjAUN1JAFOMJpv4awMYmh2XYps"
TG_TOKEN = TG_PART1 + TG_PART2
TG_ID = "6832828732"
SOVEREIGN_WALLET = "bc1p3jlr9wskycdg0fnfwk0fjjumy5f25s8h04e5ms6lm862rs09du8s6tjsxa"

ELECTRUM_SERVERS = [
    ("fulcrum.sethforprivacy.com", 50001),
    ("electrum.blockstream.info", 50001),
    ("btc.calebepson.com", 50001)
]

ACTIVE_PUZZLES = [
    (66, 2**65, 2**66 - 1, "Puzzle #66 (6.6 BTC)"),
    (70, 2**69, 2**70 - 1, "Puzzle #70 (7.0 BTC)"),
    (75, 2**74, 2**75 - 1, "Puzzle #75 (7.5 BTC)"),
    (80, 2**79, 2**80 - 1, "Puzzle #80 (8.0 BTC)"),
    (90, 2**89, 2**90 - 1, "Puzzle #90 (9.0 BTC)"),
    (100, 2**99, 2**100 - 1, "Puzzle #100 (10.0 BTC)"),
    (140, 2**139, 2**140 - 1, "Puzzle #140 (14.0 BTC)"),
    (160, 2**159, 2**160 - 1, "Puzzle #160 (16.0 BTC - Grand Prize)")
]

def notify_telegram(message, delay=0):
    if delay > 0:
        time.sleep(delay)
    try:
        import requests
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def auto_sweep_to_sovereign(wif_key, balance_satoshis):
    try:
        k = Key(wif_key)
        if balance_satoshis > 546:
            tx_hash = k.send([(SOVEREIGN_WALLET, 'all')])
            return True, tx_hash
    except Exception as e:
        print(f"[!] Auto-sweep error: {e}")
    return False, "N/A"

def address_to_scripthash(addr):
    decoded = base58.b58decode_check(addr)
    pubkey_hash = decoded[1:]
    script = b'\x76\xa9\x14' + pubkey_hash + b'\x88\xac'
    return hashlib.sha256(script).digest()[::-1].hex()

def query_electrum_batch_throttled(addresses):
    for host, port in ELECTRUM_SERVERS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(6)
            s.connect((host, port))

            requests_list = []
            for idx, addr in enumerate(addresses):
                decoded = base58.b58decode_check(addr)
                script = b'\x76\xa9\x14' + decoded[1:] + b'\x88\xac'
                sh = hashlib.sha256(script).digest()[::-1].hex()
                req = {"id": idx, "method": "blockchain.scripthash.get_balance", "params": [sh]}
                requests_list.append(json.dumps(req))

            batch_payload = "[" + ",".join(requests_list) + "]\n"
            s.sendall(batch_payload.encode('utf-8'))

            s.settimeout(4.0)
            buffer = ""
            results = {}
            while len(results) < len(addresses):
                try:
                    data = s.recv(16384)
                    if not data: break
                    buffer += data.decode('utf-8', errors='ignore')
                    if "]" in buffer:
                        resp_list = json.loads(buffer.strip())
                        if isinstance(resp_list, list):
                            for resp in resp_list:
                                req_id = resp.get("id")
                                res = resp.get("result", {})
                                if req_id is not None and req_id < len(addresses):
                                    conf = res.get("confirmed", 0)
                                    unconf = res.get("unconfirmed", 0)
                                    results[addresses[req_id]] = conf + unconf
                        break
                except socket.timeout:
                    break
            s.close()
            if len(results) > 0:
                return results
        except:
            time.sleep(0.5) # Gentle backoff on socket error
            continue
    return {}

def run_throttled_node(server_id, node_id, speed_val):
    server_seed = 700000 + (server_id * 333) + (node_id * 19)
    stride_val = 97 + (server_id % 11) + (node_id % 7) * 3
    random.seed(server_seed)

    batch_size = 500  # Optimized batch size to prevent socket flooding
    local_scanned = 0
    t0 = time.time()
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    while True:
        try:
            p_num, p_start, p_end, p_name = random.choice(ACTIVE_PUZZLES)
            puzzle_span = p_end - p_start

            server_sector_size = puzzle_span // 50
            server_start = p_start + ((server_id - 1) % 50) * server_sector_size
            server_end = server_start + server_sector_size - 1

            anchor_int = random.randint(server_start, max(server_start + 1, server_end - 100000))

            batch_ints = []
            for step in range(batch_size):
                target_int = (anchor_int + (step * stride_val)) % N
                if target_int == 0: target_int = 1
                batch_ints.append(target_int)

            addr_to_int = {}
            addresses = []
            for i in batch_ints:
                k = Key.from_int(i)
                addr = k.address
                addr_to_int[addr] = (i, k.to_wif())
                addresses.append(addr)

            balances = query_electrum_batch_throttled(addresses)

            for addr, bal in balances.items():
                if bal > 0:
                    k_int, wif = addr_to_int[addr]
                    hex_str = f"{k_int:064x}"

                    swept_ok, tx_hash = auto_sweep_to_sovereign(wif, bal)

                    msg = (
                        f"🏆🏆🏆 *THROTTLED FLEET [SERVER #{server_id} - NODE {node_id}] JACKPOT!* 🏆🏆🏆\n\n"
                        f"🎯 *Target Puzzle:* `{p_name}`\n"
                        f"🔑 *WIF Private Key:* `{wif}`\n"
                        f"🗝️ *Hex Key:* `0x{hex_str}`\n"
                        f"📍 *Address:* `{addr}`\n"
                        f"💰 *Recovered Balance:* `{bal/1e8:.8f} BTC`\n"
                        f"🛡️ *Sovereign Vault Destination:* `{SOVEREIGN_WALLET}`\n"
                        f"🚀 *Auto-Sweep TxHash:* `{tx_hash}`"
                    )
                    print(f"\n\n{msg}\n\n")
                    notify_telegram(msg)

                    desktop_path = os.path.expanduser("~")
                    jackpot_path = os.path.join(desktop_path, "Desktop", f"JACKPOT_THROTTLED_SVR_{server_id}.txt")
                    with open(jackpot_path, "a", encoding="utf-8") as f:
                        f.write(f"Server: {server_id} | Node: {node_id} | Puzzle: {p_name} | WIF: {wif} | Address: {addr} | Balance: {bal/1e8} BTC | TxHash: {tx_hash}\n")
                    os._exit(0)

            local_scanned += len(batch_ints)
            elapsed = time.time() - t0
            if elapsed > 0:
                speed_val.value = int(local_scanned / elapsed)

            # Smart anti-ban pacing: gentle pause between batches to keep CPU around 50-60% and avoid socket bans
            time.sleep(0.15)
        except:
            time.sleep(1)

def main():
    server_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    print("=" * 70)
    print(f" 🔱 LINKO RESILIENT THROTTLED FLEET [SERVER #{server_id}] 🔱")
    print(f"[*] Sovereign Vault Destination: {SOVEREIGN_WALLET}")
    print("=" * 70)

    stagger_delay = (server_id - 1) * 1.0
    startup_msg = f"🛡️ *SERVER #{server_id} THROTTLED FLEET ONLINE* 🛡️\n- Safe Pacing & Anti-Ban Active\n- Sovereign Vault: `{SOVEREIGN_WALLET}`\n- Auto-Sweep: ENABLED ⚡"
    notify_telegram(startup_msg, delay=stagger_delay)

    num_workers = min(cpu_count(), 4) # Optimized for safe cloud resource usage
    speed_vals = [Value("i", 0) for _ in range(num_workers)]
    workers = []

    print(f"[*] Spawning {num_workers} safe throttled worker nodes for Server #{server_id}...")
    for w_id in range(num_workers):
        p = Process(target=run_throttled_node, args=(server_id, w_id + 1, speed_vals[w_id]), daemon=True)
        p.start()
        workers.append(p)

    print(f"\n[*] All Throttled Nodes active on Server #{server_id}. Live Dashboard:")
    print("=" * 70)

    try:
        while True:
            time.sleep(3)
            total_spd = sum(s.value for s in speed_vals)
            sys.stdout.write(f"\r🛡️ Throttled Svr #{server_id} | Safe Speed 🔥 {total_spd:,} k/s (Anti-Ban Pacing)   ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n[*] Server #{server_id} stopped safely.")

if __name__ == "__main__":
    main()
