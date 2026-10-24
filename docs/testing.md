
# Testing and Performance Analysis

## 1. Objective

The purpose of testing is to evaluate UDP packet delivery and
observe how the SDN-controlled network responds when a link fails.

## 2. Test environment

Record the actual environment used for the experiment:

- Operating system:
- Python version:
- Mininet version:
- SDN controller:
- Number of hosts:
- Network topology:
- UDP sender and receiver configuration:

## 3. Test cases

### Test 1: Normal UDP transmission

Send UDP packets through the network while all required links are available.
Record the number of packets sent and received, packet loss, and duration.

### Test 2: Link failure

Start UDP traffic and disable the selected network link.
Observe packet delivery and whether the controller selects an alternate path.
Record the number of lost packets and the time taken for recovery, if measurable.

### Test 3: Recovery and continued transmission

After the network reroutes traffic, check whether packets continue reaching
the receiver. Record the measured results and any errors.

## 4. Metrics

- Packets sent
- Packets received
- Packets lost
- Packet-loss percentage
- Test duration
- Recovery time, where measurable

Packet-loss percentage = (packets lost / packets sent) * 100

Recovery time is the measured interval between the defined failure event
and the observed recovery event. State exactly how both events were detected.

## 5. Results

Insert the results table generated from the actual experiment.
Include graphs for packet loss and recovery time where measurements are available.

Do not report expected or sample values as experimental results.

## 6. Observations

Describe what happened in each test.
Compare normal transmission with the link-failure scenario.
Explain whether rerouting was observed and how the measured results support
your conclusion.

## 7. Reproducibility

Document the commands used to start the controller, launch the topology,
start the sender and receiver, trigger a link failure, and collect results.

## 8. Limitations

Mention any test that could not be completed, any missing measurements,
and any assumptions made during the experiment.

## Mininet UDP Packet-Loss Test

### Test Setup
- Topology: Mininet with sender `h1` and receiver `h2`
- Sender IP: `10.0.0.1`
- Receiver IP: `10.0.0.2`
- Protocol: UDP
- Simulated packet loss: 30% using Linux `tc netem` on `h1-eth0`
- Packets requested: 10
- ACK timeout: 1 second
- Maximum retries per packet: 5

### Results
- Packets requested: 10
- Packets acknowledged: 10
- Unacknowledged packets: 0
- Retransmissions: 6
- Sender run ID: `8efe090da8d6`

### Conclusion
In this test, the sender successfully delivered all 10 packets despite simulated network loss. Six retransmissions were recorded, demonstrating the sender's retry and acknowledgement mechanism. The test was performed in Mininet, not on a physical network.
