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

## Quickstart: Step-by-Step Setup

### Clone the Repository
git clone https://github.com/ishAg20/Securing-MQTT-Communications-in-IoT

cd mqtt-aes

### Download the TON-IoT Dataset
- Visit [TON-IoT Datasets](https://unsw-my.sharepoint.com/personal/z5025758_ad_unsw_edu_au/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fz5025758%5Fad%5Funsw%5Fedu%5Fau%2FDocuments%2FTON%5FIoT%20datasets%2FTrain%5FTest%5Fdatasets%2FTrain%5FTest%5FIoT%5Fdataset&ga=1)
- Download `Train_Test_IoT_Fridge.csv`
- Place the file inside the `mqtt-aes/` directory

### Create the Keys Directory
mkdir keys

### Install Python Dependencies
pip install -r requirements.txt

### Preview the Dataset
python dataset.py

### Benchmark AES Overheads & Visualize
python performance.py

This runs tests for all configurations and generates a PNG visualization (`aes_performance_analysis.png`). The visualizations open automatically.

### Run MQTT Subscriber (Listener) in One Terminal
python mqtt_subscriber.py

Receives encrypted telemetry, decrypts it, and prints latency stats live.

### Run MQTT Publisher (in Another Terminal)
python mqtt_publisher.py

Publishes encrypted telemetry with various configurations; displays encryption time and size statistics.

## MQTT Broker Integration

By default, the scripts connect to `localhost:1883` (this can be changed in `config.yaml`).  
Recommended: Install and test with Mosquitto.

Example installation and running Mosquitto on Ubuntu/Debian:
sudo apt install mosquitto mosquitto-clients
mosquitto -v


You can monitor MQTT traffic using Mosquitto CLI:
mosquitto_sub -h localhost -p 1883 -t 'ton_iot/telemetry'

## Security Notes

- Only **elliptic-curve-based key exchange** and **AES-GCM** are supported for maximal security.
- Automatic and frequent rekeying ensures messages maintain forward secrecy.
