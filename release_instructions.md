# Steps for new releases

1. `git flow release start <version>`
2. Change version number in the following places:
    - `.github_changelog_geneartor`
    - `setup.py`
    - each `__init__.py`
3. Run `github_changelog_geneartor`
4. Change `CHANGELOG` so new version has `v` prefix
5. (After committing) `git flow release finish`
6. `git push --all`
7. `git push --tags`
