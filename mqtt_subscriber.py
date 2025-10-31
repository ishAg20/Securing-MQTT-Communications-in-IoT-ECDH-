import yaml, json, threading
import paho.mqtt.client as mqtt
from ecdh_handler import ECDHHandler
from aes_gcm_handler import AESGCMHandler

conf = yaml.safe_load(open('config.yaml'))

class MQTTSubAutoKeyRotation:
    def __init__(self):
        self.client = mqtt.Client(
            transport="tcp",
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.client.connect(conf['mqtt']['broker'], conf['mqtt']['port'], conf['mqtt']['keepalive'])
        self.client.loop_start()
        self.ecdh = ECDHHandler()
        self.aes = None
        self.peer_pub = None
        self.topic = conf['mqtt']['topic']
        self.ecdh_topic = conf['key_rotation']['ecdh_topic']

        # Subscribe to both topics
        self.client.subscribe([(self.topic, 0), (self.ecdh_topic, 0)])

        # Use one unified callback
        self.client.on_message = self.on_message

        self.publish_pubkey()
        self.start_rotation_timer()

    def publish_pubkey(self):
        self.client.publish(self.ecdh_topic, self.ecdh.get_pub())

    def on_message(self, client, userdata, msg):
        if msg.topic == self.ecdh_topic:
            self.handle_key_msg(msg)
        elif msg.topic == self.topic:
            self.handle_data_msg(msg)

    def handle_key_msg(self, msg):
        peer_key = msg.payload.decode()
        if peer_key != self.ecdh.get_pub():
            self.peer_pub = peer_key
            derived = self.ecdh.derive_shared(self.peer_pub)
            self.aes = AESGCMHandler(derived)

    def handle_data_msg(self, msg):
        if not self.aes:
            print("Waiting for key exchange before decrypting.")
            return
        try:
            payload = json.loads(msg.payload.decode())
            data = self.aes.decrypt(payload)
            print("Received:", data)
        except Exception as e:
            print("Decryption error:", e)

    def rotate_keys(self):
        self.ecdh.regenerate_keys()
        self.publish_pubkey()
        if self.peer_pub:
            derived = self.ecdh.derive_shared(self.peer_pub)
            self.aes = AESGCMHandler(derived)
        threading.Timer(conf['key_rotation']['interval_seconds'], self.rotate_keys).start()

    def start_rotation_timer(self):
        threading.Timer(conf['key_rotation']['interval_seconds'], self.rotate_keys).start()


if __name__ == "__main__":
    MQTTSubAutoKeyRotation()
