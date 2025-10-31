# Securing MQTT Communications in IoT with ECDH Key Exchange, AES-GCM Encryption, and Automatic Key Rotation

## Overview

This project secures MQTT-based IoT communications by:

- Using **ECDH (Elliptic Curve Diffie-Hellman)** for establishing a shared AES key between publisher and subscriber over the broker.
- Encrypting all messages with **AES-GCM** for confidentiality and integrity.
- **Automatically rotating encryption keys** at configurable intervals for strong forward secrecy.

## Main Features

- No pre-shared key files: session keys are negotiated using public key cryptography.
- Every `interval_seconds` (see `config.yaml`), both parties re-generate ECDH key pairs and derive fresh AES keys.
- Keys are never reused or stored long-term; keys are exchanged over MQTT using a dedicated topic (e.g., `ton_iot/keyex`).
- Legacy modes (CBC, static AES keys) are fully deprecated.

## File Structure

- `ecdh_handler.py`: ECC/ECDH logic for public key management and shared secret extraction.
- `aes_gcm_handler.py`: AES-GCM encryption/decryption logic, takes ECDH-derived keys.
- `mqtt_publisher.py`: Publishes telemetry securely; handles ECDH exchange and key rotation.
- `mqtt_subscriber.py`: Subscribes for telemetry; handles ECDH exchange and key rotation.
- `performance.py`: Benchmarks AES-GCM encryption/decryption times and message overhead. (See below)
- `config.yaml`: Configuration for MQTT broker, topics, key rotation, dataset, etc.
- `requirements.txt`: Required Python packages.

## Usage

1. **Install requirements**:  
   `pip install -r requirements.txt`
2. **Edit `config.yaml`** to fit your MQTT broker, topic, and rotation needs.

3. **Start publisher and subscriber** (in separate shells):
   `python mqtt_publisher.py
python mqtt_subscriber.py`

## Performance Evaluation

Run:
`python performance.py`
This script runs AES-GCM encryption/decryption performance benchmarks and reports average latency, overhead, and throughput using a representative IoT dataset.

## Security Notes

- Only **elliptic-curve-based key exchange** and **AES-GCM** are supported for maximal security.
- Automatic and frequent rekeying ensures messages maintain forward secrecy.
