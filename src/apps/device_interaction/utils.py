from django.conf import settings
from netmiko import ConnectHandler
from rest_framework import status
from rest_framework.response import Response


class CommonUtils:
    @staticmethod
    def generate_loopback_commands(loopback_number, ip_address, subnet_mask):
        """
        Generate commands to configure a loopback interface.

        Args:
            loopback_number (int): The number of the loopback interface.
            ip_address (str): The IP address to assign to the loopback interface.
            subnet_mask (str): The subnet mask for the loopback interface.

        Returns:
            list: A list of commands to configure the loopback interface.
        """
        return [
            f"interface Loopback{loopback_number}",
            f"description Loopback interface {loopback_number}",
            f"ipv4 address {ip_address} {subnet_mask}",
            "commit",
        ]

    @staticmethod
    def generate_deletion_commands(loopback_number):
        """
        Generate commands to delete a loopback interface.

        Args:
            loopback_number (int): The number of the loopback interface to delete.

        Returns:
            list: A list of commands to delete the loopback interface.
        """
        return [
            f"configure terminal",
            f"no interface Loopback{loopback_number}",
            f"commit",
            f"end",
        ]

    @staticmethod
    def execute_commands(device, commands):
        """
        Execute configuration commands on a network device using Netmiko.

        Args:
            device (dict): A dictionary containing device connection parameters.
            commands (list): A list of commands to execute on the device.

        Returns:
            str or Response: Output of the executed commands or an error response.
        """
        if settings.DRY_RUN:
            response_data = {
                "commands": commands,
            }
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        else:
            try:
                with ConnectHandler(**device) as net_connect:
                    net_connect.enable()
                    output = net_connect.send_config_set(commands)
                    response_data = {"message": "Configuration applied successfully"}
                    return Response(response_data, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                error_message = f"Configuration failed: {str(e)}"
                return Response(
                    {"error": error_message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class ConnectionUtils:
    @staticmethod
    def get_netmiko_connection_params():
        """
        Get connection parameters for Netmiko.

        Returns:
            dict: A dictionary containing the connection parameters for Netmiko.
        """
        return {
            "device_type": "cisco_xr",
            "ip": settings.NETCONF_HOST,
            "username": settings.NETCONF_USERNAME,
            "password": settings.NETCONF_PASSWORD,
            "timeout": settings.NETCONF_TIMEOUT,
        }

    @staticmethod
    def get_ncclient_connection_params():
        """
        Get connection parameters for NCclient.

        Returns:
            dict: A dictionary containing the connection parameters for NCclient.
        """
        return {
            "host": settings.NETCONF_HOST,
            "port": 830,
            "username": settings.NETCONF_USERNAME,
            "password": settings.NETCONF_PASSWORD,
            "device_params": {"name": "iosxr"},
        }
