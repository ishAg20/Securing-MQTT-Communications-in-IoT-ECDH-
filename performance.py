import time, json, os
from aes_gcm_handler import AESGCMHandler
from ecdh_handler import ECDHHandler
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
import seaborn as sns

conf = yaml.safe_load(open('config.yaml'))
dataset = pd.read_csv(conf['dataset']['file']).sample(conf['dataset']['sample_size'])

def benchmark_aes_gcm(sim_iterations=1):
    key_latencies, enc_times, dec_times, overheads = [], [], [], []
    for _ in range(sim_iterations):
        # Simulate ECDH key exchange per session
        alice, bob = ECDHHandler(), ECDHHandler()
        alice_peer, bob_peer = bob.get_pub(), alice.get_pub()
        alice_aes_key = alice.derive_shared(alice_peer)
        bob_aes_key = bob.derive_shared(bob_peer)
        handlerA = AESGCMHandler(alice_aes_key)
        handlerB = AESGCMHandler(bob_aes_key)
        for _, row in dataset.iterrows():
            payload = row[conf['dataset']['features']].to_dict()
            start_enc = time.time()
            enc = handlerA.encrypt(payload)
            enc_time = (time.time() - start_enc) * 1000
            enc_size = len(json.dumps(enc).encode('utf-8'))
            plain_size = len(json.dumps(payload).encode('utf-8'))
            overheads.append(enc_size - plain_size)
            enc_times.append(enc_time)

            # Decrypt on other side
            start_dec = time.time()
            dec = handlerB.decrypt(enc)
            dec_time = (time.time() - start_dec) * 1000
            dec_times.append(dec_time)

    return {
        'avg_enc_ms': np.mean(enc_times),
        'std_enc_ms': np.std(enc_times),
        'avg_dec_ms': np.mean(dec_times),
        'std_dec_ms': np.std(dec_times),
        'avg_overhead_bytes': np.mean(overheads),
        'throughput_ops_per_sec': len(dataset) * sim_iterations / (np.sum(enc_times)/1000),
        'raw_enc_times': enc_times,
        'raw_dec_times': dec_times,
        'raw_overheads': overheads,
    }

def plot_results(results):
    plt.figure(figsize=(8,6))
    sns.histplot(results['raw_enc_times'], bins=30, label='Encryption', color='blue', kde=True)
    sns.histplot(results['raw_dec_times'], bins=30, label='Decryption', color='orange', kde=True)
    plt.legend()
    plt.title('AES-GCM Encryption/Decryption Latency Distribution')
    plt.xlabel('Time (ms)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('aes_gcm_performance.png')
    plt.show()

if __name__ == "__main__":
    print("Running AES-GCM with ECDH Key Exchange Performance Benchmark...")
    results = benchmark_aes_gcm()
    print(f"Average encryption time: {results['avg_enc_ms']:.2f} ms")
    print(f"Average decryption time: {results['avg_dec_ms']:.2f} ms")
    print(f"Average ciphertext size overhead: {results['avg_overhead_bytes']:.1f} bytes")
    print(f"Estimated throughput: {results['throughput_ops_per_sec']:.1f} ops/sec")
    plot_results(results)
