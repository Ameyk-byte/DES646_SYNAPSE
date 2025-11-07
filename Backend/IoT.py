import paho.mqtt.client as mqtt
import logging
import os

def iot(query):
    """
    Control IoT devices based on the provided query.

    Parameters:
        query (str): The user input containing the device name and state.

    Returns:
        str: A response indicating success or failure.
    """
    # HiveMQ Cloud MQTT broker details
    MQTT_BROKER = "04fff2a5571b47729adc6fcd76c17bd0.s1.eu.hivemq.cloud"
    MQTT_PORT = 8883  # Secure MQTT port for HiveMQ Cloud

    # MQTT Credentials
    MQTT_USER = "hivemq.webclient.1741844782940"
    MQTT_PASSWORD = "v2,7<B&k@9jKFLX8mewD"

    # Base topic to publish commands
    BASE_TOPIC = "esp8266/devices"

    # Configure logging
    logging.basicConfig(filename="iot.log", level=logging.ERROR)

    # Read device names from iot.data
    iot_data_path = "Data/iot.data"
    if not os.path.exists(iot_data_path):
        logging.error(f"File not found: {iot_data_path}")
        return f"Error: File not found: {iot_data_path}"

    try:
        with open(iot_data_path, "r") as file:
            device_names = [line.strip() for line in file if line.strip()]
    except Exception as e:
        logging.error(f"Error reading iot.data: {e}")
        return "Error reading device names."

    # Parse the query into device name and state
    parts = query.split()
    if len(parts) < 2:
        return "Invalid query format. Please use 'device_name ON/OFF'."

    device_name = parts[0]
    state = parts[1]

    # Validate the device name
    if device_name not in device_names:
        logging.error(f"Invalid device name: {device_name}")
        return f"Sorry, no device available with the name '{device_name}'."

    # Validate the state
    if state.upper() not in ["ON", "OFF"]:
        logging.error(f"Invalid state: {state}")
        return "Invalid state. Please enter 'ON' or 'OFF'."

    # Create an MQTT client instance
    client = mqtt.Client()

    # Set username and password for authentication
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # Set TLS for secure connection
    client.tls_set()

    # Connect to the MQTT broker
    try:
        print("Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        return "Failed to connect to the MQTT broker."

    # Start the loop to process network traffic
    client.loop_start()

    # Create the command message
    command = f"{device_name} {state.upper()}"
    print(f"Publishing command: {command}")

    # Publish the command to the MQTT broker
    try:
        result, mid = client.publish(BASE_TOPIC, command, qos=1)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Command '{command}' published successfully")
        else:
            logging.error(f"Failed to publish command. Result: {result}")
            return "Failed to publish the command."
    except Exception as e:
        logging.error(f"Error publishing command: {e}")
        return "An error occurred while publishing the command."
    finally:
        client.loop_stop()
        client.disconnect()

    return f"Command '{command}' published successfully"

if __name__ == "__main__":
    iot("light off")