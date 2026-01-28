from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cashmoov_api.chatbot"

    def ready(self):
        """
        Elle nous permet de retrouver les signales presentes dans notre application.
        """
        import cashmoov_api.chatbot.signals
