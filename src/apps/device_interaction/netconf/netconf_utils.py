# network_device_management/device_interaction/netconf/netconf_utils.py
from ncclient import manager, NCClientError
from django.conf import settings


class NetconfConnector:
    """
    A utility class for establishing a NETCONF connection to a network device.

    Attributes:
        host (str): The hostname or IP address of the network device.
        port (int): The port number for NETCONF communication.
        username (str): The username for authentication.
        password (str): The password for authentication.
        device_params (dict): Additional parameters for device connection.
    """

    def __init__(self):
        """
        Initialize the NetconfConnector with connection parameters from Django settings.
        """
        self.host = settings.NETCONF_HOST
        self.port = settings.NETCONF_PORT
        self.username = settings.NETCONF_USERNAME
        self.password = settings.NETCONF_PASSWORD
        self.device_params = {"name": "csr"}

    def connect(self):
        """
        Connect to the network device using NETCONF.

        Returns:
            manager.Session: A NETCONF session to the network device.

        Raises:
            Exception: If a connection error occurs.
        """
        try:
            return manager.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                device_params=self.device_params,
            )
        except NCClientError as e:
            raise Exception(f"NETCONF Connection Error: {str(e)}")


class NetconfUtils:
    """
    A utility class for executing NETCONF configurations on a network device.

    Methods:
        execute(ncconf): Execute a NETCONF configuration.

    """

    @staticmethod
    def execute(ncconf):
        """
        Execute a NETCONF configuration on the network device.

        Args:
            ncconf (str): The NETCONF configuration to be executed.

        Raises:
            Exception: If a NETCONF error occurs during execution.
        """
        connector = NetconfConnector()
        with connector.connect() as device:
            try:
                device.edit_config(target="running", config=ncconf)
            except NCClientError as e:
                raise Exception(f"NETCONF Execution Error: {str(e)}")
