#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def run():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink,
                  autoSetMacs=False, build=False)
    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    h1 = net.addHost("h1", ip="10.0.0.1/24", mac="00:00:00:00:00:01")
    h2 = net.addHost("h2", ip="10.0.0.2/24", mac="00:00:00:00:00:02")

    s1 = net.addSwitch("s1", dpid="0000000000000001", protocols="OpenFlow13")
    s2 = net.addSwitch("s2", dpid="0000000000000002", protocols="OpenFlow13")
    s3 = net.addSwitch("s3", dpid="0000000000000003", protocols="OpenFlow13")
    s4 = net.addSwitch("s4", dpid="0000000000000004", protocols="OpenFlow13")

    # Keep this order: the controller uses the resulting switch port numbers.
    net.addLink(h1, s1)  # s1 port 1: h1
    net.addLink(s1, s2)  # s1 port 2; s2 port 1
    net.addLink(s1, s3)  # s1 port 3; s3 port 1
    net.addLink(s2, s4)  # s2 port 2; s4 port 1 (primary path)
    net.addLink(s3, s4)  # s3 port 2; s4 port 2 (alternate path)
    net.addLink(s4, h2)  # s4 port 3: h2

    net.build()
    for sw in (s1, s2, s3, s4):
        sw.start([net.controllers[0]])

    info("*** Network is ready. Run pingall, then start receiver/sender.\n")
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
