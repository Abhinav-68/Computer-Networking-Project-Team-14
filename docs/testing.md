
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

