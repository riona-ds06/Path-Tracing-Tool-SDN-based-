Title: 
Path Tracing Tool (SDN-based)

Problem Statement: 
Identify and display the path taken by packets.

Objectives:
Track flow rules 
Identify forwarding path
Display route 
Validate using tests


Installation:
Clone the POX repository: git clone https://github.com
Place path_tracer.py in the pox/ext/ directory.
Place topo.py in your main project folder.

Execution:
Start the POX Controller:
./pox.py log.level --INFO path_tracer

Launch the Mininet Topology:
sudo mn --custom topo.py --topo pathtopo --controller remote

Configure Secure Mode (Ensures firewall enforcement):
In a separate terminal, run:
sudo ovs-vsctl set-fail-mode s1 secure
sudo ovs-vsctl set-fail-mode s2 secure
sudo ovs-vsctl set-fail-mode s3 secure

Expected Output & Validation:
Scenario 1: Allowed vs. Blocked (Security Test)
Test: h2 ping -c 1 h3
Expected Result: 100% Packet Loss. The POX terminal logs: FIREWALL: Dropping traffic from h2.
Validation: Proves the controller can enforce access control at the ingress switch.

Scenario 2: Path Identification
Test: h1 ping -c 1 h3
Expected Result: Successful ping. The POX terminal logs: PATH TRACED: h1 -> s1 -> s2 -> s3 -> h3.
Validation: Demonstrates real-time tracking of switch hops across the control plane.

Scenario 3: Match-Action Flow Rules
Test: Run sudo ovs-ofctl dump-flows s1 during active traffic.
Expected Result: Display of explicit OpenFlow entries showing specific MAC matches and output port actions.
Validation: Confirms that the controller successfully pushes rules to the data plane.

Scenario 4: Normal vs. Failure
Test: mininet> link s1 s2 down, then h1 ping h3.
Expected Result: Immediate "Destination Host Unreachable."
Validation: Validates that path tracing and connectivity are dependent on physical link availability.
