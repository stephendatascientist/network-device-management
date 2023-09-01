from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from .views import (
    ListInterfaceView,
    ConfigureLoopbackView,
    DryRunConfigView,
    DeleteLoopbackView,
)


class ConfigureLoopbackTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.valid_payload = {
            "loopback_number": 1,
            "ip_address": "192.168.1.1",
            "subnet_mask": "255.255.255.0",
        }

    @patch(
        "apps.device_interaction.views.ConnectionUtils.get_netmiko_connection_params"
    )
    @patch("apps.device_interaction.views.CommonUtils.generate_loopback_commands")
    @patch("apps.device_interaction.views.CommonUtils.execute_commands")
    def test_configure_loopback_success(
        self, mock_execute_commands, mock_generate_commands, mock_connection_params
    ):
        mock_connection_params.return_value = {"device": "dummy_params"}
        mock_generate_commands.return_value = ["dummy_command"]
        mock_execute_commands.return_value = Response(
            "Configuration applied successfully", status=status.HTTP_200_OK
        )

        request = self.factory.post("/configure-loopback/", self.valid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Configuration applied successfully")

    @patch("apps.device_interaction.views.LoopbackConfigSerializer")
    def test_configure_loopback_invalid_data(self, mock_serializer):
        mock_serializer.return_value.is_valid.return_value = False
        mock_serializer.return_value.errors = {"error": "Invalid data"}

        request = self.factory.post("/configure-loopback/", self.valid_payload)
        response = ConfigureLoopbackView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid data"})


class DeleteLoopbackTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch(
        "apps.device_interaction.views.ConnectionUtils.get_netmiko_connection_params"
    )
    @patch("apps.device_interaction.views.CommonUtils.generate_deletion_commands")
    @patch("apps.device_interaction.views.CommonUtils.execute_commands")
    def test_delete_loopback_success(
        self, mock_execute_commands, mock_generate_commands, mock_connection_params
    ):
        mock_connection_params.return_value = {"device": "dummy_params"}
        mock_generate_commands.return_value = ["dummy_command"]
        mock_execute_commands.return_value = Response(
            "Deletion successful", status=status.HTTP_200_OK
        )

        request = self.factory.delete("/delete-loopback/1/")
        response = DeleteLoopbackView.as_view()(request, loopback_number=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Deletion successful")

    def test_delete_loopback_missing_number(self):
        request = self.factory.delete("/delete-loopback/")
        response = DeleteLoopbackView.as_view()(request, loopback_number=None)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "loopback_number is required."})


class ListInterfaceTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch(
        "apps.device_interaction.views.ConnectionUtils.get_ncclient_connection_params"
    )
    @patch("ncclient.manager.connect")
    def test_list_interface_success(
        self, mock_ncclient_connect, mock_connection_params
    ):
        mock_connection_params.return_value = {"device": "dummy_params"}
        mock_manager = MagicMock()
        mock_manager.get.return_value.data_xml = "<data><dummy>value</dummy></data>"
        mock_ncclient_connect.return_value = mock_manager

        request = self.factory.get("/interfaces/")
        response = ListInterfaceView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("apps.device_interaction.views.settings")
    def test_list_interface_dry_run(self, mock_settings):
        mock_settings.DRY_RUN = True

        request = self.factory.get("/interfaces/")
        response = ListInterfaceView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DryRunConfigTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.valid_payload = {
            "dry_run_mode": True,
        }

    @patch("apps.device_interaction.views.settings")
    def test_configure_dry_run_success(self, mock_settings):
        mock_settings.DRY_RUN = False
        mock_serializer = MagicMock()
        mock_serializer.return_value.is_valid.return_value = True
        mock_serializer.return_value.validated_data = {"dry_run_mode": True}

        request = self.factory.put("/dry-run-config/", self.valid_payload)
        response = DryRunConfigView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"status": "Dry run mode updated successfully."}
        )

    @patch("apps.device_interaction.views.DryRunConfigSerializer")
    def test_configure_dry_run_invalid_data(self, mock_serializer):
        mock_serializer.return_value.is_valid.return_value = False
        mock_serializer.return_value.errors = {"error": "Invalid data"}

        request = self.factory.put("/dry-run-config/", self.valid_payload)
        response = DryRunConfigView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid data"})
