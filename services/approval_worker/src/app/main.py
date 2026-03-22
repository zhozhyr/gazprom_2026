import asyncio
import logging

from app.worker import ApprovalWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


async def main() -> None:
    worker = ApprovalWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
