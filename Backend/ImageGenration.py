import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Function to open images
def open_image(prompt):
    """Open generated images using PIL."""
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Add a delay between opening images
        except IOError:
            print(f"Unable to open {image_path}")

# API URL and headers
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Asynchronous query function
async def query(payload):
    """Send a POST request to the Hugging Face API asynchronously."""
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    return response.content

# Asynchronous function to generate images
async def generate_images(prompt: str):
    """Generate multiple images based on the given prompt."""
    tasks = []
    for _ in range(4):  # Generate 4 images
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution",
            "options": {"seed": randint(0, 1000000)}
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_byte_list = await asyncio.gather(*tasks)
    for i, image_byte in enumerate(image_byte_list):
        # Check if the response contains valid image data
        if image_byte.startswith(b'\xff\xd8'):  # JPEG file signature
            with open(fr"Data\{prompt.replace(' ', '_')}{i+1}.jpg", "wb") as f:
                f.write(image_byte)
            print(f"Generated image saved: Image/{prompt.replace(' ', '_')}{i+1}.jpg")
        else:
            print(f"Invalid image data received for image {i+1}")

# Synchronous wrapper for generating images
def GenerateImage(prompt: str):
    """Wrapper function to generate images and open them."""
    try:
        if not isinstance(prompt, str):
            raise ValueError(f"Invalid prompt type: {type(prompt)}. Expected a string.")
        
        print(f"Generating images for prompt: {prompt}")
        asyncio.run(generate_images(prompt))
        open_image(prompt)
    except Exception as e:
        print(f"Error during image generation: {e}")

# Ensure this only runs if executed directly
if __name__ == "__main__":
    while True:
        try:
            # Read the ImageGeneration.data file
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                Data: str = f.read().strip()
            Prompt, Status = Data.split(",")
            
            # If the status is "True", generate images
            if Status.strip() == "True":
                print("Generating Images...")
                GenerateImage(prompt=Prompt.strip())  # Strip whitespace from the prompt
                
                # Reset the status in ImageGeneration.data
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                break  # Exit the loop after processing
            else:
                sleep(1)  # Wait before checking again
        except FileNotFoundError:
            print("ImageGeneration.data file not found.")
        except Exception as e:
            print(f"Error during image generation process: {e}")