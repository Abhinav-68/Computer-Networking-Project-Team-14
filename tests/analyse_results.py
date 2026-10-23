
import csv
import os
import sys

INPUT_FILE = "results/metrics.csv"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Results file not found: {INPUT_FILE}")
        print("Run the tests and save their measured results first.")
        sys.exit(1)

    with open(INPUT_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        required = {
            "test_name", "sent", "received", "lost",
            "loss_percent", "duration_s", "recovery_time_ms"
        }

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            print("CSV is missing required columns.")
            print("Required:", ", ".join(sorted(required)))
            print("Found:", reader.fieldnames)
            sys.exit(1)

        rows = list(reader)

    if not rows:
        print("The CSV contains no test results yet.")
        sys.exit(1)

    print("\nPACKET LOSS AND RECOVERY ANALYSIS")
    print("-" * 72)
    print(
        f"{'Test':<20}{'Sent':>8}{'Received':>10}"
        f"{'Lost':>8}{'Loss %':>10}{'Recovery ms':>14}"
    )
    print("-" * 72)

    for row in rows:
        sent = int(row["sent"])
        received = int(row["received"])
        lost = int(row["lost"])
        duration = float(row["duration_s"])
        recovery = row["recovery_time_ms"].strip()

        # Check that the reported packet counts are consistent.
        if sent < 0 or received < 0 or lost < 0:
            print(f"Invalid negative packet count in {row['test_name']}")
            sys.exit(1)

        if received + lost != sent:
            print(f"Packet counts do not match in {row['test_name']}")
            print("Expected received + lost = sent.")
            sys.exit(1)

        if duration < 0:
            print(f"Invalid duration in {row['test_name']}")
            sys.exit(1)

        loss_percent = (lost / sent * 100) if sent else 0.0
        recovery_text = recovery if recovery else "N/A"

        print(
            f"{row['test_name']:<20}{sent:>8}{received:>10}"
            f"{lost:>8}{loss_percent:>9.2f}%{recovery_text:>14}"
        )

    print("-" * 72)
    print("Analysis complete.")

if __name__ == "__main__":
    main()
