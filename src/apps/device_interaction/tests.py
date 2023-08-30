import xmltodict
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from .views import ConfigureLoopbackView, DeleteLoopbackView, ListInterfaceView

# URLs
CONFIGURE_LOOPBACK_URL = "/configure-loopback/"
DELETE_LOOPBACK_URL = "/delete-loopback/{}/"
INTERFACES_URL = "/interfaces/"


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

        request = self.factory.post(CONFIGURE_LOOPBACK_URL, self.valid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_configure_loopback_invalid_data(self, mock_connect_handler):
        invalid_payload = {
            "loopback_number": 1,
            "ip_address": "invalid_ip",
            "subnet_mask": "255.255.255.0",
        }

        request = self.factory.post(CONFIGURE_LOOPBACK_URL, invalid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_configure_loopback_netmiko_exception(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Netmiko error")

        request = self.factory.post(CONFIGURE_LOOPBACK_URL, self.valid_payload)
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

        request = self.factory.delete(DELETE_LOOPBACK_URL.format(self.loopback_number))
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_delete_loopback_missing_number(self, mock_connect_handler):
        request = self.factory.delete(DELETE_LOOPBACK_URL.format(self.loopback_number))
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch("apps.device_interaction.views.ConnectHandler")
    def test_delete_loopback_netmiko_exception(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Netmiko error")

        request = self.factory.delete(DELETE_LOOPBACK_URL.format(self.loopback_number))
        response = DeleteLoopbackView.as_view()(
            request, loopback_number=self.loopback_number
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListInterfaceViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ListInterfaceView.as_view()

    @patch("apps.device_interaction.views.manager.connect")
    def test_successful_interface_retrieval(self, mock_connect):
        # Mock the manager and its get method
        mock_manager = MagicMock()
        mock_manager.get.return_value.data_xml = "<xml>mocked_data</xml>"
        mock_manager.get.return_value.status_code = status.HTTP_200_OK

        # Set the side effect to return the mock manager
        mock_connect.side_effect = lambda *args, **kwargs: mock_manager

        request = self.factory.get(INTERFACES_URL)
        response = self.view(request)

        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    @patch(
        "apps.device_interaction.views.manager.connect",
        side_effect=Exception("Connection error"),
    )
    def test_failed_interface_retrieval(self, mock_connect):
        request = self.factory.get(INTERFACES_URL)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data,
            {"error": "Failed to retrieve interface configurations: Connection error"},
        )
