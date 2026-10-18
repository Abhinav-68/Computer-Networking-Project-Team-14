"""
Mininet Topology with redundant paths for SDN rerouting:
         s2 (Primary)
       /    \
h1 - s1      s3 - h2
       \    /
         s4 (Alternate)
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

class RedundantTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

        # Add switches
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')
        s3 = self.addSwitch('s3', protocols='OpenFlow13')
        s4 = self.addSwitch('s4', protocols='OpenFlow13')

        # Host-to-Switch links
        self.addLink(h1, s1)
        self.addLink(h2, s3)

        # Inter-switch links (Primary: s1-s2-s3; Alternate: s1-s4-s3)
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s1, s4)
        self.addLink(s4, s3)

topos = {'redundant': (lambda: RedundantTopo())}

if __name__ == '__main__':
    setLogLevel('info')
    topo = RedundantTopo()
    # Point to the local Ryu controller (default OpenFlow port: 6653/6633)
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None, autoSetMacs=True)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    net.start()
    CLI(net)
    net.stop()
