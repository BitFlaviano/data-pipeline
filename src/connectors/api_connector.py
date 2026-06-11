import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from src.utils.logger import PipelineLogger


class APIConnector:
    def __init__(
        self,
        base_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.base_url = base_url
        self.method = method.upper()
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.logger = PipelineLogger.get_logger_for_module("pipeline.extract")

    def _request(self, url: str, params: Dict = None) -> requests.Response:
        for attempt in range(self.max_retries):
            try:
                if self.method == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif self.method == "POST":
                    response = self.session.post(url, json=params, timeout=self.timeout)
                else:
                    raise ValueError(f"Método HTTP não suportado: {self.method}")

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                self.logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def extract(
        self,
        endpoint: str = "",
        params: Dict = None,
        pagination: bool = False,
        page_size: int = 100,
        max_pages: int = 10,
    ) -> pd.DataFrame:
        url = f"{self.base_url}{endpoint}"
        all_data: List[Dict] = []

        if pagination:
            for page in range(1, max_pages + 1):
                page_params = {**(params or {}), "page": page, "per_page": page_size}
                self.logger.info(f"Buscando página {page}/{max_pages}")
                response = self._request(url, params=page_params)
                data = response.json()

                items = data if isinstance(data, list) else data.get("results", data.get("data", data.get("items", [data])))
                if not items:
                    break
                all_data.extend(items)
                self.logger.info(f"Página {page}: {len(items)} registros")
        else:
            response = self._request(url, params=params)
            data = response.json()
            all_data = data if isinstance(data, list) else data.get("results", data.get("data", data.get("items", [data])))

        self.logger.info(f"Extração da API concluída: {len(all_data)} registros")
        return pd.DataFrame(all_data)

    def close(self):
        self.session.close()
