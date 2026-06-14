import os
import hashlib
import logging
import threading
import time
from flask import Flask, jsonify, send_file, request
from web3 import Web3

# ================= CONFIG =================

CONFIG = {
    "GANACHE_URL": os.environ.get("GANACHE_URL", "http://127.0.0.1:7545"),
    "CONTRACT_ADDRESS": os.environ.get("CONTRACT_ADDRESS", "YOUR_CONTRACT_ADDRESS"),
    "ACCOUNT_ADDRESS": os.environ.get("ACCOUNT_ADDRESS", "YOUR_ACCOUNT_ADDRESS"),
    "PRIVATE_KEY": os.environ.get("PRIVATE_KEY", ""),  # Never hardcode this
    "MY_IP": os.environ.get("MY_IP", "127.0.0.1"),
    "MY_PORT": 5000,
    "FIRMWARE_FILE": "firmware_v1.0.3.bin",
    "FIRMWARE_VERSION": "1.0.3",
    "DEVICE_TYPE": "ESP32",
}

# ================= ABI =================

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_version", "type": "string"},
            {"internalType": "string", "name": "_hash", "type": "string"},
            {"internalType": "string", "name": "_url", "type": "string"},
            {"internalType": "string", "name": "_deviceType", "type": "string"},
            {"internalType": "string", "name": "_signature", "type": "string"},
        ],
        "name": "registerFirmware",
        "outputs": [{"internalType": "bytes32", "name": "firmwareId", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getFirmwareCount",
        "outputs": [{"internalType": "uint256", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getLogCount",
        "outputs": [{"internalType": "uint256", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_index", "type": "uint256"}],
        "name": "getDeviceLog",
        "outputs": [
            {"internalType": "string", "type": "string"},
            {"internalType": "string", "type": "string"},
            {"internalType": "bool", "type": "bool"},
            {"internalType": "uint256", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_deviceId", "type": "string"},
            {"internalType": "string", "name": "_firmwareVersion", "type": "string"},
            {"internalType": "bool", "name": "_success", "type": "bool"},
        ],
        "name": "logDeviceUpdate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# ================= GLOBALS =================

w3 = None
contract = None

# ================= LOGGING =================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Broker")

# ================= STATUS =================

status = {
    "firmware_version": CONFIG["FIRMWARE_VERSION"],
    "firmware_hash": "",
    "firmware_url": "",
    "device_logs": [],
}

# ================= HELPERS =================

def calculate_hash(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha.update(f.read())
    return sha.hexdigest()

def connect_blockchain():
    global w3, contract
    w3 = Web3(Web3.HTTPProvider(CONFIG["GANACHE_URL"]))

    if not w3.is_connected():
        log.error("❌ Cannot connect to Ganache")
        return

    log.info("✅ Connected to Ganache")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONFIG["CONTRACT_ADDRESS"]),
        abi=CONTRACT_ABI,
    )

# ================= FLASK =================

app = Flask(__name__)

@app.route("/api/firmware/hash")
def get_hash():
    return jsonify({
        "version": status["firmware_version"],
        "hash": status["firmware_hash"],
        "url": status["firmware_url"],
    })

@app.route("/api/firmware/download")
def download():
    return send_file(CONFIG["FIRMWARE_FILE"], as_attachment=True)

@app.route("/api/log", methods=["POST"])
def receive_log():
    data = request.get_json()
    log.info(f"Log received: {data}")

    status["device_logs"].append(data)

    try:
        nonce = w3.eth.get_transaction_count(CONFIG["ACCOUNT_ADDRESS"])

        tx = contract.functions.logDeviceUpdate(
            data["device_id"],
            data["version"],
            data["success"]
        ).build_transaction({
            "from": CONFIG["ACCOUNT_ADDRESS"],
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("1", "gwei"),
        })

        signed = w3.eth.account.sign_transaction(tx, CONFIG["PRIVATE_KEY"])
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        log.info("✅ Logged to blockchain")

    except Exception as e:
        log.error(f"Blockchain log error: {e}")

    return jsonify({"ok": True})

# ================= MAIN =================

if __name__ == "__main__":

    # Create dummy firmware if not exists
    if not os.path.exists(CONFIG["FIRMWARE_FILE"]):
        with open(CONFIG["FIRMWARE_FILE"], "wb") as f:
            f.write(b"BW_VER: 1.0.3\n" + b"\x00" * 1024)

    fw_hash = calculate_hash(CONFIG["FIRMWARE_FILE"])
    fw_url = f"http://{CONFIG['MY_IP']}:{CONFIG['MY_PORT']}/api/firmware/download"

    status["firmware_hash"] = fw_hash
    status["firmware_url"] = fw_url

    connect_blockchain()

    print("🚀 Broker running...")
    app.run(host="0.0.0.0", port=CONFIG["MY_PORT"])
