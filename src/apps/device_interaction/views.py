import xmltodict
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from ncclient import manager
from netmiko import ConnectHandler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoopbackConfigSerializer


class ConfigureLoopbackView(APIView):
    """
    API view for configuring loopback interfaces on network devices.
    """

    @swagger_auto_schema(tags=["loopback"], request_body=LoopbackConfigSerializer)
    def post(self, request, format=None):
        """
        Configure a loopback interface on a network device.
        """
        serializer = LoopbackConfigSerializer(data=request.data)
        if serializer.is_valid():
            loopback_number = serializer.validated_data["loopback_number"]
            ip_address = serializer.validated_data["ip_address"]
            subnet_mask = serializer.validated_data["subnet_mask"]

            # Device connection parameters
            device = {
                "device_type": "cisco_xr",
                "ip": settings.NETCONF_HOST,
                "username": settings.NETCONF_USERNAME,
                "password": settings.NETCONF_PASSWORD,
                "timeout": settings.NETCONF_TIMEOUT,
            }

            # CLI commands to configure loopback interface
            commands = [
                f"interface Loopback{loopback_number}",
                f"description Loopback interface {loopback_number}",
                f"ipv4 address {ip_address} {subnet_mask}",
                "commit",
            ]

            try:
                with ConnectHandler(**device) as net_connect:
                    net_connect.enable()
                    output = net_connect.send_config_set(commands)
                    response_data = {
                        "message": "Configuration applied successfully",
                    }
                    return Response(response_data, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                error_message = f"Configuration failed: {str(e)}"
                return Response(
                    {"error": error_message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteLoopbackView(APIView):
    """
    API view for deleting loopback interfaces on network devices.
    """

    @swagger_auto_schema(tags=["loopback"])
    def delete(self, request, loopback_number, format=None):
        """
        Delete a loopback interface from a network device.
        """
        if not loopback_number:
            return Response(
                {"error": "loopback_number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Device connection parameters for Netmiko
        device = {
            "device_type": "cisco_xr",
            "ip": settings.NETCONF_HOST,
            "username": settings.NETCONF_USERNAME,
            "password": settings.NETCONF_PASSWORD,
            "timeout": settings.NETCONF_TIMEOUT,
        }

        # CLI commands to delete loopback interface
        commands = [
            f"configure terminal",
            f"no interface Loopback{loopback_number}",
            f"commit",
            f"end",
        ]

        try:
            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(commands)
                response_data = {
                    "message": f"Loopback{loopback_number} deleted successfully",
                }
                return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            error_message = f"Configuration failed using Netmiko: {str(e)}"
            return Response(
                {"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListInterfaceView(APIView):
    """
    API view for retrieving interface configurations using NETCONF.
    """

    @swagger_auto_schema(tags=["loopback"])
    def get(self, request, format=None):
        """
        Retrieve interface configurations using NETCONF.
        """
        # Device connection parameters
        device = {
            "host": settings.NETCONF_HOST,
            "port": 830,
            "username": settings.NETCONF_USERNAME,
            "password": settings.NETCONF_PASSWORD,
            "device_params": {"name": "iosxr"},
        }

        # NETCONF filter to retrieve interface configurations
        netconf_filter = """
        <filter>
            <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"/>
        </filter>
        """

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
