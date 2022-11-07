from typing import cast

import async_timeout
import aiohttp
from homeassistant.helpers.aiohttp_client import HassClientResponse, DATA_CLIENTSESSION


class RohlikApi:
    _session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession, username, password):
        self._user = username
        self._pass = password
        self._session = session

    async def login(self):
        async with async_timeout.timeout(10):
            response = await self._session.post("https://www.rohlik.cz/services/frontend-service/login",
                                                json={"email": self._user,"password": self._pass, "name": ""})
            if response.status != 200:
                raise ValueError("Login failed")

    def upcomming_orders(self) -> HassClientResponse:
        return cast(HassClientResponse, self._session.get("https://www.rohlik.cz/api/v3/orders/upcoming"))