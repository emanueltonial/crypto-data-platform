from httpx import AsyncClient, Response


class TradeApiClient:
    """Centralises every call to the trades endpoint so tests don't repeat URLs."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list_trades(self, symbol: str, limit: int | None = None) -> Response:
        params: dict[str, str | int] = {"symbol": symbol}
        if limit is not None:
            params["limit"] = limit
        return await self._client.get("/trades/", params=params)

    async def list_trades_raw(self, **params) -> Response:
        """Send arbitrary params"""
        return await self._client.get("/trades/", params=params)


class HealthApiClient:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def check(self) -> Response:
        return await self._client.get("/health/")