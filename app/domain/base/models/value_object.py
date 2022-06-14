from attrs import define

value_object = define(
    slots=False, kw_only=True, hash=True
)  # frozen=True break sqlalchemy loading
