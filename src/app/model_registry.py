from src.app.services.generator import Generator
from src.app.services.encoder import Encoder
class ModelRegistry:
    def __init__(self):
        self.encoder = None
        self.generator = None

    def init_app(self, app):
        self.encoder = Encoder(
            app.config("ENCODER_MODEL_PATH")
        )

        self.generator = Generator(
            app.config("GENERATOR_MODEL_PATH")
        )