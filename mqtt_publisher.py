import yaml, json, time, threading
import paho.mqtt.client as mqtt
from ecdh_handler import ECDHHandler
from aes_gcm_handler import AESGCMHandler

conf = yaml.safe_load(open('config.yaml'))

class MQTTSubAutoKeyRotation:
    def __init__(self):
      self.client = mqtt.Client(transport="tcp",protocol=mqtt.MQTTv5,callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
      self.client.connect(conf['mqtt']['broker'], conf['mqtt']['port'], conf['mqtt']['keepalive'])
      self.client.loop_start()
      self.ecdh = ECDHHandler()
      self.aes = None
      self.peer_pub = None
      self.topic = conf['mqtt']['topic']
      self.ecdh_topic = conf['key_rotation']['ecdh_topic']
      self.client.on_message = self.on_msg
      self.client.subscribe(self.topic)
      self.client.subscribe(self.ecdh_topic)
      self.publish_pubkey()
      self.start_rotation_timer()

    def publish_pubkey(self):
        time.sleep(1)
        self.client.publish(self.ecdh_topic, self.ecdh.get_pub(),retain=True)

    def on_msg(self, client, userdata, msg):
        if msg.topic == self.ecdh_topic:
            peer_key = msg.payload.decode()
            if peer_key != self.ecdh.get_pub():
                self.peer_pub = peer_key
                derived = self.ecdh.derive_shared(self.peer_pub)
                self.aes = AESGCMHandler(derived)
        elif self.aes and msg.topic == self.topic:
            payload = json.loads(msg.payload.decode())
            try:
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
