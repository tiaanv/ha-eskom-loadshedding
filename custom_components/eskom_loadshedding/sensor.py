"""Sensor platform for Eskom Loadshedding Interface."""
from .const import (
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR,
)
from .entity import EskomEntity, LoadSheddingActiveEntity, NextLoadSheddingEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EskomStageSensor(coordinator, entry),
            LoadSheddingActiveSensor(coordinator, entry),
            NextLoadSheddingSensor(coordinator, entry),
        ]
    )


class EskomStageSensor(EskomEntity):
    """Eskom Stage Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_stage"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("stage")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON


class LoadSheddingActiveSensor(LoadSheddingActiveEntity):
    """Load Shedding Active Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_load_shedding_active"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("load_shedding_active")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON


class NextLoadSheddingSensor(NextLoadSheddingEntity):
    """Load Shedding Active Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_next_load_shedding"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("next_load_shedding")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
