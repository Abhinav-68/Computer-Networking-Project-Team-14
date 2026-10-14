
import argparse
import csv
import os
import socket
import time

from protocol import decode_message, encode_message


def write_row(writer, file_handle, event, run_id="", seq="", detail=""):
    writer.writerow([
        f"{time.time():.6f}",
        event,
        run_id,
        seq,
        detail
    ])
    file_handle.flush()


def main():
    parser = argparse.ArgumentParser(
        description="UDP packet receiver with ACKs"
    )
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Stop after this many unique DATA packets"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=120,
        help="Maximum run duration in seconds"
    )
    parser.add_argument("--log", default="results/receiver.csv")

    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.log) or ".", exist_ok=True)

    seen = set()
    start = time.time()

    with open(args.log, "w", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([
            "timestamp", "event", "run_id", "seq", "detail"
        ])
        log_file.flush()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((args.bind, args.port))
        sock.settimeout(0.5)

        print(
            f"Receiver listening on {args.bind}:{args.port}",
            flush=True
        )

        try:
            while (
                time.time() - start < args.duration
                and len(seen) < args.count
            ):
                try:
                    raw, peer = sock.recvfrom(65535)
                except socket.timeout:
                    continue

                message = decode_message(raw)

                if message is None:
                    write_row(
                        writer, log_file, "MALFORMED",
                        detail=str(peer)
                    )
                    continue

                if message["type"] != "DATA":
                    continue

                run_id = message["run_id"]
                seq = message["seq"]
                key = (run_id, seq)

                if key in seen:
                    event = "DUPLICATE"
                else:
                    seen.add(key)
                    event = "RECEIVED"

                write_row(
                    writer, log_file, event, run_id, seq, str(peer)
                )

                ack = {
                    "type": "ACK",
                    "run_id": run_id,
                    "seq": seq
                }
                sock.sendto(encode_message(ack), peer)

            print(
                f"Receiver finished: {len(seen)} unique packets",
                flush=True
            )

        finally:
            sock.close()


if __name__ == "__main__":
    main()

