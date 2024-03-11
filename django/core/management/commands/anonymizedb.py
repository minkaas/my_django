from django.core.management import BaseCommand


class Command(BaseCommand):
    help = (
        "Anonymizes the model fields that are marked as sensitive information. "
        "With the help of Faker new dummy data is created according to the field "
        "properties that have been set."
    )

    requires_system_checks = []
    shells = ["python"]

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--model",
            help=(
                "Which model should be anonymized"
            ),
        )

    def handle(self, *args, **options):
        pass
