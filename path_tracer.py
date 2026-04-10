from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class PathTracer(object):
    def __init__(self):
        core.openflow.addListeners(self)
        self.mac_to_port = {}
        self.paths = {}

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet: return

        dpid = event.dpid
        src_mac = str(packet.src)
        dst_mac = str(packet.dst)

        # --- 1. FIREWALL: Block h2 (Requirement: Allowed vs Blocked) ---
        if src_mac == "00:00:00:00:00:02":
            log.warning("FIREWALL: Dropping traffic from h2 (%s)", src_mac)
            return # DROP

        # --- 2. ARP HANDLING: Allow hosts to discover each other ---
        if packet.type == packet.ARP_TYPE:
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            event.connection.send(msg)
            return

        # --- 3. PATH TRACKING: (Requirement: Identify Path) ---
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = event.port
        
        key = (src_mac, dst_mac)
        self.paths.setdefault(key, [])
        if not self.paths[key] or self.paths[key][-1] != dpid:
            self.paths[key].append(dpid)

        # --- 4. FORWARDING: (Requirement: Display Route) ---
        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]
            
            # Print the path trace only when reaching the destination switch
            if dpid == 3 or dpid == 1:
                sw_path = " -> ".join([f"s{int(str(x)[-1])}" for x in self.paths[key]])
                log.info("PATH TRACED: %s -> %s | Route: %s", src_mac, dst_mac, sw_path)

            # Install Explicit Flow Rule (Match-Action)
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port=out_port))
            event.connection.send(msg)
        else:
            out_port = of.OFPP_FLOOD

        # Send packet out
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(msg)

def launch():
    core.registerNew(PathTracer)
