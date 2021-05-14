Date: 2021-04-14

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?  -->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
I want to be able to track my reproduction history of multimedia items (songs,
tv shows, movies, RSS articles, pictures, and books) to be able to create smart
playlists, reports and improve my quantified self logging.

This server is to give a clean interface to register when an item has been
reproduced, when a user gives a rating to an item, and to extract data of the
history of an item. With the idea that other programs can use this server as
a backend to get the items data and do the complex logic required for smart
playlists and reports.

I've done the investigation for audio scrobbling and I've found no open source
solution that solves my use case. Even less one that allows other type of media.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

To solve the issue we need to decide:

* [Initial solution architecture](#solution-architecture).
* [Integration with other services](#integrations).
* [Design pattern](#design-pattern).

## Solution architecture

We can have a standalone program, or a client-server architecture. The first one
has a lower entry barrier for new users, but it's difficult to use when many
services at different hosts need to interact with each other.

For a first approach, we're going to create a backend HTTP API with no frontend.

To interact with the system, we'll use existent command line tools like `curl`
or `httpie`, but a proper command line tool will be created to make it easier.

To install it, we'll support both `pip` and a docker container.

## Integrations

The problem to solve is not new, so it will be based on existent, community
maintained open source software, as much as possible, to reduce the creation of
new code to maintain. Ideally we will just create abstract interfaces to other
services.

## Design pattern

To follow the practices on other projects, I'm going to use [Domain Driven
Design](https://lyz-code.github.io/blue-book/architecture/domain_driven_design/)
to structure the code, and develop with TDD to ensure the code quality.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

We're going to create a backend HTTP API that gives the functionality.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
