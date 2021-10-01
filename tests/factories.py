from datetime import timezone

import factory


class QuoteFactory(factory.DictFactory):
    policy_type = "event_ticket_protection"
    policy_type_version = 1
    policy_start_date = factory.Faker(
        "future_datetime", end_date="+1d", tzinfo=timezone.utc
    )
    event_datetime = factory.Faker(
        "future_datetime", end_date="+30d", tzinfo=timezone.utc
    )
    event_name = "Ariana Grande"
    event_location = "The O2"
    number_of_tickets = 2
    tickets = factory.List([factory.Dict({"price": 100})])
    resale_ticket = False
    event_country = "GB"


class QuotePackageFactory(factory.DictFactory):
    request = factory.List([QuoteFactory()])
    currency = "GBP"
    customer_country = "GB"
    customer_region = "London"
    customer_language = "en"
