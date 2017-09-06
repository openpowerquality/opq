import ngrok

class NgrokConnector:

    def __init__(self):
        try:
            tunnels = ngrok.client.get_tunnels()
            self.success = True
        except:
            self.success = False

    def getTunnelName(self):
        try:
            self.success = True
            return ngrok.client.get_tunnels()[0].public_url
        except:
            self.success = False
            return None