from huggingface_hub import InferenceClient

class AIService:
    def __init__(self, hf_token):
        self.client = InferenceClient(api_key=hf_token)

    def generate_interior_design(self, prompt):
        image = self.client.text_to_image(
            prompt=f"Professional interior design, high-end furniture, {prompt}",
            model="black-forest-labs/FLUX.2-dev"
        )
        return image

    def redesign_from_image(self, base_image_path, prompt):
        with open(base_image_path, "rb") as f:
            image_data = f.read()
        image = self.client.image_to_image(
            image=image_data,
            prompt=f"Modernize this room with {prompt}, photorealistic, 8k resolution",
            model="black-forest-labs/FLUX.2-dev"
        )
        return image
