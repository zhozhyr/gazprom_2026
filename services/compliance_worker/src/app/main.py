import asyncio
import logging

from app.worker import ComplianceWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


async def main() -> None:
    worker = ComplianceWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
