import requests
import logging
from shared.config import settings

logger = logging.getLogger(__name__)

class TransactionClient:
    @staticmethod
    def create_transaction(order_id: int, amount: float, auth_token: str):
        try:
            response = requests.post(
            f"{settings.TRANSACTION_SERVICE_URL}/transactions/",
                json={
                    "order_id": order_id,
                    "cost": amount,
                },
                headers={
                    "authorization": f"Bearer {auth_token}",
                    "content-type": "application/json",
                },
                timeout=10.0
            )
            if response.status_code == 201:
                logger.info(f"Transaction for order {order_id} created successfully")
                return {
                    "success": True,
                    "transaction": response.json(),
                    "status_code": response.status_code
                }
            else:
                logger.error(f"Error creating transaction {response.status_code} for order {order_id}: {response.text}")
                return {
                    "success": False,
                    "transaction": response.text,
                    "status_code": response.status_code
                }
        except requests.Timeout:
            logger.error(f"Timeout for transaction {order_id}")
            return {
                "success": False,
                "error": "Timeout connecting to transaction service",
                "status_code": 408
            }

        except requests.RequestException as e:
            logger.error(f"HTTP exception in FastAPI: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 503
            }