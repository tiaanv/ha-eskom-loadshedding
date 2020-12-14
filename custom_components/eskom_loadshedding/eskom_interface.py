import ssl
from .loadshedding_schedule import isLoadSheddingNow, getNextTimeSlot


from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError
from aiohttp_retry import RetryClient


class eskom_interface:
    """Interface class to obtain loadshedding information using the Eskom API"""

    def __init__(self):
        """Initializes class parameters"""

        self.base_url = "https://loadshedding.eskom.co.za/LoadShedding"
        self.headers = {
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0"
        }
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")

    async def async_query_api(self, endpoint, payload=None):
        """Queries a given endpoint on the Eskom loadshedding API with the specified payload

        Args:
            endpoint (string): The endpoint of the Eskom API
            payload (dict, optional): The parameters to apply to the query. Defaults to None.

        Returns:
            The response object from the request
        """
        async with RetryClient() as client:
            # The Eskom API occasionally drops incoming connections, implement reies
            async with client.get(
                url=self.base_url + endpoint,
                headers=self.headers,
                params=payload,
                ssl=self.ssl_context,
                retry_attempts=50,
                retry_exceptions={
                    ClientConnectorError,
                    ServerDisconnectedError,
                    ConnectionError,
                    OSError,
                },
            ) as res:
                return await res.json()

    async def async_get_stage(self, attempts=50):
        """Fetches the current loadshedding stage from the Eskom API

        Args:
            attempts (int, optional): The number of attempts to query a sane value from the Eskom API. Defaults to 5.

        Returns:
            The loadshedding stage if the query succeeded, else `None`
        """

        # Query the API until a sensible (> 0) value is received, or the number of attempts is exceeded
        for attempt in range(attempts):
            res = await self.async_query_api("/GetStatus")

            # Return the current loadshedding stage by subtracting 1 from the query result
            # Occasionally the Eskom API will return a negative stage, so simply retry if this occurs
            if res and int(res) > 0:
                return int(res) - 1

        # If the query does not succeed after the number of attempts has been exceeded, raise an exception
        raise Exception(
            f"Error, invalid loadshedding stage received from API after {attempts} attempts"
        )

    async def async_get_data(self, coct_area):
        """Fetches data from the loadshedding API"""
        stage = await self.async_get_stage()

        if stage > 0:
            load_shedding_active = isLoadSheddingNow(stage, coct_area)["status"]
            next_load_shedding = getNextTimeSlot(stage, coct_area)["date"]
        else:
            load_shedding_active = False
            next_load_shedding = "N/A"

        data = {
            "data": {
                "stage": stage,
                "load_shedding_active": load_shedding_active,
                "next_load_shedding": next_load_shedding,
            },
        }
        return data
