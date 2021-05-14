Date: 2021-04-14

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We need to create a backend HTTP API that:

* Is well tested.
* Is flexible to add new types of items.
* Persists the data.
* Minimize the item stored data, rely on external providers.

Some non mandatory nice to have features are:

* Is compatible with existent scrobbler solutions.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
We're going to build the API backend with
[FastAPI](https://fastapi.tiangolo.com/) because it takes care of most of the
needs we have, and it works nicely with our data model based on pydantic.

## Data persistence

We'll use [repository-orm](https://lyz-code.github.io/repository-orm/) as an
interface to persist the data, because it decouples our model layer from the
data layer. It hides the boring details of data access by pretending that all of
our data is in memory.

We'll start with the TinyDB backend until the schema is stable enough and we
need more performance.

## Testing

Follow the [FastAPI testing
guidelines](https://fastapi.tiangolo.com/tutorial/testing/).

## Flexible to add new types

Media type interface definition.

## Authentication

We'll use [FastAPI authentication
system](https://fastapi.tiangolo.com/tutorial/security/first-steps/).

## Integrations

## Configuration

We'll use a yaml file to configure:

* The `repository-orm` database url.

## Deployment

Follow [FastAPI guidelines](https://fastapi.tiangolo.com/deployment/docker/).

## Asynchrony

It makes total sense to make it asynchronous, but I don't yet dived into the
`async` world. Thus, for the first version we'll make it synchronous.

The upside is that FastAPI supports [`async` quite
easily](https://fastapi.tiangolo.com/async/#concurrency-and-async-await), so
a change in the future won't be dramatic (in theory).

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
