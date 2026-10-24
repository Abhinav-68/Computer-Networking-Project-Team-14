
import csv
import os
import sys
import matplotlib.pyplot as plt

INPUT_FILE = "results/metrics.csv"
OUTPUT_DIR = "results"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Results file not found: {INPUT_FILE}")
        print("Run the tests and save measured results first.")
        sys.exit(1)

    with open(INPUT_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        required = {
            "test_name", "sent", "received", "lost",
            "loss_percent", "duration_s", "recovery_time_ms"
        }

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            print("CSV is missing required columns.")
            sys.exit(1)

        rows = list(reader)

    if not rows:
        print("The CSV contains no test results yet.")
        sys.exit(1)

    names = [row["test_name"] for row in rows]
    loss = []
    recovery_names = []
    recovery_values = []

    for row in rows:
        sent = int(row["sent"])
        received = int(row["received"])
        lost = int(row["lost"])

        if sent < 0 or received < 0 or lost < 0:
            print(f"Invalid packet count in {row['test_name']}")
            sys.exit(1)

        if received + lost != sent:
            print(f"Packet counts do not match in {row['test_name']}")
            sys.exit(1)

        loss.append((lost / sent * 100) if sent else 0.0)

        recovery = row["recovery_time_ms"].strip()
        if recovery and recovery.upper()!="N/A" :
            recovery_names.append(row["test_name"])
            recovery_values.append(float(recovery))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Graph 1: packet loss percentage for each test.
    plt.figure()
    plt.bar(names, loss)
    plt.xlabel("Test")
    plt.ylabel("Packet loss (%)")
    plt.title("Packet Loss by Test")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "packet_loss.png"))
    plt.close()

    # Graph 2: recovery time where it was measured.
    if recovery_values:
        plt.figure()
        plt.bar(recovery_names, recovery_values)
        plt.xlabel("Test")
        plt.ylabel("Recovery time (ms)")
        plt.title("Recovery Time by Test")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "recovery_time.png"))
        plt.close()
    else:
        print("No recovery-time measurements available; skipped that graph.")

    print("Graphs saved in the results folder.")

if __name__ == "__main__":
    main()

