import xmltodict
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from ncclient import manager
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoopbackConfigSerializer, DryRunConfigSerializer
from .utils import CommonUtils, ConnectionUtils


class ConfigureLoopbackView(APIView):
    """
    API view for configuring loopback interfaces on network devices.
    """

    @swagger_auto_schema(tags=["loopback"], request_body=LoopbackConfigSerializer)
    def post(self, request, format=None):
        """
        Configure a loopback interface on a network device.

        Args:
            request (Request): The HTTP request object.
            format (str): The format of the response (default is None).

        Returns:
            Response: The response containing the output of the configuration or error messages.
        """
        serializer = LoopbackConfigSerializer(data=request.data)
        if serializer.is_valid():
            loopback_number = serializer.validated_data["loopback_number"]
            ip_address = serializer.validated_data["ip_address"]
            subnet_mask = serializer.validated_data["subnet_mask"]

            # Device connection parameters
            device = ConnectionUtils.get_netmiko_connection_params()

            # CLI commands to configure loopback interface
            commands = CommonUtils.generate_loopback_commands(
                loopback_number, ip_address, subnet_mask
            )

            # Execute commands
            output = CommonUtils.execute_commands(device, commands)
            return output
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteLoopbackView(APIView):
    """
    API view for deleting loopback interfaces on network devices.
    """

    @swagger_auto_schema(tags=["loopback"])
    def delete(self, request, loopback_number, format=None):
        """
        Delete a loopback interface on a network device.

        Args:
            request (Request): The HTTP request object.
            loopback_number (int): The number of the loopback interface to delete.
            format (str): The format of the response (default is None).

        Returns:
            Response: The response containing the output of the deletion or error messages.
        """
        if not loopback_number:
            return Response(
                {"error": "loopback_number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Device connection parameters
        device = ConnectionUtils.get_netmiko_connection_params()

        # CLI commands to delete loopback interface
        commands = CommonUtils.generate_deletion_commands(loopback_number)

        # Execute commands
        output = CommonUtils.execute_commands(device, commands)
        return output


class ListInterfaceView(APIView):
    """
    API view for retrieving interface configurations using NETCONF.
    """

    @swagger_auto_schema(tags=["loopback"])
    def get(self, request, format=None):
        """
        Retrieve interface configurations using NETCONF.

        Args:
            request (Request): The HTTP request object.
            format (str): The format of the response (default is None).

        Returns:
            Response: The response containing the retrieved interface configurations or error messages.
        """
        # Device connection parameters
        device = ConnectionUtils.get_ncclient_connection_params()

        # NETCONF filter to retrieve interface configurations
        netconf_filter = """
        <filter>
            <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"/>
        </filter>
        """

        if settings.DRY_RUN:
            response_data = {
                "filter": netconf_filter,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            try:
                with manager.connect(**device) as m:
                    result = m.get(netconf_filter)
                    data = xmltodict.parse(result.data_xml)
                    return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                error_message = f"Failed to retrieve interface configurations: {str(e)}"
                return Response(
                    {"error": error_message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class DryRunConfigView(APIView):
    """
    API view to configure the 'dry run' mode using a boolean field.
    """

    @swagger_auto_schema(tags=["default"], request_body=DryRunConfigSerializer)
    def post(self, request, format=None):
        """
        Configure the 'dry run' mode.

        Args:
            request (Request): The HTTP request object.
            format (str): The format of the response (default is None).

        Returns:
            Response: The response indicating the success or failure of configuring the 'dry run' mode.
        """
        serializer = DryRunConfigSerializer(data=request.data)
        if serializer.is_valid():
            new_dry_run_mode = serializer.validated_data["dry_run_mode"]
            settings.DRY_RUN = new_dry_run_mode
            status_msg = "Dry run mode updated successfully."
            return Response({"status": status_msg}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
