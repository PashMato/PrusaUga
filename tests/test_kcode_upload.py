# python 3.6

import random
import time
import numpy as np

from paho.mqtt import client as mqtt_client

KCODE_TOPIC = "/prusa_uga/kcode"

broker = '192.168.20.197'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'kcode-upload-tester-{random.randint(0, 1000)}'
username = password = ''
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg):
    result = client.publish(KCODE_TOPIC, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{KCODE_TOPIC}`")
    else:
        print(f"Failed to send message to topic {KCODE_TOPIC}")


def make_kcode(xyz: np.ndarray, t: np.ndarray):
    """Generate a k-code from an N*4 np.int16 buffer"""
    assert len(xyz.shape) == 2, "Should be a 2D array"
    assert xyz.shape[1] == 3, "Must be N*3"
    num_rows = len(xyz)
    assert num_rows == len(t), "XYZ and t must be the same length"
    xyz32 = xyz.astype(np.int32)
    xyz16 = xyz.astype(np.int16)
    assert (xyz32 == xyz16.astype(np.int32)).all(), "Overflow!"
    v_min = xyz16.min(axis=0)
    v_max = xyz16.max(axis=0)
    header = np.array([num_rows, v_min[0], v_max[0], v_min[1], v_max[1]], dtype=np.int32).tobytes()
    t16 = np.frombuffer(t.astype(np.uint32).tobytes(), dtype=np.int16).reshape((num_rows, 2))
    # s16 = np.zeros((num_rows, 1), dtype=np.int16) + 7

    pos_16 = np.c_[xyz16, t16].T.tobytes()
    return header + pos_16


def run():
    client = connect_mqtt()
    client.loop_start()
    xyz = np.arange(27).reshape((-1, 3))
    t = np.arange(len(xyz)) * 100 + 7
    msg = make_kcode(xyz, t)
    publish(client, msg)


if __name__ == '__main__':
    run()
