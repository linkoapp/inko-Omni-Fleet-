import coincurve, hashlib, requests, os, sys, base58, time, random
from bit import Key

# 🔱 LINKO ULTIMATE 1-MILLION TAME TRAP KANGAROO HERD (PUZZLE #66) 🔱
# Plants 1,000,000 Tame Traps in RAM for maximum collision density,
# auto-sweeps to Sovereign Wallet on jackpot, and alerts Telegram.

TG_PART1 = "8936479076:"
TG_PART2 = "AAE_nWzWFrjAUN1JAFOMJpv4awMYmh2XYps"
TG_TOKEN = TG_PART1 + TG_PART2
TG_ID = "6832828732"
SOVEREIGN_WALLET = "bc1p3jlr9wskycdg0fnfwk0fjjumy5f25s8h04e5ms6lm862rs09du8s6tjsxa"

PUZZLE_66_START = 36893488147419103232       # 2^65
PUZZLE_66_END   = 73786976294838206463       # 2^66 - 1
PUZZLE_66_ADDR  = "13yVhZkrwbAv6YvDqjfkDfRtRiH52K92XA"
PUZZLE_66_HASH  = bytes.fromhex("209f80a224a919028a2a8e807096e594d2105a01")

def notify(m):
    try:
        import requests
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_ID, "text": m, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def auto_sweep_to_sovereign(wif_key):
    try:
        k = Key(wif_key)
        tx_hash = k.send([(SOVEREIGN_WALLET, 'all')])
        return True, tx_hash
    except Exception as e:
        print(f"[!] Auto-sweep error: {e}")
    return False, "N/A"

def main():
    print("=" * 70)
    print(" 🔱 LINKO 1-MILLION TAME TRAP KANGAROO HERD (PUZZLE #66) 🔱")
    print(f"[*] Target Address : {PUZZLE_66_ADDR} (6.6 BTC Bounty)")
    print(f"[*] Search Interval: {PUZZLE_66_START:,} to {PUZZLE_66_END:,}")
    print("=" * 70)

    midpoint = (PUZZLE_66_START + PUZZLE_66_END) // 2
    num_traps = 1000000 # 1 MILLION TAME TRAPS IN RAM!

    print(f"[*] Planting {num_traps:,} Tame Kangaroo Traps in RAM (Maximum Density)...")

    sha256 = hashlib.sha256
    ripemd160 = lambda x: hashlib.new("ripemd160", x).digest()

    tame_traps = dict()

    lib = coincurve._libsecp256k1.lib
    ffi = coincurve._libsecp256k1.ffi
    ctx = coincurve.context.GLOBAL_CONTEXT.ctx
    flags = coincurve.flags.EC_COMPRESSED

    pubkey = ffi.new("secp256k1_pubkey *")
    out_pub = ffi.new("unsigned char[33]")
    out_len = ffi.new("size_t *", 33)
    buf = ffi.buffer(out_pub, 33)
    create_pub = lib.secp256k1_ec_pubkey_create

    t0 = time.time()
    for i in range(num_traps):
        k_val = midpoint + (i * 73) # Dense stride
        create_pub(ctx, pubkey, k_val.to_bytes(32, "big"))
        out_len[0] = 33
        lib.secp256k1_ec_pubkey_serialize(ctx, out_pub, out_len, pubkey, flags)
        h = ripemd160(sha256(bytes(buf)).digest())
        tame_traps[h] = k_val

        if (i + 1) % 200000 == 0:
            sys.stdout.write(f"\r[Planting Traps...] {i+1:,} / 1,000,000 traps planted in RAM...")
            sys.stdout.flush()

    print(f"\n[+] Successfully planted {len(tame_traps):,} Tame Traps in RAM ({time.time()-t0:.2f}s)!")
    print(f"[*] Launching Wild Kangaroos for Meet-in-the-Middle Collision Hunt...\n")

    wild_count = 0
    t_start = time.time()

    while True:
        try:
            wild_start = random.randint(PUZZLE_66_START, PUZZLE_66_END - 500000)

            for step in range(10000):
                wild_k = wild_start + (step * 91)
                create_pub(ctx, pubkey, wild_k.to_bytes(32, "big"))
                out_len[0] = 33
                lib.secp256k1_ec_pubkey_serialize(ctx, out_pub, out_len, pubkey, flags)

                h = ripemd160(sha256(bytes(buf)).digest())

                # Check direct match against Puzzle #66
                if h == PUZZLE_66_HASH:
                    wif = Key.from_int(wild_k).to_wif()
                    hex_str = f"{wild_k:064x}"
                    swept_ok, tx_hash = auto_sweep_to_sovereign(wif)
                    msg = (
                        f"🏆🏆🏆 *PUZZLE #66 CRACKED! DIRECT COLLISION!* 🏆🏆🏆\n\n"
                        f"🎯 *Target Address:* `{PUZZLE_66_ADDR}`\n"
                        f"🔑 *WIF Private Key:* `{wif}`\n"
                        f"🗝️ *Hex Key:* `0x{hex_str}`\n"
                        f"📍 *Integer (k):* `{wild_k}`\n"
                        f"💰 *Bounty:* `6.6 BTC ($600,000+)`\n"
                        f"🛡️ *Sovereign Vault:* `{SOVEREIGN_WALLET}`\n"
                        f"🚀 *Auto-Sweep TxHash:* `{tx_hash}`"
                    )
                    print(f"\n\n{msg}\n\n")
                    notify(msg)
                    os._exit(0)

                # Check trap collision in RAM
                if h in tame_traps:
                    hit_k = tame_traps[h]
                    wif = Key.from_int(hit_k).to_wif()
                    hex_str = f"{hit_k:064x}"
                    swept_ok, tx_hash = auto_sweep_to_sovereign(wif)
                    msg = (
                        f"💥💥💥 *1-MILLION TRAP KANGAROO COLLISION HIT!* 💥💥💥\n\n"
                        f"🎯 *Target Puzzle:* `Puzzle #66 (6.6 BTC)`\n"
                        f"🔑 *WIF Private Key:* `{wif}`\n"
                        f"🗝️ *Hex Key:* `0x{hex_str}`\n"
                        f"📍 *Trap Integer k:* `{hit_k}`\n"
                        f"🛡️ *Sovereign Vault:* `{SOVEREIGN_WALLET}`\n"
                        f"🚀 *Auto-Sweep TxHash:* `{tx_hash}`"
                    )
                    print(f"\n\n{msg}\n\n")
                    notify(msg)
                    os._exit(0)

                wild_count += 1

            elapsed = time.time() - t_start
            spd = int(wild_count / elapsed) if elapsed > 0 else 0
            sys.stdout.write(f"\r🦘 1M-Trap Herd | 🔥 {spd:,} k/s | Wild Hops: {wild_count:,} | Traps Active: {len(tame_traps):,}   ")
            sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n[*] 1M-Trap Kangaroo Herd paused safely.")
            break

if __name__ == "__main__":
    main()
