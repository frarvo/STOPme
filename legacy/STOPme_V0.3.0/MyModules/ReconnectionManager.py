import time
from bluepy.btle import BTLEDisconnectError


class BlueCoinReconnectionManager:
    def __init__(self, node):
        print("Reconnection manager instantiated")
        self._node = node

    def get_node(self):
        return self._node

    def reconnect(self):
        node = self.get_node()
        node_name = node.get_name()
        print("Trying to re-establish connection to device %s" % node_name)
        while True:
            print("Attempting reconnection to %s" % node_name)
            try:
                if not node.connect():
                    print("Reconnection to %s failed" % node_name)
                    print(node.get_status())
                else:
                    print("Reconnection to %s successful" % node_name)
                    print(node.get_status())
                    break

            except BTLEDisconnectError:
                print("Reconnection failed due to an exception")
            time.sleep(1)