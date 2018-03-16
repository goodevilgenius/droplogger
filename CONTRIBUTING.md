# Contributing to this project

I welcome any contributions to this project.

## Issues

Please feel free to [submit issues](https://github.com/goodevilgenius/droplogger/issues/new) for any bugs you find, or features you think should be implemented.

Please bear in mind that this is a hobby project of mine. I created it primarily for my own use. If you request a feature that I don't feel would contribute much to the functionality of the application, or contradicts my intended use for the application, I will reject it. In that case, you are more than welcome to fork the project, and implement the feature yourself.

If I simply don't have time to implement a feature, I may not act on it right away, but will try to at least respond quickly (within a day or two). In that case, pull requests are welcome.

## Pull Requests

Pull Requests are welcome. Please bear in mind, that I use the [git flow](http://nvie.com/posts/a-successful-git-branching-model/) workflow. My development branch is `devel`, so all pull requests should be made off of `devel`, rather than `master`. The exception to this is any hotfixes to significant bugs, which should be based off of `master` directly.

Again, bear in mind that this project is mainly for my personal use, and if any new features in any pull requests go against my specific use, I won't accept them.

Also, this project is under an [MIT License](LICENSE), so any code accepted in a pull request will fall under that license as well.

## Code of Conduct

I have a [Code of Conduct](CODE_OF_CONDUCT.md) for this project. Any comments on any issues or pull requests (or commit messages) that violate that code of conduct will be ignored and deleted.

## Current state

The application is currently very usable, and stable. The command-line scripts, `droplogger` and `drop-a-log`, work as intended, and the `droplogger.drop_a_log` module works well to add new entries programatically from within another python application.

However, both `droplogger.py` and `drop_a_log.py` are both very messy. Some more code reorganization is definitely needed.

I'm currently tracking these sorts of issues through [Code Climate](https://codeclimate.com/github/goodevilgenius/droplogger/issues). I have also [added several GitHub issues](https://github.com/goodevilgenius/droplogger/issues?q=is%3Aissue+is%3Aopen+label%3Acode-climate) based on CodeClimate's analysis.

If anyone would like to tackle some of these issues, they would be welcome to do so. It will require some code reorganization, however, so if you intend to try and clean up some of the code, please comment on an appropriate issue (or [open a new issue](https://github.com/goodevilgenius/droplogger/issues/new)) to discuss what type of reorganization you think would be beneficial. I'd hate for someone to put in a lot of effor to clean up some of my code, open up a PR, and I have to reject the entire thing because it's going in a completely different route than I intended.

I intend to make no breaking changes to the command-line scripts between 1.0 and 2.0, however, there may be breaking changes to the API during that time.

## My contributions

Currently, at v1.0, I'm very satisfied with it's functionality. Therefore, I won't be contributing much for the present time. I have several other projects I'm going to be focusing on now. I will come back around to it at some point, however. But until then, I'll likely only be contributing by approving PRs by others.
