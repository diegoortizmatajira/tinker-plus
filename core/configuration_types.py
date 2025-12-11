""" Types for configuration properties used across the application. """
AcceptedPropertyTypes = str | int | bool | list[str] | dict[str, str]
NullableAcceptedPropertyTypes = AcceptedPropertyTypes | None
ConfigurationDictionary = dict[str, NullableAcceptedPropertyTypes]
