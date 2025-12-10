import time
import yaml
import threading
import logging
from pathlib import Path

from node.core.entropy_reader import EntropyReader
from node.core.hasher import Hasher
from node.core.random_buffer import RandomBuffer
from node.core.health_tester import HealthTester
from node.core.control_loop import ControlLoop
from node.core.uplink_client import UplinkClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class NodeDaemon:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.entropy_reader = EntropyReader(
            chunk_size=self.config["entropy"]["chunk_size"]
        )
        self.hasher = Hasher(
            hash_alg=self.config["conditioner"]["algorithm"]
        )
        self.buffer = RandomBuffer(
            capacity=self.config["buffer"]["capacity_bytes"]
        )
        self.health = HealthTester()
        self.control = ControlLoop()
        self.uplink = UplinkClient(
            server_url=self.config["server_url"],
            api_key=self.config["api_key"],
            node_id=self.config["node_id"]
        )

        self.sequence = 0
        self.running = True
        self.upload_chunk_size = self.config["upload"]["chunk_bytes"]
        self.heartbeat_interval = self.config["heartbeat"]["interval_seconds"]

    def generation_loop(self):
        logger.info("Generation loop started")
        while self.running:
            if not self.control.is_allowed_to_generate():
                time.sleep(1)
                continue

            try:
                raw = self.entropy_reader.read_chunk()
                conditioned = self.hasher.condition(raw)
                self.buffer.append(conditioned)
                self.health.update(conditioned)
                self.sequence += 1

                if self.sequence % 10 == 0:
                    logger.debug(f"Generated {self.sequence} chunks")
            except Exception as e:
                logger.error(f"Generation error: {e}")
                self.control.state = "ERROR"
                time.sleep(5)

    def upload_loop(self):
        logger.info("Upload loop started")
        while self.running:
            try:
                chunk = self.buffer.take_chunk(self.upload_chunk_size)
                if chunk is None:
                    time.sleep(0.5)
                    continue

                self.uplink.send_chunk(
                    chunk,
                    self.health.current_status(),
                    self.sequence
                )
                logger.debug(f"Uploaded {len(chunk)} bytes")
            except Exception as e:
                logger.error(f"Upload error: {e}")
                time.sleep(2)

    def heartbeat_loop(self):
        logger.info("Heartbeat loop started")
        while self.running:
            try:
                control_response = self.uplink.send_heartbeat(
                    self.buffer.stats(),
                    self.health.current_status(),
                    self.control.state
                )
                if control_response:
                    self.control.update_from_server(control_response)
                    logger.debug(f"Control updated: {control_response}")

                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                time.sleep(self.heartbeat_interval)

    def start(self):
        logger.info(f"Starting node daemon {self.config['node_id']}")

        threads = [
            threading.Thread(target=self.generation_loop, daemon=True),
            threading.Thread(target=self.upload_loop, daemon=True),
            threading.Thread(target=self.heartbeat_loop, daemon=True)
        ]

        for t in threads:
            t.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
            for t in threads:
                t.join(timeout=2)


def main():
    config_path = Path(__file__).parent.parent / "config.yaml"
    daemon = NodeDaemon(str(config_path))
    daemon.start()


if __name__ == "__main__":
    main()
