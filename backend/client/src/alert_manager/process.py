from typing import Any
import operator
from .entities import Data, Fault, Connection


class ProcessData:


    USINA_RULES = [
        ("purity",            operator.lt,  90.0,  "Low purity: {value}%"),
        ("product_pressure",  operator.lt,   5.0,  "Low product pressure: {value}"),
        ("pressure",          operator.lt,   5.0,  "Low central pressure: {value}"),
        ("dew_point",         operator.gt, -45.0,  "High dew point: {value}"),
        ("line",              operator.lt,   5.0,  "Low line pressure: {value}"),
    ]

    FLAG_RULES = [
        ("phase_fault", operator.ne, "OK", "RST failure detected"),
        ("emergency_btn",  operator.ne, "OK", "Emergency button activated"),
    ]

    HOSPITAL_RULES = [
        ("pressure", operator.lt, 5.0, "Low pressure: {value}"),
        ("line",     operator.lt, 5.0, "Low line pressure: {value}"),
        ("dew_point", operator.gt, -45.0, "High dew point: {value}"),
    ]



    @staticmethod
    def _safe_get(value: Any, default: Any) -> Any:
        """
        Safely retrieve a numeric value with a fallback default.

        Converts the input value to a float and returns it if the conversion is successful.
        If the value is None or cannot be converted to a numeric type, returns the provided default value.

        Args:
            value (Any): The value to be converted to float.
            default (Any): The default value to return if value is None or not numeric.

        Returns:
            Any: The value converted to float, or the default value if conversion fails or value is None.

        Examples:
            >>> __safe_get(42, 0)
            42.0
            >>> __safe_get("3.14", 0)
            3.14
            >>> __safe_get(None, 0)
            0
            >>> __safe_get("invalid", 0)
            0
        """
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def generate_fault_objects(
                                cls,
                                name: str,
                                hospital: str,
                                values: Data,
                                rules: list,
                                safe_get
                            ) -> list[Fault]:

        faults = []
        
        for key, op, limit, message in rules:

            value = safe_get(getattr(values, key), limit)
            if op(value, limit):
                faults.append(
                    Fault(
                        hospital=hospital,
                        source=name,
                        key=key,
                        message=message.format(value=value)
                    )
                )

        return faults


class Handles:

    @classmethod
    def _handle_usina_email(cls, fault: Fault):
        """
        Process power plant alert email data by extracting PSA and central values.
        This method retrieves power plant and central data from the input, merges them,
        and processes an alert using predefined power plant rules to generate an email
        subject and body.
        Args:
            cls: Class reference for accessing class methods and constants.
            data (dict): Input data dictionary containing:
                - "Data" (dict): Dictionary with "usina" and "central" keys.
                - "Hospital" (str): Hospital identifier for the alert.
        Returns:
            tuple: A tuple containing:
                - subject (str): Email subject line.
                - body (str): Email body content.
        Example:
            >>> data = {
            ...     "Data": {"usina": {"param1": 100}, "central": {"param2": 50}},
            ...     "Hospital": "Hospital ABC"
            ... }
            >>> subject, body = cls._handle_usina_email(data)
        """
       
        return cls.create_message(fault)

    @classmethod
    def _handle_hospital_email(cls, fault: Fault):
        """
        Process hospital email data and generate an alert based on predefined rules.
        Args:
            cls: The class instance.
            data (dict): A dictionary containing hospital email data with keys:
                - "Data" (dict): Hospital data to be processed.
                - "Hospital" (str): The hospital identifier or name.
        Returns:
            The result of process_alert() method with hospital-specific rules and data.
        Raises:
            KeyError: If required keys ("Data" or "Hospital") are missing from the input data.
        """
        
        return cls.create_message(fault)

    @classmethod
    def create_message(cls, fault: Fault):
      
        return  (
            f'ALERT: Issues detected in {fault.source} {fault.hospital}\n\n'
            f'Identified issues:\n' 
            f'{fault.message}'
        )
    
    @classmethod
    def create_recover_message(cls, fault: Fault):
      
        return  (
            f'ALERT: Issues recovered in {fault.source} {fault.hospital}\n\n'
            f'Identified solved:\n' 
            f'{fault.message}'
        )


    @classmethod
    def create_connection_message(cls, connection: Connection) -> str:
    
        return (
            f'CONNECTION ALERT: \n'
            f'Hospital: {connection.hospital} \n'
            f'Status: {connection.status}'
        )




