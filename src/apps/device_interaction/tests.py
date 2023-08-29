from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .views import ConfigureLoopbackView, DeleteLoopbackView


class ConfigureLoopbackTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.valid_payload = {
            "loopback_number": 1,
            "ip_address": "192.168.1.1",
            "subnet_mask": "255.255.255.0",
        }

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_configure_loopback_success(self, mock_connect_handler):
        mock_net_connect = MagicMock()
        mock_net_connect.send_config_set.return_value = (
            "Configuration applied successfully"
        )
        mock_connect_handler.return_value = mock_net_connect

        request = self.factory.post("/configure-loopback/", self.valid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_configure_loopback_invalid_data(self, mock_connect_handler):
        invalid_payload = {
            "loopback_number": 1,
            "ip_address": "invalid_ip",
            "subnet_mask": "255.255.255.0",
        }

        request = self.factory.post("/configure-loopback/", invalid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_configure_loopback_netmiko_exception(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Netmiko error")

        request = self.factory.post("/configure-loopback/", self.valid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteLoopbackTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.loopback_number = 1

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_delete_loopback_success(self, mock_connect_handler):
        mock_net_connect = MagicMock()
        mock_net_connect.send_config_set.return_value = "Loopback1 deleted successfully"
        mock_connect_handler.return_value = mock_net_connect

        request = self.factory.delete(f"/delete-loopback/{self.loopback_number}/")
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_delete_loopback_missing_number(self, mock_connect_handler):
        request = self.factory.delete("/delete-loopback/")
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_delete_loopback_netmiko_exception(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Netmiko error")

        request = self.factory.delete(f"/delete-loopback/{self.loopback_number}/")
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
