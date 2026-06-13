"""Notification provider interface."""

from abc import ABC, abstractmethod

from app.models.internship import InternshipInDB


class NotificationProvider(ABC):
    @abstractmethod
    async def send(self, internship: InternshipInDB) -> None:
        """Send a notification for an internship."""
