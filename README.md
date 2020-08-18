# `lektor-git-src-publisher`

[Lektor][lektor]'s wonderful interface enables non-technical users to modify
the source of a Lektor-based site and publish the resulting website.

However, if such source code is managed with git, the user will still have to
fiddle around with git clients or interfaces in order collaborate with others.

This simple plugin enables two publish targets, one to update the page's
source code from a remote, and one to update the remote with the local
changes.


## Using this


### Steps

0. Setup the `REMOTE` and its authentication (out of scope for this plugin)
1. Install `lektor-git-src-publisher`
2. Add the publishers to the project
3. `lektor serve` and profit!


### Details

In order to install the plugin you can add following to your `.lektorproject`
file:

    [packages]
    lektor-git-src-publisher = 0.3

Or follow the [official plugin instructions][lektorplugins].

In order to enable the publishers, you also modify your `.lektorproject` file:

    [servers.update]
    name = Update from Remote
    enabled = yes
    target = gitsrc-forcepull://main

    [servers.push]
    name = Push to Remote
    enabled = yes
    target = gitsrc-push://main

Notice that this plugin registers the `gitsrc-forcepull://BRANCH` and
`gitsrc-push://BRANCH` schemas.

It is conceivable to have multiple publishers, e.g. one for a `staging` and
one for a `main` branch. See the [limitations](#limitations).


## Trying it out

When running on a POSIX environment, you can:

    cd test_projects
    # This generates the sample projects and initialises bare git repositories
    # to facilitate testing.
    ./gen_projects.sh

Then run one of the test projects as follows:

    # Most standard setup
    lektor --project minimal serve
    # An example with the .lektorproject not running at the root of the repo
    lektor --project nested/project/minimal serve

When using the special publisher, the bare repositories created in
`test_projects/minimal.git` and `test_projects/nested.git` respectively will
be updated with your changes.


## Getting in touch / collaborating

If you just want to say hi/thanks or ask something, we are on [Matrix][matrix]!
Get in touch with us at [#oss:camilion.eu][matrixosscml] or through
our website: [https://camilion.eu][camilion].

If you have an issue with this plugin [open an Issue][gspissues].

If you have an improvement you'd like to have shipped with this plugin,
either get in touch with us, or open an Issue or a Pull Request.

We mirror the code to GitHub from our infra, so PRs from any other code
hosting platforms are very welcome as well.

A special mention goes to our friends at [ungleich][ungleich], who
also needed this and provided the feedback and motivation needed to push
this forward.


## Limitations

Due to the way this is done, the Lektor server can be confused if you change
the `.lektorproject` too much under its feet, simple things should be alright
and, when in doubt, restart the Lektor server after making big changes.


## Gory details

This plugin uses Lektor's [publisher API][lektorpublisher] in a
non-traditional fashion, instead of publishing the resulting artifacts:
- `gitsrc-forcepull`: updates the source working directory to pull remote
  changes.
- `gitsrc-push`: auto-commits and pushes to the configured remote.

The [source code][gspcode] is quite straight forward, when in doubt do read it!

### `gitsrc-forcepull`

This is roughly equivalent to following pseudo-code:

    # Save local changes
    git stash
    # Update remotes
    git fetch --progress
    if (BRANCH != CURRENT_BRANCH) {
        # Ensure we are working on the specified branch
        git checkout -b BRANCH -t REMOTE/BRANCH
    }
    # Merge changes as necessary
    git merge --strategy=recursive --strategy-option=theirs
    # Restore local changes
    git stash pop

This needs more testing, but appears to be robust enough for simple use-cases
and should certainly be enough if the user updates before making changes.


### `gitsrc-push`

This is roughly equivalent to following pseudo-code:

    # Stage local changes
    git add .
    # Commit staged changes
    git commit -m "Updated from Lektor"
    # Push
    git push REMOTE BRANCH

You may want to setup the `GIT_COMMITTER_NAME` and `GIT_COMMITTER_EMAIL`
environment variables before running Lektor.


[lektor]: https://www.getlektor.com
[lektorplugins]: https://www.getlektor.com/docs/plugins/
[lektorpublisher]: https://www.getlektor.com/docs/api/publisher/
[gspcode]: https://github.com/camilioneu/lektor-git-src-publisher
[gspissues]: https://github.com/camilioneu/lektor-git-src-publisher/issues
[matrix]: https://matrix.org
[matrixosscml]: https://matrix.to/#/#oss:camilion.eu
[camilion]: https://camilion.eu
[ungleich]: https://ungleich.ch
