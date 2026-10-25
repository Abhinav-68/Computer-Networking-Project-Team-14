from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import ether_types

class PacketLossRecoveryController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # DPID -> output port for traffic whose destination is h2 or h1.
    PRIMARY_TO_H2 = {1: 2, 2: 2, 4: 3}
    ALTERNATE_TO_H2 = {1: 3, 3: 2, 4: 3}
    PRIMARY_TO_H1 = {4: 1, 2: 1, 1: 1}
    ALTERNATE_TO_H1 = {4: 2, 3: 1, 1: 1}

    # Ports belonging to the primary path. If any goes down, use the alternate.
    PRIMARY_PORTS = {(1, 2), (2, 1), (2, 2), (4, 1)}

    def __init__(self, *args, **kwargs):
        super(PacketLossRecoveryController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.failed_primary_ports = set()
        self.mode = "primary"

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        self.datapaths[dp.id] = dp
        self.logger.info("Switch connected: s%d", dp.id)
        self.install_all_routes()

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, CONFIG_DISPATCHER])
    def state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
        elif ev.state == CONFIG_DISPATCHER:
            self.datapaths[dp.id] = dp

    def add_flow(self, dp, priority, match, actions):
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        instructions = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp, priority=priority, match=match,
            instructions=instructions
        )
        dp.send_msg(mod)

    def delete_flows(self, dp):
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        mod = parser.OFPFlowMod(
            datapath=dp,
            command=ofp.OFPFC_DELETE,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            match=parser.OFPMatch()
        )
        dp.send_msg(mod)

    def install_destination_rule(self, dp, dst_ip, out_port, is_arp=False):
        parser = dp.ofproto_parser
        if is_arp:
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP, arp_tpa=dst_ip)
        else:
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_dst=dst_ip)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(dp, 100, match, actions)

    def install_all_routes(self):
        if not self.datapaths:
            return

        if self.failed_primary_ports:
            to_h2 = self.ALTERNATE_TO_H2
            to_h1 = self.ALTERNATE_TO_H1
            self.mode = "alternate"
        else:
            to_h2 = self.PRIMARY_TO_H2
            to_h1 = self.PRIMARY_TO_H1
            self.mode = "primary"

        self.logger.info("Installing %s route", self.mode)

        # Clear old rules on all connected switches before installing the new set.
        for dp in list(self.datapaths.values()):
            self.delete_flows(dp)

        # Rules toward h2 and toward h1; both IPv4 and ARP are covered.
        for dpid, dp in list(self.datapaths.items()):
            if dpid in to_h2:
                self.install_destination_rule(dp, "10.0.0.2", to_h2[dpid], False)
                self.install_destination_rule(dp, "10.0.0.2", to_h2[dpid], True)
            if dpid in to_h1:
                self.install_destination_rule(dp, "10.0.0.1", to_h1[dpid], False)
                self.install_destination_rule(dp, "10.0.0.1", to_h1[dpid], True)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        port_no = msg.desc.port_no
        ofp = dp.ofproto

        if (dp.id, port_no) not in self.PRIMARY_PORTS:
            return

        is_down = bool(msg.desc.state & ofp.OFPPS_LINK_DOWN)
        key = (dp.id, port_no)
        old_mode = self.mode

        if is_down:
            self.failed_primary_ports.add(key)
        else:
            self.failed_primary_ports.discard(key)

        new_mode = "alternate" if self.failed_primary_ports else "primary"
        self.logger.info("Port status: switch=%s port=%s down=%s", dp.id, port_no, is_down)

        if new_mode != old_mode:
            self.logger.warning("Primary path state changed; switching to %s", new_mode)
            self.install_all_routes()
