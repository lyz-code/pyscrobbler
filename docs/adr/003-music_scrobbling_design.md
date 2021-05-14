Date: 2021-04-14

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We want to take the principles defined in
[001](001-high_level_problem_analysis.md) and
[002](002-initial_backend_design.md).

That means define the scrobbler HTTP API to register music history data. In
particular we need to record:

* When a user has reproduced a track
* When a user has skipped a track.
* When a user has rated a track.

We want the next features:

* A way for the user to undo the last rating.
* The history of a track must be associated with an immutable id, so that we
    don't loose information if the file name or metadata of the track changes.
* An endpoint that given the track id, we get the history of that item.
* I'm not sure if I want to support asynchronous data. Imagine that the media
    player looses connectivity with the scrobbler, when it reconnects again, it
    may be able to upload all the created data.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## State of the art

Audio scrobbling is not new, there are some tools that integrate with the two
most famous scrobbling implementations last.fm's and librefm's. The first one is
used by the proprietary popular website, the second one is an open source
implementation of the first made by the people of GNU.

In the  [last.fm](https://www.last.fm/api/scrobbling) definition, a song is not
scrobbled if it's length is less than 30s, or if the user reproduced less than
50% or 4 minutes whichever comes first. I feel that those scrobbles are
representative, as some songs are small in the first case, and skipping a song
should reduce the overall score of the track as you showed no interest in
listening to it.

For the servers, a quick search shows:

* [maloja](#maloja)
* [Librefm](#librefm)
* [OpenWebScrobbler](#openwebscrobbler)

Maloja is the one that looks best, but still I feel it's not enough as it
doesn't support rating, it's not easily installed, and the storage is not one of
the supported by repository-orm.

For the clients, there exists:

* [mopidy_scrobbler](https://github.com/mopidy/mopidy-scrobbler/blob/master/mopidy_scrobbler/frontend.py#L81):
    Even though it only supports lastfm, we can think of [generalizing
    it](https://github.com/mopidy/mopidy-scrobbler/issues/5).
* [mpdscribble](https://github.com/MusicPlayerDaemon/mpdscribble): looks good,
    as it's integrated with mpd, but it's written in C++ and it doesn't support
    ratings either. I don't know if it would work with mopidy.
* [mpdas](https://50hz.ws/mpdas/)
    ([source](https://github.com/hrkfdn/mpdas/tree/master)).

### [maloja](https://github.com/krateng/maloja)

Fairly maintained and a decent enough [interface](https://maloja.krateng.ch/).
Although it doesn't [support rating](https://github.com/krateng/maloja/issues/72).

It's a good reference for an interface to get information of your history.

After a quick dive into the code, I still don't know how does it store the data
or how it fetch the metadata.

I've tried installing the server with pip or the docker image with no success.

You only need one POST request to `/apis/mlj_1/newscrobble` with the keys
`artist`, `title` and `key` (and optionally `album`, `duration` (in seconds) and
`time`(for cached scrobbles)) - either as form-data or json.

It supports [these scrobblers](https://github.com/krateng/maloja#native-support)
by default, and [these
others](https://github.com/krateng/maloja#standard-compliant-api) through the
compliant [apis](https://github.com/krateng/maloja#standard-compliant-api).

### [Librefm](https://git.gnu.io/foocorp/librefm/-/wikis/home)

Software behind http://libre.fm/. It doesn't support ratings, and it looks like
a deprecated project, last commit was a year ago. Although it supports a [wide
variety of clients](https://git.gnu.io/foocorp/librefm/-/wikis/Clients)

The source is [here](https://git.gnu.io/gnu/gnu-fm/-/tree/master/).

### [OpenWebScrobbler](https://github.com/elamperti/OpenWebScrobbler)

Uses last.fm in the backend and needs an API, so not for me.

## Solution

The existent tools doesn't solve our use case, so we need to create our own.

There are two types of clients for the API:

* Media players
* Users

The former will record when a track has been reproduced or skipped, the latter
will add the ratings.

### Server methods

To identify the records we'll use an unique identifier with the key `id`.

#### Scrob

Record when a track has been fully or partially reproduced. If the track has not
being reproduced till the end it means that it's been skipped.

If we only receive the `id`, so no `duration` and `item_duration`, we'll assume
that it's been completely reproduced. We will use those two attributes instead
of a `percent` because we can extract more information, for example how much
time has a user spent listening to the author X, or genre Y.

Additional information can be passed, such as `artist` and `title`, they will be
used for logging purposes only.

The scrob also has a `state` either `started` or `finished`, the idea is that
the media server tells pyscrobbler when the item has being started and when has
it ended. This will be useful for the [rating](#rate).

#### Rate

We assume that the user is going to use a client for the media player, but the
tool that will interact with pyscrobbler won't need to connect to it. So it
won't know what track is reproducing at the moment.

To solve this, as the media player tells the server which track is being
reproduced, the user will only need to send the `rating`, and it will be
assumed that the track rated is the started one. As the rating is done in the
middle of the reproduction, the `duration` attribute is set to the point in the
track where the rating was done.

#### Tag

We're going to assume the same scenario as the [rate](#rate) case, so the client
only needs to send the tag.

#### Undo

It won't accept any argument, it will delete the last user rating or tagging
from the database.

#### History

Will print the history of the scrobs, rates and tags of the items.

For better browsing it will accept the next arguments:

* `item_id`: Only show the history of one item.
* `limit`: The number of cases to return, by default `10`.
* `type`: They type of event to return, one of `scrob`, `rate`, `tag`, `all`.
    Default `all`.

### Clients

#### Media player

##### [Mopidy](https://lyz-code.github.io/blue-book/modipy/)

The first media player I've got in mind is mopidy as I'm going to use it in my
system, but the coding should be done through abstractions so that changing to
other player is easy.

They already have
[modipy-scrobbler](https://github.com/mopidy/mopidy-scrobbler), which even
though it doesn't fit our case, is a good starting point to develop our own
extension. What you can see in the [`track_playback_ended`
method](https://github.com/mopidy/mopidy-scrobbler/blob/master/mopidy_scrobbler/frontend.py#L64)
is that mopidy passes a [`tl_track`
object](https://docs.mopidy.com/en/release-1.1/api/models/#mopidy.models.TlTrack),
which models a tracklist track. A wrapper over a regular
[Track](https://docs.mopidy.com/en/release-1.1/api/models/#mopidy.models.Track)
and it’s tracklist ID.

We can see that the Track object has many interesting attributes, but the most
important one for us is the `uri` which will serve us as the immutable, unique
identifier of the track.

I plan to also use [mopidy-beets](https://github.com/mopidy/mopidy-beets) as
a library manager for mopidy, [diving into it's
code](https://github.com/mopidy/mopidy-beets/blob/d5b1b9142c19ef475ee5331a0ae9e9754291924b/mopidy_beets/translator.py#L101),
it looks like the `uri` contains the beets track id, which is awesome, as it's
going to be the unique identifier for the services I'm going to use in my music
management system.

#### Users

As they will only need to do a GET request to the `rate` endpoint with an
integer, I feel that we can start with assuming that they can use `curl` or
similar tools. In the docs we can document how to make a bash/zsh function so
it's more user friendly.

Once we add authentication we may think to create a small cli to
make things easier.

### Asynchrony support

Supporting the bulk upload of scrobs and rates in the event of a disconnection
between the media player or the user with the scrobbler server would mean that:

* User and media player clients should be able to store that information, and
    retry the upload when the connection is reestablished.
* We can't assume that the clocks of the user and the media player are
    synchronized, so the current rating method may fail badly and would need to
    be reformulated.

Those two facts will make both server and client's code more complex, to
solve a problem that we may not have. So we won't implement it in the first
versions.

# Decision
<!-- What is the change that we're proposing and/or doing? -->
We'll:

* Develop an FastAPI backend with the methods: `scrob`, `rate`, `start`,
    `undo`, and `item` that will use an unique `id` as the identifier of the
    track.
* Discern a full reproduction from a skip by comparing the `item_duration` with
    the reproduction `duration`.
* Create a mopidy extension to send the media player scrobbles.
* Create a bash/zsh function for the user to use the `rate` endpoint.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
