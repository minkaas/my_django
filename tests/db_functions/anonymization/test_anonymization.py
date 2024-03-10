from io import StringIO

from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from tests.db_functions.models import Author, SecretAuthor


class AnonymizeDatabaseTestNoDB(SimpleTestCase):

    def test_no_database(self):
        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("Error! No database was found!", result)


class AnonymizeDatabaseTest(TestCase):

    def test_no_models(self):
        pass

    def test_no_data(self):
        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("0 items have been anonymized", result)

    def test_no_sensitive_columns(self):
        Author.objects.create(name="Patrick", age=22)

        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("0 items have been anonymized", result)

    def test_model_undefined(self):
        out = StringIO()
        call_command("anonymizedb", model="new_undefined_model")
        result = out.getvalue()
        self.assertEqual("The model new_undefined_model could not be found", result)

    def test_anonymize_string(self):
        SecretAuthor.objects.create(name="Sander", age=22)
        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("1 item has been anonymized", result)

        self.assertEqual(0, Author.objects.filter(name="Sander").count())

    def test_anonymize_email(self):
        SecretAuthor.objects.create(name="Christiana", age=43, email="supersecret@gmail.com")

        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("1 item has been anonymized", result)

        # The age should not have been modified.
        chris = SecretAuthor.objects.get(age=43)

        # Should still be a valid email.
        self.assertTrue("@" in chris.email)

    def test_anonymize_integer(self):
        pass

    def test_anonymize_password(self):
        pass

    def test_anonymize_file(self):
        pass

    def test_anonymize_url(self):
        pass
