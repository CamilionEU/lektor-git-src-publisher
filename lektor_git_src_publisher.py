# -*- coding: utf-8 -*-
from lektor.pluginsystem import Plugin
from lektor.publisher import Publisher, _patch_git_env
import subprocess


class GitSrcPublisher(Publisher):
    """
    Helper class to simplify the useful publishers.
    """

    def _git(self, args, **kwargs):
        """
        Run a git command and return a Command object.

        This comes (mostly) from lektor.publisher.GithubPagesPublisher.
        """
        root_path = self._plugin.env.root_path

        kwargs["env"] = _patch_git_env(kwargs.pop("env", None), None)
        kwargs["stdout"] = subprocess.PIPE
        kwargs["universal_newlines"] = True
        kwargs["bufsize"] = 1

        git_cmd = ["git", "-C", root_path]
        git_cmd.extend(args)

        return subprocess.run(git_cmd, **kwargs)

    def _git_output(self, args, **kwargs):
        """
        Run a git Command but return just its output.
        """
        return self._git(args, **kwargs).stdout

    def branch(self, target_url):
        return target_url[1].strip()

    def remote(self):
        """
        Return the configured remote.
        """
        return self._git_output(["remote"]).strip()

    def current_branch(self):
        """
        Return the current branch.
        """
        return self._git_output(["rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def is_in_branch(self, target_url):
        """
        Return True if the current branch matches the target branch,
        or False otherwise.
        """
        current = self.current_branch()
        target = self.branch(target_url)
        return current == target


class GitSrcForcePullPublisher(GitSrcPublisher):
    """
    Simple publisher that pulls external source changes.

    It may cause data loss if the branch can't be pulled cleanly, in which
    case the current directory will be forcibly cleaned and remote data will
    be pulled.

    Use with a publisher in your .lektorproject file with target:
    gitsrc-forcepull://BRANCH

    This will use the default remote and assumes credentials are a
    solved problem, in particular the credentials argument is ignored.
    """

    def publish(self, target_url, credentials=None, **extra):
        yield "Fetching updates...\n"

        yield self._git_output(["fetch", "--progress"])

        yield "Saving any uncommitted changes...\n"

        yield self._git_output(["stash"])

        if not self.is_in_branch(target_url):
            yield "Changing branch as requested...\n"
            yield self._git_output(
                [
                    "checkout",
                    "-b",
                    self.branch(target_url),
                    "-t",
                    self.remote() + "/" + self.branch(target_url),
                ]
            )

        yield "Merging remote changes...\n"
        yield self._git_output(
            ["merge", "--strategy=recursive", "--strategy-option=theirs"]
        )

        yield "Restore any previously uncommitted changes...\n"
        yield self._git_output(["stash", "pop"])

        yield "\nDone!"


class GitSrcPushPublisher(GitSrcPublisher):
    """
    Simple publisher that pushes local source changes.
    It is recommended that any changes start by "publishing" to a
    gitsrc-forcepull target.

    Use with a publisher in your .lektorproject file with target:
    gitsrc-push://BRANCH

    This will use the default remote and assumes credentials are a
    solved problem, in particular the credentials argument is ignored.
    """

    def publish(self, target_url, credentials=None, **extra):
        yield "Staging changes"
        yield self._git_output(["add", "."])

        yield "Commiting changes"
        yield self._git_output(["commit", "-m", "Updated from Lektor"])

        yield "Pushing changes"
        yield self._git_output(["push", self.remote(), self.branch(target_url)])

        yield "\nDone!"


class GitSrcPublisherPlugin(Plugin):
    name = "git-src-publisher"
    description = u"Simple plugin to use Lektor to abstract away git usage."

    def on_setup_env(self, **extra):
        # Add reference to self
        # TODO: is this safe? :-D
        GitSrcForcePullPublisher._plugin = self
        GitSrcPushPublisher._plugin = self

        # Register publishers
        self.env.add_publisher("gitsrc-forcepull", GitSrcForcePullPublisher)
        self.env.add_publisher("gitsrc-push", GitSrcPushPublisher)
