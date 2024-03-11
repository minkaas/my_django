import datetime
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.validators import URLValidator
from django.test import TestCase, SimpleTestCase
from tests.db_functions.models import Author, SecretAuthor, SecretArticle, \
    ArticleRepository


class AnonymizeDatabaseTestNoDB(SimpleTestCase):

    def test_no_database(self):
        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("Error! No database was found!", result)


class AnonymizeDatabaseTest(TestCase):

    def test_no_models(self):
        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("0 items have been anonymized", result)

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
        sa = SecretArticle.objects.create(
            authors=[SecretAuthor.objects.get(age=43)],
            title="Secret papers - A revised collection",
            text="A long time ago, papers where send with simple cyphers like the "
                 "Caesar cypher, over time these have become more and more complex.",
            written=datetime.date.today(),
            views=0
        )

        view_changed = False

        # Checking the actual integer being different is non-deterministic. Since for
        # some seeds, the random value may actually be zero again.
        updated_sa = None
        for i in range(100):
            out = StringIO()
            call_command("anonymizedb")
            result = out.getvalue()
            self.assertEqual("1 item has been anonymized", result)
            updated_sa = SecretArticle.objects.get(pk=sa.pk)
            if updated_sa.views != 0:
                view_changed = True
                break

        self.assertTrue(view_changed, "The nr of views should have changed, but it "
                                      "didn't")
        # The anonymizer should be aware of the constraint of the positive integer field
        # and only generate positive integers.
        self.assertGreaterEqual(updated_sa.views, 0)

    def test_anonymize_file(self):
        sa = SecretArticle.objects.create(
            authors=[SecretAuthor.objects.get(age=43)],
            title="Secret papers - A revised collection",
            text="A long time ago, papers where send with simple cyphers like the "
                 "Caesar cypher, over time these have become more and more complex.",
            written=datetime.date.today(),
            views=0,
            pdf=open("random_file", "r")
        )

        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("1 item has been anonymized", result)

        self.assertNotIn("random_file", sa.pdf.path)

    def test_anonymize_null(self):
        """
        For null values the results may still be not null.
        """
        sa = SecretArticle.objects.create(
            authors=[SecretAuthor.objects.get(age=43)],
            title="Secret papers - A revised collection",
            text="A long time ago, papers where send with simple cyphers like the "
                 "Caesar cypher, over time these have become more and more complex.",
            written=datetime.date.today(),
            views=0
        )

        was_null = False
        was_not_null = False

        for i in range(100):
            out = StringIO()
            call_command("anonymizedb")
            result = out.getvalue()
            self.assertEqual("1 item has been anonymized", result)
            updated_sa = SecretArticle.objects.get(pk=sa.pk)
            if updated_sa.pdf is not None:
                was_not_null = True
            else:
                was_null = True

            if was_null and was_not_null:
                break

        self.assertTrue(was_null)
        self.assertTrue(was_not_null)

    def test_anonymize_url(self):
        ar = ArticleRepository.objects.create(
            name="article hosting",
            url="https://secret-location.org/"
        )

        out = StringIO()
        call_command("anonymizedb")
        result = out.getvalue()
        self.assertEqual("1 item has been anonymized", result)

        anon_ar = ArticleRepository.objects.all()[0]

        # The url should be different
        self.assertNotEqual("https://secret-location.org/", anon_ar.url)

        # The url should be a valid one
        validator = URLValidator(verify_exists=False)
        try:
            validator(anon_ar.url)
        except ValidationError as e:
            self.fail(f"The anonymous URL was invalid! {anon_ar.url}")
