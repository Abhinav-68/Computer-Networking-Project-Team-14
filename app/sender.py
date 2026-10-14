
import argparse
import csv
import os
import socket
import time
import uuid

from protocol import decode_message, encode_message


def log_event(writer, file_handle, event, run_id, seq, attempt, detail=""):
    writer.writerow([
        f"{time.time():.6f}",
        event,
        run_id,
        seq,
        attempt,
        detail
    ])
    file_handle.flush()


def main():
    parser = argparse.ArgumentParser(
        description="UDP sender with stop-and-wait retransmission"
    )
    parser.add_argument("--host", required=True, help="Receiver IPv4 address")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--log", default="results/sender.csv")

    args = parser.parse_args()

    if args.count < 0 or args.timeout <= 0 or args.interval < 0:
        parser.error("count and interval must be non-negative; timeout must be positive")

    if args.max_retries < 0:
        parser.error("max-retries must be non-negative")

    os.makedirs(os.path.dirname(args.log) or ".", exist_ok=True)

    run_id = uuid.uuid4().hex[:12]
    acknowledged = 0
    retransmissions = 0

    with open(args.log, "w", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([
            "timestamp", "event", "run_id", "seq", "attempt", "detail"
        ])
        log_file.flush()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(args.timeout)
        destination = (args.host, args.port)

        try:
            for seq in range(args.count):
                message = {
                    "type": "DATA",
                    "run_id": run_id,
                    "seq": seq,
                    "payload": f"sample-payload-{seq}"
                }
                packet = encode_message(message)
                success = False

                for attempt in range(args.max_retries + 1):
                    event = "SEND" if attempt == 0 else "RETRANSMIT"

                    if attempt > 0:
                        retransmissions += 1

                    sock.sendto(packet, destination)
                    log_event(
                        writer, log_file, event,
                        run_id, seq, attempt, destination[0]
                    )

                    deadline = time.monotonic() + args.timeout

                    while time.monotonic() < deadline:
                        remaining = deadline - time.monotonic()
                        sock.settimeout(max(remaining, 0.001))

                        try:
                            raw, _peer = sock.recvfrom(65535)
                        except socket.timeout:
                            break

                        reply = decode_message(raw)

                        if (
                            reply
                            and reply["type"] == "ACK"
                            and reply["run_id"] == run_id
                            and reply["seq"] == seq
                        ):
                            log_event(
                                writer, log_file, "ACK",
                                run_id, seq, attempt
                            )
                            acknowledged += 1
                            success = True
                            break

                    if success:
                        break

                    log_event(
                        writer, log_file, "TIMEOUT",
                        run_id, seq, attempt
                    )

                if not success:
                    log_event(
                        writer, log_file, "FAILED",
                        run_id, seq, args.max_retries,
                        "ACK not received"
                    )

                time.sleep(args.interval)

        finally:
            sock.close()

    print(f"Run ID: {run_id}")
    print(f"Packets requested: {args.count}")
    print(f"ACKed: {acknowledged}")
    print(f"Unacknowledged: {args.count - acknowledged}")
    print(f"Retransmissions: {retransmissions}")


if __name__ == "__main__":
    main()
