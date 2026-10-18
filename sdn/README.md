```markdown
# SDN Controller & Redundant Topology Documentation

This directory contains the Ryu OpenFlow 1.3 SDN controller and execution instructions for the redundant 4-switch network topology designed for packet loss detection, dynamic path failover, and recovery[cite: 5].

---

## 1. Network Topology & Port Mapping

The network uses a diamond topology connecting two virtual hosts (`h1`, `h2`) across four OpenFlow 1.3 switches (`s1`, `s2`, `s3`, `s4`)[cite: 5].


```

```
                  +--- s2 (Primary Path) ---+
h1 (Sender) --- s1                           s4 --- h2 (Receiver)
                  +--- s3 (Alternate Path) -+

```

### Host Parameters
* **`h1` (UDP Sender)**: IP `10.0.0.1/24` | MAC `00:00:00:00:00:01`
* **`h2` (UDP Receiver)**: IP `10.0.0.2/24` | MAC `00:00:00:00:00:02`
* **Transport Port**: UDP port `12000` (or agreed port)[cite: 5]

### Switch Port Map (Do Not Change Link Order)
The SDN controller relies strictly on these OpenFlow port numbers:

| Switch | Port Number | Connected Device / Role |
| :---: | :---: | :--- |
| **`s1`** | `1` | `h1` (Host 1) |
| **`s1`** | `2` | `s2` (Primary path link) |
| **`s1`** | `3` | `s3` (Alternate path link) |
| **`s2`** | `1` | `s1` |
| **`s2`** | `2` | `s4` (Primary path link) |
| **`s3`** | `1` | `s1` |
| **`s3`** | `2` | `s4` (Alternate path link) |
| **`s4`** | `1` | `s2` (Primary path link) |
| **`s4`** | `2` | `s3` (Alternate path link) |
| **`s4`** | `3` | `h2` (Host 2) |

---

## 2. Startup & Execution Sequence

All components run on the designated Ubuntu VM using separate terminal windows[cite: 5]. Follow this startup sequence[cite: 5]:

### Terminal 1: Launch Ryu SDN Controller
Start the OpenFlow 1.3 controller from the repository root[cite: 5]:
```bash
cd ~/Computer-Networking-Project-Team-14
ryu-manager --ofp-tcp-listen-port 6653 sdn/controller.py

```

Leave this terminal running. The controller listens on port `6653` and logs switch connections and path installations.

### Terminal 2: Launch Mininet Network

In a second terminal, clear any stale state and run the topology script:

```bash
sudo mn -c
cd ~/Computer-Networking-Project-Team-14
sudo python3 topology/topology.py

```

Switches `s1`–`s4` will connect to the controller, and Terminal 2 will enter the `mininet>` prompt.

---

## 3. Network Verification & Baseline Testing

Inside the `mininet>` prompt in Terminal 2, verify reachability:

```bash
mininet> pingall
mininet> net
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1

```

* `pingall` should report **0% dropped** once initial OpenFlow rules are installed.

---

## 4. Failure Simulation & Dynamic Rerouting

The primary path uses the link between `s2` and `s4`. To simulate link failure and restoration during testing:

### Trigger Primary Path Failure

```bash
mininet> link s2 s4 down

```

* **Controller Reaction (Terminal 1)**: The controller receives `EventOFPPortStatus`, detects the link-down event on the primary path, and installs alternate routes across `s1`–`s4` via switch `s3`.
* **Verify Alternate Route**:
```bash
mininet> pingall

```



### Restore Primary Path

```bash
mininet> link s2 s4 up

```

* **Controller Reaction (Terminal 1)**: The controller detects port recovery and restores the primary route via switch `s2`.
* **Verify Restored Route**:
```bash
mininet> pingall

```



---

## 5. Integration Guide for Person 1 (App) & Person 3 (Testing)

### Running Application Scripts Inside Host Shells

Person 1's UDP application scripts execute inside virtual hosts `h1` and `h2` from the Mininet CLI:

1. **Start Receiver on `h2` (Background process)**:


```bash
mininet> h2 python3 app/receiver.py &

```


2. **Start Sender on `h1`**:


```bash
mininet> h1 python3 app/sender.py

```



### Execution Flow for Person 3's Experiments

1. Start controller and Mininet as described above.


2. Run baseline tests with full connectivity (record sent vs. received packets).


3. Run the loss/recovery test: Start `h1` transmission, execute `link s2 s4 down` midway through transmission, and record packet loss and recovery timestamps.


4. Verify application-layer retransmission (Person 1) alongside network-layer dynamic path failover (Person 2).



```

```
