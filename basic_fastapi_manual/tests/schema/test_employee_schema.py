import unittest

from pydantic import ValidationError

from app.schema.employee import Employee


class TestEmployeeSchema(unittest.TestCase):

    def test_valid_user(self):
        emp = Employee(employee_id=1, first_name="John Doe", email="john@example.com")
        self.assertEqual(emp.employee_id, 1)
        self.assertEqual(emp.first_name, "John Doe")
        self.assertEqual(emp.email, "john@example.com")

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            Employee(employee_id=1, first_name="John", email="invalid-email")

    def test_non_existent_attr(self):
        with self.assertRaises(ValidationError):
            Employee(employee_id=1, first_name="John Doe", email="john@example.com", age=15)


if __name__ == "__main__":
    unittest.main()
