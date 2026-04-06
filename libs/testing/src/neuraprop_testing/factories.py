"""Test data factories using factory_boy."""

import uuid

import factory
from faker import Faker

fake = Faker()


class FirmFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.LazyFunction(lambda: fake.company())
    slug = factory.LazyFunction(lambda: fake.slug())
    status = "active"
    plan_tier = "starter"
    settings = factory.LazyFunction(dict)


class TraderFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    firm_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    external_id = factory.LazyFunction(lambda: f"TRD-{fake.random_int(10000, 99999)}")
    email = factory.LazyFunction(fake.email)
    display_name = factory.LazyFunction(fake.name)
    kyc_status = "verified"
    risk_tier = "standard"
    profile_data = factory.LazyFunction(dict)


class ConversationFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    firm_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    trader_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    channel = "discord"
    status = "active"
    current_agent = None


class MessageFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    conversation_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    firm_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    role = "user"
    content = factory.LazyFunction(lambda: fake.sentence())
    agent_name = None


class UnifiedMessageFactory(factory.DictFactory):
    """Factory for the UnifiedMessage schema used in the message bus."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    firm_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    channel = "discord"
    direction = "inbound"
    sender_type = "trader"
    sender_channel_id = factory.LazyFunction(lambda: str(fake.random_int(100000, 999999)))
    trader_id = None
    content = factory.LazyFunction(lambda: fake.sentence())
    attachments = factory.LazyFunction(list)
    metadata = factory.LazyFunction(dict)
    conversation_id = None
    reply_to_message_id = None
