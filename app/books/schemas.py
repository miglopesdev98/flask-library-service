from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    author = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    isbn = fields.Str(required=True, validate=validate.Length(min=10, max=13))
    published_date = fields.Date(allow_none=True)
    publisher = fields.Str(allow_none=True, validate=validate.Length(max=100))
    description = fields.Str(allow_none=True)
    total_copies = fields.Int(load_default=1, validate=validate.Range(min=0))
    available_copies = fields.Int(dump_only=True)
    date_added = fields.DateTime(dump_only=True)
    
    @validates('isbn')
    def validate_isbn(self, value):
        """Basic ISBN validation"""
        if not value.isdigit():
            raise ValidationError("ISBN must contain only digits")
        if len(value) not in (10, 13):
            raise ValidationError("ISBN must be 10 or 13 digits long")
    
    @validates('published_date')
    def validate_published_date(self, value):
        if value and value > datetime.now().date():
            raise ValidationError("Publication date cannot be in the future")

class CheckoutSchema(Schema):
    id = fields.Int(dump_only=True)
    book_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    checkout_date = fields.DateTime(dump_only=True)
    due_date = fields.DateTime(required=True)
    return_date = fields.DateTime(allow_none=True)
    
    @validates('due_date')
    def validate_due_date(self, value):
        if value <= datetime.now():
            raise ValidationError("Due date must be in the future")
