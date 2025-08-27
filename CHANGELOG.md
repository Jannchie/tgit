## v0.24.0

[v0.23.1...v0.24.0](https://github.com/Jannchie/tgit/compare/v0.23.1...v0.24.0)

### :sparkles: Features

- **version**: support release bump to remove prerelease && handle invalid version strings robustly - By [Jannchie](mailto:jannchie@gmail.com) in [945f42e](https://github.com/Jannchie/tgit/commit/945f42e)
- **version-detect**: add gitignore and venv directory ignore to file detection - By [Jannchie](mailto:jannchie@gmail.com) in [985aaf4](https://github.com/Jannchie/tgit/commit/985aaf4)

### :adhesive_bandage: Fixes

- resolve all ruff linting errors - By [Jannchie](mailto:jannchie@gmail.com) and [Claude](mailto:noreply@anthropic.com) in [61808b6](https://github.com/Jannchie/tgit/commit/61808b6)

### :lipstick: Styles

- **tests**: remove extra blank lines and fix formatting - By [Jannchie](mailto:jannchie@gmail.com) in [7c4947a](https://github.com/Jannchie/tgit/commit/7c4947a)
- **tests**: format test code for consistency - By [Jannchie](mailto:jannchie@gmail.com) in [20d2087](https://github.com/Jannchie/tgit/commit/20d2087)

### :memo: Documentation

- **readme**: add codecov badge - By [Jannchie](mailto:jannchie@gmail.com) in [5e4c4ef](https://github.com/Jannchie/tgit/commit/5e4c4ef)
- **readme**: update codetime badge url - By [Jannchie](mailto:jannchie@gmail.com) in [7d27200](https://github.com/Jannchie/tgit/commit/7d27200)
- **readme**: update usage and module details - By [Jannchie](mailto:jannchie@gmail.com) in [1381044](https://github.com/Jannchie/tgit/commit/1381044)

### :wrench: Chores

- **ci**: add github actions ci workflow - By [Jannchie](mailto:jannchie@gmail.com) in [3d545a0](https://github.com/Jannchie/tgit/commit/3d545a0)

## v0.23.1

[v0.23.0...v0.23.1](https://github.com/Jannchie/tgit/compare/v0.23.0...v0.23.1)

### :adhesive_bandage: Fixes

- **tests**: update model mock value in settings test - By [Jannchie](mailto:jannchie@gmail.com) in [a9ea795](https://github.com/Jannchie/tgit/commit/a9ea795)

### :art: Refactors

- **openai-client**: initialize client with kwargs - By [Jannchie](mailto:jannchie@gmail.com) in [3b5051b](https://github.com/Jannchie/tgit/commit/3b5051b)

## v0.23.0

[v0.22.0...v0.23.0](https://github.com/Jannchie/tgit/compare/v0.22.0...v0.23.0)

### :sparkles: Features

- **changelog**: add up-to-date and empty change checks - By [Jannchie](mailto:jannchie@gmail.com) in [2ab2427](https://github.com/Jannchie/tgit/commit/2ab2427)
- **version**: update cargo toml version in package section only - By [Jannchie](mailto:jannchie@gmail.com) in [4c38ef9](https://github.com/Jannchie/tgit/commit/4c38ef9)

### :wrench: Chores

- update lock file - By [Jannchie](mailto:jannchie@gmail.com) in [184c304](https://github.com/Jannchie/tgit/commit/184c304)

## v0.22.0

[v0.21.1...v0.22.0](https://github.com/Jannchie/tgit/compare/v0.21.1...v0.22.0)

### :rocket: Breaking Changes

- **settings**: unify config and settings command && centralize settings logic in utils - By [Jannchie](mailto:jannchie@gmail.com) in [c51a4c4](https://github.com/Jannchie/tgit/commit/c51a4c4)

### :sparkles: Features

- **version**: detect and display version files before updating - By [Jannchie](mailto:jannchie@gmail.com) in [44f0c36](https://github.com/Jannchie/tgit/commit/44f0c36)

### :memo: Documentation

- **readme**: expand features and usage instructions - By [Jannchie](mailto:jannchie@gmail.com) in [e34a78c](https://github.com/Jannchie/tgit/commit/e34a78c)

## v0.21.1

[v0.21.0...v0.21.1](https://github.com/Jannchie/tgit/compare/v0.21.0...v0.21.1)

### :lipstick: Styles

- **utils**: improve console output formatting - By [Jannchie](mailto:jannchie@gmail.com) in [465f4b4](https://github.com/Jannchie/tgit/commit/465f4b4)

## v0.21.0

[v0.20.0...v0.21.0](https://github.com/Jannchie/tgit/compare/v0.20.0...v0.21.0)

### :rocket: Breaking Changes

- **cli**: replace typer with click for cli commands and tests - By [Jannchie](mailto:jannchie@gmail.com) in [31f8664](https://github.com/Jannchie/tgit/commit/31f8664)

### :adhesive_bandage: Fixes

- **interactive-settings**: improve input cancellation handling && update reset tests && sort filtered diff files - By [Jannchie](mailto:jannchie@gmail.com) in [8307321](https://github.com/Jannchie/tgit/commit/8307321)

### :lipstick: Styles

- **typing**: add explicit type annotations - By [Jannchie](mailto:panjianqi@preferred.jp) in [3f2832b](https://github.com/Jannchie/tgit/commit/3f2832b)
- **utils**: clean up command output formatting - By [Jannchie](mailto:jannchie@gmail.com) in [86bd5e7](https://github.com/Jannchie/tgit/commit/86bd5e7)

### :wrench: Chores

- **deps**: update lock file - By [Jannchie](mailto:jannchie@gmail.com) in [fba0eff](https://github.com/Jannchie/tgit/commit/fba0eff)
- **vscode**: remove coverage-gutters extension && switch python type to debugpy - By [Jannchie](mailto:panjianqi@preferred.jp) in [1cb2cbe](https://github.com/Jannchie/tgit/commit/1cb2cbe)

## v0.20.0

[v0.19.0...v0.20.0](https://github.com/Jannchie/tgit/compare/v0.19.0...v0.20.0)

### :sparkles: Features

- **settings**: add interactive settings command and improve config options - By [Jannchie](mailto:jannchie@gmail.com) in [8f261f6](https://github.com/Jannchie/tgit/commit/8f261f6)

## v0.19.0

[v0.18.0...v0.19.0](https://github.com/Jannchie/tgit/compare/v0.18.0...v0.19.0)

### :rocket: Breaking Changes

- **cli**: migrate argparse to typer for all commands - By [Jannchie](mailto:jannchie@gmail.com) in [ae48a5b](https://github.com/Jannchie/tgit/commit/ae48a5b)
- **settings**: migrate yaml to json for settings && use dataclasses for type safety - By [Jannchie](mailto:jannchie@gmail.com) in [1fd7a0f](https://github.com/Jannchie/tgit/commit/1fd7a0f)

## v0.18.0

[v0.17.1...v0.18.0](https://github.com/Jannchie/tgit/compare/v0.17.1...v0.18.0)

### :sparkles: Features

- **testing**: add unit tests for core modules - By [Jannchie](mailto:jannchie@gmail.com) in [20fa74d](https://github.com/Jannchie/tgit/commit/20fa74d)
- **testing**: add comprehensive pytest test suite and tooling - By [Jannchie](mailto:panjianqi@preferred.jp) in [8cbdb4c](https://github.com/Jannchie/tgit/commit/8cbdb4c)

### :adhesive_bandage: Fixes

- **changelog**: handle commit messages type safety && improve changelog extraction - By [Jannchie](mailto:jannchie@gmail.com) in [c6ecbb5](https://github.com/Jannchie/tgit/commit/c6ecbb5)
- **version**: return input value in pre-release prompt - By [Jannchie](mailto:jannchie@gmail.com) in [124f0e1](https://github.com/Jannchie/tgit/commit/124f0e1)

### :art: Refactors

- **prompts**: replace inquirer with questionary and update user prompts - By [Jannchie](mailto:panjianqi@preferred.jp) in [e16b1a9](https://github.com/Jannchie/tgit/commit/e16b1a9)
- **version**: improve interactive version selection with questionary choices - By [Jannchie](mailto:jannchie@gmail.com) in [cbb51aa](https://github.com/Jannchie/tgit/commit/cbb51aa)

## v0.17.1

[v0.17.0...v0.17.1](https://github.com/Jannchie/tgit/compare/v0.17.0...v0.17.1)

### :art: Refactors

- **ai**: modularize ai client creation and file filtering - By [Jannchie](mailto:jannchie@gmail.com) in [8071a1c](https://github.com/Jannchie/tgit/commit/8071a1c)

## v0.17.0

[v0.16.0...v0.17.0](https://github.com/Jannchie/tgit/compare/v0.16.0...v0.17.0)

### :sparkles: Features

- **changelog**: improve changelog output with panel ui - By [Jianqi Pan](mailto:jannchie@gmail.com) in [15237ca](https://github.com/Jannchie/tgit/commit/15237ca)
- **changelog**: add custom heading render and refactor changelog output - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca81836](https://github.com/Jannchie/tgit/commit/ca81836)

## v0.16.0

[v0.15.1...v0.16.0](https://github.com/Jannchie/tgit/compare/v0.15.1...v0.16.0)

### :sparkles: Features

- **version-changelog**: add interactive changelog generation on version bump - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2c6c3b3](https://github.com/Jannchie/tgit/commit/2c6c3b3)

### :adhesive_bandage: Fixes

- **changelog**: report no changes when changelog empty - By [Jianqi Pan](mailto:jannchie@gmail.com) in [02d94ff](https://github.com/Jannchie/tgit/commit/02d94ff)

### :art: Refactors

- **changelog**: simplify current tag handling in changelog - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ac7903](https://github.com/Jannchie/tgit/commit/6ac7903)

## v0.15.1

[v0.15.0...v0.15.1](https://github.com/Jannchie/tgit/compare/v0.15.0...v0.15.1)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4ab3b1e](https://github.com/Jannchie/tgit/commit/4ab3b1e)

## v0.15.0

[v0.14.2...v0.15.0](https://github.com/Jannchie/tgit/compare/v0.14.2...v0.15.0)

### :sparkles: Features

- **prompts**: revise commit message instructions for clarity - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b58f9ec](https://github.com/Jannchie/tgit/commit/b58f9ec)

## v0.14.2

[v0.14.1...v0.14.2](https://github.com/Jannchie/tgit/compare/v0.14.1...v0.14.2)

### :adhesive_bandage: Fixes

- **version**: fix bump logic for v0 breaking changes to minor - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0f14045](https://github.com/Jannchie/tgit/commit/0f14045)

### :art: Refactors

- **changelog**: extract changelog segment, write helpers && simplify handle logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ebc1e17](https://github.com/Jannchie/tgit/commit/ebc1e17)

### :lipstick: Styles

- **changelog**: add extra newline before old changelog content && remove noqa for rich print import - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca93aaf](https://github.com/Jannchie/tgit/commit/ca93aaf)

### :memo: Documentation

- **changelog**: update changelog for v0.14.0 and v0.14.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3d26e26](https://github.com/Jannchie/tgit/commit/3d26e26)

## v0.14.1

[v0.14.0...v0.14.1](https://github.com/Jannchie/tgit/compare/v0.14.0...v0.14.1)

### :adhesive_bandage: Fixes

- **changelog**: prepend new changelog entries if file exists - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c4b3dff](https://github.com/Jannchie/tgit/commit/c4b3dff)

## v0.14.0

[v0.13.2...v0.14.0](https://github.com/Jannchie/tgit/compare/v0.13.2...v0.14.0)

### :sparkles: Features

- **changelog**: add incremental changelog generation && support appending to existing file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2d193a5](https://github.com/Jannchie/tgit/commit/2d193a5)

### :adhesive_bandage: Fixes

- **changelog**: remove head from default changelog range && update changelog entries - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f6509e3](https://github.com/Jannchie/tgit/commit/f6509e3)

## v0.13.2

[v0.13.1...v0.13.2](https://github.com/Jannchie/tgit/compare/v0.13.1...v0.13.2)

### :adhesive_bandage: Fixes

- **cli**: suppress import error for openai in thread - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4973127](https://github.com/Jannchie/tgit/commit/4973127)

## v0.13.1

[v0.13.0...v0.13.1](https://github.com/Jannchie/tgit/compare/v0.13.0...v0.13.1)

### :adhesive_bandage: Fixes

- **commit**: update no-files message for ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cda3740](https://github.com/Jannchie/tgit/commit/cda3740)

### :wrench: Chores

- **ci**: update build workflow to release only on tag push && replace artifact upload with github release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7548485](https://github.com/Jannchie/tgit/commit/7548485)
- **code-cleanup**: remove unnecessary noqa for print && update changelog and ruff ignore list - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdf5665](https://github.com/Jannchie/tgit/commit/bdf5665)

## v0.13.0

[v0.12.0...v0.13.0](https://github.com/Jannchie/tgit/compare/v0.12.0...v0.13.0)

### :sparkles: Features

- **changelog**: add progress bar and improve tag changelog aggregation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e98fba4](https://github.com/Jannchie/tgit/commit/e98fba4)
- **commit**: filter large diffs and lock files from ai commit msg input && switch from litellm to openai - By [Jianqi Pan](mailto:jannchie@gmail.com) in [587c4d1](https://github.com/Jannchie/tgit/commit/587c4d1)

### :memo: Documentation

- **changelog**: update changelog for v0.13.0 release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e61e8bb](https://github.com/Jannchie/tgit/commit/e61e8bb)

### :wrench: Chores

- **ci**: trigger on tag && simplify commands && upload artifacts only for tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee952df](https://github.com/Jannchie/tgit/commit/ee952df)
- **ci**: add github actions workflow for building python package with uv - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7450f78](https://github.com/Jannchie/tgit/commit/7450f78)

## v0.12.0

[v0.11.2...v0.12.0](https://github.com/Jannchie/tgit/compare/v0.11.2...v0.12.0)

### :sparkles: Features

- **commit**: add console status during ai command generation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [779d2da](https://github.com/Jannchie/tgit/commit/779d2da)
- **commit**: add support for user-specified commit type in get_ai_command && update get_ai_command to handle default commit types - By [Jianqi Pan](mailto:jannchie@gmail.com) in [88f6980](https://github.com/Jannchie/tgit/commit/88f6980)
- **commit**: add branch name to AI commit prompt && update dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [016facc](https://github.com/Jannchie/tgit/commit/016facc)

## v0.11.2

[v0.11.0...v0.11.2](https://github.com/Jannchie/tgit/compare/v0.11.0...v0.11.2)

### :adhesive_bandage: Fixes

- **versioning**: correct cargo.toml regex for version update && update litellm package to 1.64.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdb69c5](https://github.com/Jannchie/tgit/commit/bdb69c5)

### :wrench: Chores

- **dependencies**: update package versions && add beautifulsoup4 dependency && update comments for sys_platform checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c9d14a](https://github.com/Jannchie/tgit/commit/4c9d14a)

## v0.11.0

[v0.10.2...v0.11.0](https://github.com/Jannchie/tgit/compare/v0.10.2...v0.11.0)

### :sparkles: Features

- **cli**: add config command && update dependencies - By [Jannchie](mailto:panjianqi@preferred.jp) in [32d0ecc](https://github.com/Jannchie/tgit/commit/32d0ecc)
- **config, dependencies, commit**: Add configuration command and update dependency versions and AI provider - By [Jannchie](mailto:panjianqi@preferred.jp) in [e446030](https://github.com/Jannchie/tgit/commit/e446030)

### :art: Refactors

- **utils**: update function signature for get_commit_command - By [Jannchie](mailto:panjianqi@preferred.jp) in [4c67c0a](https://github.com/Jannchie/tgit/commit/4c67c0a)

### :memo: Documentation

- **commit**: update commit prompt with class definition - By [Jannchie](mailto:panjianqi@preferred.jp) in [2f5a464](https://github.com/Jannchie/tgit/commit/2f5a464)

### :wrench: Chores

- **dependencies**: add ruff to dev dependencies && update type hints and function signatures - By [Jannchie](mailto:panjianqi@preferred.jp) in [e137b4f](https://github.com/Jannchie/tgit/commit/e137b4f)
- **lock**: update lock file - By [Jannchie](mailto:panjianqi@preferred.jp) in [c4330c5](https://github.com/Jannchie/tgit/commit/c4330c5)

## v0.10.2

[v0.10.1...v0.10.2](https://github.com/Jannchie/tgit/compare/v0.10.1...v0.10.2)

### :adhesive_bandage: Fixes

- **template-rendering**: correct types rendering in commit prompt - By [Jianqi Pan](mailto:jannchie@gmail.com) in [542db82](https://github.com/Jannchie/tgit/commit/542db82)

### :art: Refactors

- **commit-command**: improve function signatures && handle keyword args - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f3bc59](https://github.com/Jannchie/tgit/commit/8f3bc59)

## v0.10.1

[v0.10.0...v0.10.1](https://github.com/Jannchie/tgit/compare/v0.10.0...v0.10.1)

### :adhesive_bandage: Fixes

- **file-open**: open pyproject.toml and Cargo.toml in binary mode - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5ba059a](https://github.com/Jannchie/tgit/commit/5ba059a)

### :art: Refactors

- **project**: revise configuration files && update package dependencies && enhance type annotations - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ff2ecc](https://github.com/Jannchie/tgit/commit/6ff2ecc)
- **version**: modularize version retrieval && extract diff formatting - By [Jianqi Pan](mailto:jannchie@gmail.com) in [9832dfc](https://github.com/Jannchie/tgit/commit/9832dfc)

## v0.10.0

[v0.9.0...v0.10.0](https://github.com/Jannchie/tgit/compare/v0.9.0...v0.10.0)

### :sparkles: Features

- **version**: add support for updating build.gradle.kts version - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c66e792](https://github.com/Jannchie/tgit/commit/c66e792)
- **version**: add custom path support for version handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c79f46](https://github.com/Jannchie/tgit/commit/4c79f46)

## v0.9.0

[v0.8.1...v0.9.0](https://github.com/Jannchie/tgit/compare/v0.8.1...v0.9.0)

### :sparkles: Features

- **add**: implement add command to wrap git add - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e372314](https://github.com/Jannchie/tgit/commit/e372314)
- **version**: add recursive option for version bumping - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c98bf05](https://github.com/Jannchie/tgit/commit/c98bf05)

### :wrench: Chores

- **deps**: update python version and dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3c49d1a](https://github.com/Jannchie/tgit/commit/3c49d1a)

## v0.8.1

[v0.8.0...v0.8.1](https://github.com/Jannchie/tgit/compare/v0.8.0...v0.8.1)

### :lipstick: Styles

- **commit**: update commit message instructions && change import style - By [Jianqi Pan](mailto:jannchie@gmail.com) in [538f27d](https://github.com/Jannchie/tgit/commit/538f27d)

## v0.8.0

[v0.7.1...v0.8.0](https://github.com/Jannchie/tgit/compare/v0.7.1...v0.8.0)

### :sparkles: Features

- **commit**: add 'wip' to commit types and correct invalid type error message - By [Jianqi Pan](mailto:jannchie@gmail.com) in [be64b23](https://github.com/Jannchie/tgit/commit/be64b23)

### :memo: Documentation

- **commit**: clarify role description by specifying message should cover all changes in diff - By [Jianqi Pan](mailto:jannchie@gmail.com) in [486cb2c](https://github.com/Jannchie/tgit/commit/486cb2c)

### :wrench: Chores

- **dependencies**: update dependencies versions in pyproject.toml and lock files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51142a2](https://github.com/Jannchie/tgit/commit/51142a2)
- update readme configuration to include content-type in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [122be13](https://github.com/Jannchie/tgit/commit/122be13)

## v0.7.1

[v0.7.0...v0.7.1](https://github.com/Jannchie/tgit/compare/v0.7.0...v0.7.1)

### :adhesive_bandage: Fixes

- **authentication**: handle openai authentication error - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e2e0e53](https://github.com/Jannchie/tgit/commit/e2e0e53)
- handle invalid git repository error when getting ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c8c4a54](https://github.com/Jannchie/tgit/commit/c8c4a54)

### :wrench: Chores

- update lock files with new dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [537c627](https://github.com/Jannchie/tgit/commit/537c627)

## v0.7.0

[v0.6.1...v0.7.0](https://github.com/Jannchie/tgit/compare/v0.6.1...v0.7.0)

### :sparkles: Features

- **changelog**: add ability to output changelog to a file - By [Jannchie](mailto:panjianqi@preferred.jp) in [b1a52e1](https://github.com/Jannchie/tgit/commit/b1a52e1)

## v0.6.1

[v0.6.0...v0.6.1](https://github.com/Jannchie/tgit/compare/v0.6.0...v0.6.1)

### :adhesive_bandage: Fixes

- **changelog**: simplify sort by scope logic and validate diff before AI command - By [Jannchie](mailto:panjianqi@preferred.jp) in [32dd4e3](https://github.com/Jannchie/tgit/commit/32dd4e3)

### :wrench: Chores

- update gitignore, vscode settings, and pyproject.toml - By [Jannchie](mailto:panjianqi@preferred.jp) in [103271e](https://github.com/Jannchie/tgit/commit/103271e)

## v0.6.0

[v0.5.2...v0.6.0](https://github.com/Jannchie/tgit/compare/v0.5.2...v0.6.0)

### :sparkles: Features

- **version**: introduce auto-detection of version bump based on commit types - By [Jannchie](mailto:panjianqi@preferred.jp) in [910107f](https://github.com/Jannchie/tgit/commit/910107f)

### :art: Refactors

- extract git commit range logic into separate function for better readability - By [Jannchie](mailto:panjianqi@preferred.jp) in [44f9c94](https://github.com/Jannchie/tgit/commit/44f9c94)

## v0.5.2

[v0.5.1...v0.5.2](https://github.com/Jannchie/tgit/compare/v0.5.1...v0.5.2)

### :adhesive_bandage: Fixes

- **commit**: correct commit message formatting and emoji usage - By [Jannchie](mailto:panjianqi@preferred.jp) in [34b58a9](https://github.com/Jannchie/tgit/commit/34b58a9)

## v0.5.1

[v0.5.0...v0.5.1](https://github.com/Jannchie/tgit/compare/v0.5.0...v0.5.1)

### :sparkles: Features

- **commit**: add rich print for missing commit message - By [Jannchie](mailto:panjianqi@preferred.jp) in [686cf4a](https://github.com/Jannchie/tgit/commit/686cf4a)

## v0.5.0

[v0.4.3...v0.5.0](https://github.com/Jannchie/tgit/compare/v0.4.3...v0.5.0)

### :sparkles: Features

- **tgit**: add ai-powered commit message suggestion using openai - By [Jannchie](mailto:panjianqi@preferred.jp) in [93299f1](https://github.com/Jannchie/tgit/commit/93299f1)

## v0.4.3

[v0.4.2...v0.4.3](https://github.com/Jannchie/tgit/compare/v0.4.2...v0.4.3)

### :art: Refactors

- **version**: make the code clearer - By [Jianqi Pan](mailto:jannchie@gmail.com) in [68d626e](https://github.com/Jannchie/tgit/commit/68d626e)

### :memo: Documentation

- add codetime badge - By [Jianqi Pan](mailto:jannchie@gmail.com) in [984b9d3](https://github.com/Jannchie/tgit/commit/984b9d3)

## v0.4.2

[v0.4.1...v0.4.2](https://github.com/Jannchie/tgit/compare/v0.4.1...v0.4.2)

### :adhesive_bandage: Fixes

- **depeendencies**: need python 3.11 because of tomllib - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d7b3c0a](https://github.com/Jannchie/tgit/commit/d7b3c0a)

## v0.4.1

[v0.4.0...v0.4.1](https://github.com/Jannchie/tgit/compare/v0.4.0...v0.4.1)

### :adhesive_bandage: Fixes

- **depeendencies**: add gitpython as dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51bbcb1](https://github.com/Jannchie/tgit/commit/51bbcb1)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/tgit/compare/v0.3.0...v0.4.0)

### :sparkles: Features

- **changelog**: implement basic changelog features - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cf623c6](https://github.com/Jannchie/tgit/commit/cf623c6)

### :adhesive_bandage: Fixes

- **changelog**: check whether the latest commit has a tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [310a306](https://github.com/Jannchie/tgit/commit/310a306)

### :memo: Documentation

- add readme - By [Jianqi Pan](mailto:jannchie@gmail.com) in [1b31cbf](https://github.com/Jannchie/tgit/commit/1b31cbf)

### :wrench: Chores

- **build**: use poetry - By [Jianqi Pan](mailto:jannchie@gmail.com) in [656de25](https://github.com/Jannchie/tgit/commit/656de25)
- **version**: clean the useless code - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0c24d69](https://github.com/Jannchie/tgit/commit/0c24d69)

## v0.3.0

[v0.2.2...v0.3.0](https://github.com/Jannchie/tgit/compare/v0.2.2...v0.3.0)

### :sparkles: Features

- **version**: update more version files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3a87374](https://github.com/Jannchie/tgit/commit/3a87374)
- add gitt as a alias - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bacd8fe](https://github.com/Jannchie/tgit/commit/bacd8fe)

### :wrench: Chores

- **commit**: do not show type choices because they are too long - By [Jianqi Pan](mailto:jannchie@gmail.com) in [886ed07](https://github.com/Jannchie/tgit/commit/886ed07)
- **scripts**: update build script - By [Jianqi Pan](mailto:jannchie@gmail.com) in [89702cd](https://github.com/Jannchie/tgit/commit/89702cd)

## v0.2.2

[v0.2.1...v0.2.2](https://github.com/Jannchie/tgit/compare/v0.2.1...v0.2.2)

### :adhesive_bandage: Fixes

- **commit**: add tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8ea1e80](https://github.com/Jannchie/tgit/commit/8ea1e80)

## v0.2.1

[0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1](https://github.com/Jannchie/tgit/compare/0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1)

### :sparkles: Features

- **commit**: enable emoji settings - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6acd0dc](https://github.com/Jannchie/tgit/commit/6acd0dc)
- **version**: detect version from file or git tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5b4d4aa](https://github.com/Jannchie/tgit/commit/5b4d4aa)

### :adhesive_bandage: Fixes

- **commit**: push tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [35c96a8](https://github.com/Jannchie/tgit/commit/35c96a8)

### :wrench: Chores

- **format**: use sourcery - By [Jianqi Pan](mailto:jannchie@gmail.com) in [03f2078](https://github.com/Jannchie/tgit/commit/03f2078)

## v0.19.1

[v0.19.0...v0.19.1](https://github.com/Jannchie/tgit/compare/v0.19.0...v0.19.1)

## v0.19.0

[v0.18.0...v0.19.0](https://github.com/Jannchie/tgit/compare/v0.18.0...v0.19.0)

### :rocket: Breaking Changes

- **cli**: migrate argparse to typer for all commands - By [Jannchie](mailto:jannchie@gmail.com) in [ae48a5b](https://github.com/Jannchie/tgit/commit/ae48a5b)
- **settings**: migrate yaml to json for settings && use dataclasses for type safety - By [Jannchie](mailto:jannchie@gmail.com) in [1fd7a0f](https://github.com/Jannchie/tgit/commit/1fd7a0f)

## v0.18.0

[v0.17.1...v0.18.0](https://github.com/Jannchie/tgit/compare/v0.17.1...v0.18.0)

### :sparkles: Features

- **testing**: add unit tests for core modules - By [Jannchie](mailto:jannchie@gmail.com) in [20fa74d](https://github.com/Jannchie/tgit/commit/20fa74d)
- **testing**: add comprehensive pytest test suite and tooling - By [Jannchie](mailto:panjianqi@preferred.jp) in [8cbdb4c](https://github.com/Jannchie/tgit/commit/8cbdb4c)

### :adhesive_bandage: Fixes

- **changelog**: handle commit messages type safety && improve changelog extraction - By [Jannchie](mailto:jannchie@gmail.com) in [c6ecbb5](https://github.com/Jannchie/tgit/commit/c6ecbb5)
- **version**: return input value in pre-release prompt - By [Jannchie](mailto:jannchie@gmail.com) in [124f0e1](https://github.com/Jannchie/tgit/commit/124f0e1)

### :art: Refactors

- **prompts**: replace inquirer with questionary and update user prompts - By [Jannchie](mailto:panjianqi@preferred.jp) in [e16b1a9](https://github.com/Jannchie/tgit/commit/e16b1a9)
- **version**: improve interactive version selection with questionary choices - By [Jannchie](mailto:jannchie@gmail.com) in [cbb51aa](https://github.com/Jannchie/tgit/commit/cbb51aa)

## v0.17.1

[v0.17.0...v0.17.1](https://github.com/Jannchie/tgit/compare/v0.17.0...v0.17.1)

### :art: Refactors

- **ai**: modularize ai client creation and file filtering - By [Jannchie](mailto:jannchie@gmail.com) in [8071a1c](https://github.com/Jannchie/tgit/commit/8071a1c)

## v0.17.0

[v0.16.0...v0.17.0](https://github.com/Jannchie/tgit/compare/v0.16.0...v0.17.0)

### :sparkles: Features

- **changelog**: improve changelog output with panel ui - By [Jianqi Pan](mailto:jannchie@gmail.com) in [15237ca](https://github.com/Jannchie/tgit/commit/15237ca)
- **changelog**: add custom heading render and refactor changelog output - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca81836](https://github.com/Jannchie/tgit/commit/ca81836)

## v0.16.0

[v0.15.1...v0.16.0](https://github.com/Jannchie/tgit/compare/v0.15.1...v0.16.0)

### :sparkles: Features

- **version-changelog**: add interactive changelog generation on version bump - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2c6c3b3](https://github.com/Jannchie/tgit/commit/2c6c3b3)

### :adhesive_bandage: Fixes

- **changelog**: report no changes when changelog empty - By [Jianqi Pan](mailto:jannchie@gmail.com) in [02d94ff](https://github.com/Jannchie/tgit/commit/02d94ff)

### :art: Refactors

- **changelog**: simplify current tag handling in changelog - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ac7903](https://github.com/Jannchie/tgit/commit/6ac7903)

## v0.15.1

[v0.15.0...v0.15.1](https://github.com/Jannchie/tgit/compare/v0.15.0...v0.15.1)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4ab3b1e](https://github.com/Jannchie/tgit/commit/4ab3b1e)

## v0.15.0

[v0.14.2...v0.15.0](https://github.com/Jannchie/tgit/compare/v0.14.2...v0.15.0)

### :sparkles: Features

- **prompts**: revise commit message instructions for clarity - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b58f9ec](https://github.com/Jannchie/tgit/commit/b58f9ec)

## v0.14.2

[v0.14.1...v0.14.2](https://github.com/Jannchie/tgit/compare/v0.14.1...v0.14.2)

### :adhesive_bandage: Fixes

- **version**: fix bump logic for v0 breaking changes to minor - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0f14045](https://github.com/Jannchie/tgit/commit/0f14045)

### :art: Refactors

- **changelog**: extract changelog segment, write helpers && simplify handle logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ebc1e17](https://github.com/Jannchie/tgit/commit/ebc1e17)

### :lipstick: Styles

- **changelog**: add extra newline before old changelog content && remove noqa for rich print import - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca93aaf](https://github.com/Jannchie/tgit/commit/ca93aaf)

### :memo: Documentation

- **changelog**: update changelog for v0.14.0 and v0.14.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3d26e26](https://github.com/Jannchie/tgit/commit/3d26e26)

## v0.14.1

[v0.14.0...v0.14.1](https://github.com/Jannchie/tgit/compare/v0.14.0...v0.14.1)

### :adhesive_bandage: Fixes

- **changelog**: prepend new changelog entries if file exists - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c4b3dff](https://github.com/Jannchie/tgit/commit/c4b3dff)

## v0.14.0

[v0.13.2...v0.14.0](https://github.com/Jannchie/tgit/compare/v0.13.2...v0.14.0)

### :sparkles: Features

- **changelog**: add incremental changelog generation && support appending to existing file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2d193a5](https://github.com/Jannchie/tgit/commit/2d193a5)

### :adhesive_bandage: Fixes

- **changelog**: remove head from default changelog range && update changelog entries - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f6509e3](https://github.com/Jannchie/tgit/commit/f6509e3)

## v0.13.2

[v0.13.1...v0.13.2](https://github.com/Jannchie/tgit/compare/v0.13.1...v0.13.2)

### :adhesive_bandage: Fixes

- **cli**: suppress import error for openai in thread - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4973127](https://github.com/Jannchie/tgit/commit/4973127)

## v0.13.1

[v0.13.0...v0.13.1](https://github.com/Jannchie/tgit/compare/v0.13.0...v0.13.1)

### :adhesive_bandage: Fixes

- **commit**: update no-files message for ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cda3740](https://github.com/Jannchie/tgit/commit/cda3740)

### :wrench: Chores

- **ci**: update build workflow to release only on tag push && replace artifact upload with github release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7548485](https://github.com/Jannchie/tgit/commit/7548485)
- **code-cleanup**: remove unnecessary noqa for print && update changelog and ruff ignore list - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdf5665](https://github.com/Jannchie/tgit/commit/bdf5665)

## v0.13.0

[v0.12.0...v0.13.0](https://github.com/Jannchie/tgit/compare/v0.12.0...v0.13.0)

### :sparkles: Features

- **changelog**: add progress bar and improve tag changelog aggregation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e98fba4](https://github.com/Jannchie/tgit/commit/e98fba4)
- **commit**: filter large diffs and lock files from ai commit msg input && switch from litellm to openai - By [Jianqi Pan](mailto:jannchie@gmail.com) in [587c4d1](https://github.com/Jannchie/tgit/commit/587c4d1)

### :memo: Documentation

- **changelog**: update changelog for v0.13.0 release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e61e8bb](https://github.com/Jannchie/tgit/commit/e61e8bb)

### :wrench: Chores

- **ci**: trigger on tag && simplify commands && upload artifacts only for tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee952df](https://github.com/Jannchie/tgit/commit/ee952df)
- **ci**: add github actions workflow for building python package with uv - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7450f78](https://github.com/Jannchie/tgit/commit/7450f78)

## v0.12.0

[v0.11.2...v0.12.0](https://github.com/Jannchie/tgit/compare/v0.11.2...v0.12.0)

### :sparkles: Features

- **commit**: add console status during ai command generation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [779d2da](https://github.com/Jannchie/tgit/commit/779d2da)
- **commit**: add support for user-specified commit type in get_ai_command && update get_ai_command to handle default commit types - By [Jianqi Pan](mailto:jannchie@gmail.com) in [88f6980](https://github.com/Jannchie/tgit/commit/88f6980)
- **commit**: add branch name to AI commit prompt && update dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [016facc](https://github.com/Jannchie/tgit/commit/016facc)

## v0.11.2

[v0.11.0...v0.11.2](https://github.com/Jannchie/tgit/compare/v0.11.0...v0.11.2)

### :adhesive_bandage: Fixes

- **versioning**: correct cargo.toml regex for version update && update litellm package to 1.64.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdb69c5](https://github.com/Jannchie/tgit/commit/bdb69c5)

### :wrench: Chores

- **dependencies**: update package versions && add beautifulsoup4 dependency && update comments for sys_platform checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c9d14a](https://github.com/Jannchie/tgit/commit/4c9d14a)

## v0.11.0

[v0.10.2...v0.11.0](https://github.com/Jannchie/tgit/compare/v0.10.2...v0.11.0)

### :sparkles: Features

- **cli**: add config command && update dependencies - By [Jannchie](mailto:panjianqi@preferred.jp) in [32d0ecc](https://github.com/Jannchie/tgit/commit/32d0ecc)
- **config, dependencies, commit**: Add configuration command and update dependency versions and AI provider - By [Jannchie](mailto:panjianqi@preferred.jp) in [e446030](https://github.com/Jannchie/tgit/commit/e446030)

### :art: Refactors

- **utils**: update function signature for get_commit_command - By [Jannchie](mailto:panjianqi@preferred.jp) in [4c67c0a](https://github.com/Jannchie/tgit/commit/4c67c0a)

### :memo: Documentation

- **commit**: update commit prompt with class definition - By [Jannchie](mailto:panjianqi@preferred.jp) in [2f5a464](https://github.com/Jannchie/tgit/commit/2f5a464)

### :wrench: Chores

- **dependencies**: add ruff to dev dependencies && update type hints and function signatures - By [Jannchie](mailto:panjianqi@preferred.jp) in [e137b4f](https://github.com/Jannchie/tgit/commit/e137b4f)
- **lock**: update lock file - By [Jannchie](mailto:panjianqi@preferred.jp) in [c4330c5](https://github.com/Jannchie/tgit/commit/c4330c5)

## v0.10.2

[v0.10.1...v0.10.2](https://github.com/Jannchie/tgit/compare/v0.10.1...v0.10.2)

### :adhesive_bandage: Fixes

- **template-rendering**: correct types rendering in commit prompt - By [Jianqi Pan](mailto:jannchie@gmail.com) in [542db82](https://github.com/Jannchie/tgit/commit/542db82)

### :art: Refactors

- **commit-command**: improve function signatures && handle keyword args - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f3bc59](https://github.com/Jannchie/tgit/commit/8f3bc59)

## v0.10.1

[v0.10.0...v0.10.1](https://github.com/Jannchie/tgit/compare/v0.10.0...v0.10.1)

### :adhesive_bandage: Fixes

- **file-open**: open pyproject.toml and Cargo.toml in binary mode - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5ba059a](https://github.com/Jannchie/tgit/commit/5ba059a)

### :art: Refactors

- **project**: revise configuration files && update package dependencies && enhance type annotations - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ff2ecc](https://github.com/Jannchie/tgit/commit/6ff2ecc)
- **version**: modularize version retrieval && extract diff formatting - By [Jianqi Pan](mailto:jannchie@gmail.com) in [9832dfc](https://github.com/Jannchie/tgit/commit/9832dfc)

## v0.10.0

[v0.9.0...v0.10.0](https://github.com/Jannchie/tgit/compare/v0.9.0...v0.10.0)

### :sparkles: Features

- **version**: add support for updating build.gradle.kts version - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c66e792](https://github.com/Jannchie/tgit/commit/c66e792)
- **version**: add custom path support for version handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c79f46](https://github.com/Jannchie/tgit/commit/4c79f46)

## v0.9.0

[v0.8.1...v0.9.0](https://github.com/Jannchie/tgit/compare/v0.8.1...v0.9.0)

### :sparkles: Features

- **add**: implement add command to wrap git add - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e372314](https://github.com/Jannchie/tgit/commit/e372314)
- **version**: add recursive option for version bumping - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c98bf05](https://github.com/Jannchie/tgit/commit/c98bf05)

### :wrench: Chores

- **deps**: update python version and dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3c49d1a](https://github.com/Jannchie/tgit/commit/3c49d1a)

## v0.8.1

[v0.8.0...v0.8.1](https://github.com/Jannchie/tgit/compare/v0.8.0...v0.8.1)

### :lipstick: Styles

- **commit**: update commit message instructions && change import style - By [Jianqi Pan](mailto:jannchie@gmail.com) in [538f27d](https://github.com/Jannchie/tgit/commit/538f27d)

## v0.8.0

[v0.7.1...v0.8.0](https://github.com/Jannchie/tgit/compare/v0.7.1...v0.8.0)

### :sparkles: Features

- **commit**: add 'wip' to commit types and correct invalid type error message - By [Jianqi Pan](mailto:jannchie@gmail.com) in [be64b23](https://github.com/Jannchie/tgit/commit/be64b23)

### :memo: Documentation

- **commit**: clarify role description by specifying message should cover all changes in diff - By [Jianqi Pan](mailto:jannchie@gmail.com) in [486cb2c](https://github.com/Jannchie/tgit/commit/486cb2c)

### :wrench: Chores

- **dependencies**: update dependencies versions in pyproject.toml and lock files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51142a2](https://github.com/Jannchie/tgit/commit/51142a2)
- update readme configuration to include content-type in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [122be13](https://github.com/Jannchie/tgit/commit/122be13)

## v0.7.1

[v0.7.0...v0.7.1](https://github.com/Jannchie/tgit/compare/v0.7.0...v0.7.1)

### :adhesive_bandage: Fixes

- **authentication**: handle openai authentication error - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e2e0e53](https://github.com/Jannchie/tgit/commit/e2e0e53)
- handle invalid git repository error when getting ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c8c4a54](https://github.com/Jannchie/tgit/commit/c8c4a54)

### :wrench: Chores

- update lock files with new dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [537c627](https://github.com/Jannchie/tgit/commit/537c627)

## v0.7.0

[v0.6.1...v0.7.0](https://github.com/Jannchie/tgit/compare/v0.6.1...v0.7.0)

### :sparkles: Features

- **changelog**: add ability to output changelog to a file - By [Jannchie](mailto:panjianqi@preferred.jp) in [b1a52e1](https://github.com/Jannchie/tgit/commit/b1a52e1)

## v0.6.1

[v0.6.0...v0.6.1](https://github.com/Jannchie/tgit/compare/v0.6.0...v0.6.1)

### :adhesive_bandage: Fixes

- **changelog**: simplify sort by scope logic and validate diff before AI command - By [Jannchie](mailto:panjianqi@preferred.jp) in [32dd4e3](https://github.com/Jannchie/tgit/commit/32dd4e3)

### :wrench: Chores

- update gitignore, vscode settings, and pyproject.toml - By [Jannchie](mailto:panjianqi@preferred.jp) in [103271e](https://github.com/Jannchie/tgit/commit/103271e)

## v0.6.0

[v0.5.2...v0.6.0](https://github.com/Jannchie/tgit/compare/v0.5.2...v0.6.0)

### :sparkles: Features

- **version**: introduce auto-detection of version bump based on commit types - By [Jannchie](mailto:panjianqi@preferred.jp) in [910107f](https://github.com/Jannchie/tgit/commit/910107f)

### :art: Refactors

- extract git commit range logic into separate function for better readability - By [Jannchie](mailto:panjianqi@preferred.jp) in [44f9c94](https://github.com/Jannchie/tgit/commit/44f9c94)

## v0.5.2

[v0.5.1...v0.5.2](https://github.com/Jannchie/tgit/compare/v0.5.1...v0.5.2)

### :adhesive_bandage: Fixes

- **commit**: correct commit message formatting and emoji usage - By [Jannchie](mailto:panjianqi@preferred.jp) in [34b58a9](https://github.com/Jannchie/tgit/commit/34b58a9)

## v0.5.1

[v0.5.0...v0.5.1](https://github.com/Jannchie/tgit/compare/v0.5.0...v0.5.1)

### :sparkles: Features

- **commit**: add rich print for missing commit message - By [Jannchie](mailto:panjianqi@preferred.jp) in [686cf4a](https://github.com/Jannchie/tgit/commit/686cf4a)

## v0.5.0

[v0.4.3...v0.5.0](https://github.com/Jannchie/tgit/compare/v0.4.3...v0.5.0)

### :sparkles: Features

- **tgit**: add ai-powered commit message suggestion using openai - By [Jannchie](mailto:panjianqi@preferred.jp) in [93299f1](https://github.com/Jannchie/tgit/commit/93299f1)

## v0.4.3

[v0.4.2...v0.4.3](https://github.com/Jannchie/tgit/compare/v0.4.2...v0.4.3)

### :art: Refactors

- **version**: make the code clearer - By [Jianqi Pan](mailto:jannchie@gmail.com) in [68d626e](https://github.com/Jannchie/tgit/commit/68d626e)

### :memo: Documentation

- add codetime badge - By [Jianqi Pan](mailto:jannchie@gmail.com) in [984b9d3](https://github.com/Jannchie/tgit/commit/984b9d3)

## v0.4.2

[v0.4.1...v0.4.2](https://github.com/Jannchie/tgit/compare/v0.4.1...v0.4.2)

### :adhesive_bandage: Fixes

- **depeendencies**: need python 3.11 because of tomllib - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d7b3c0a](https://github.com/Jannchie/tgit/commit/d7b3c0a)

## v0.4.1

[v0.4.0...v0.4.1](https://github.com/Jannchie/tgit/compare/v0.4.0...v0.4.1)

### :adhesive_bandage: Fixes

- **depeendencies**: add gitpython as dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51bbcb1](https://github.com/Jannchie/tgit/commit/51bbcb1)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/tgit/compare/v0.3.0...v0.4.0)

### :sparkles: Features

- **changelog**: implement basic changelog features - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cf623c6](https://github.com/Jannchie/tgit/commit/cf623c6)

### :adhesive_bandage: Fixes

- **changelog**: check whether the latest commit has a tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [310a306](https://github.com/Jannchie/tgit/commit/310a306)

### :memo: Documentation

- add readme - By [Jianqi Pan](mailto:jannchie@gmail.com) in [1b31cbf](https://github.com/Jannchie/tgit/commit/1b31cbf)

### :wrench: Chores

- **build**: use poetry - By [Jianqi Pan](mailto:jannchie@gmail.com) in [656de25](https://github.com/Jannchie/tgit/commit/656de25)
- **version**: clean the useless code - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0c24d69](https://github.com/Jannchie/tgit/commit/0c24d69)

## v0.3.0

[v0.2.2...v0.3.0](https://github.com/Jannchie/tgit/compare/v0.2.2...v0.3.0)

### :sparkles: Features

- **version**: update more version files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3a87374](https://github.com/Jannchie/tgit/commit/3a87374)
- add gitt as a alias - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bacd8fe](https://github.com/Jannchie/tgit/commit/bacd8fe)

### :wrench: Chores

- **commit**: do not show type choices because they are too long - By [Jianqi Pan](mailto:jannchie@gmail.com) in [886ed07](https://github.com/Jannchie/tgit/commit/886ed07)
- **scripts**: update build script - By [Jianqi Pan](mailto:jannchie@gmail.com) in [89702cd](https://github.com/Jannchie/tgit/commit/89702cd)

## v0.2.2

[v0.2.1...v0.2.2](https://github.com/Jannchie/tgit/compare/v0.2.1...v0.2.2)

### :adhesive_bandage: Fixes

- **commit**: add tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8ea1e80](https://github.com/Jannchie/tgit/commit/8ea1e80)

## v0.2.1

[0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1](https://github.com/Jannchie/tgit/compare/0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1)

### :sparkles: Features

- **commit**: enable emoji settings - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6acd0dc](https://github.com/Jannchie/tgit/commit/6acd0dc)
- **version**: detect version from file or git tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5b4d4aa](https://github.com/Jannchie/tgit/commit/5b4d4aa)

### :adhesive_bandage: Fixes

- **commit**: push tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [35c96a8](https://github.com/Jannchie/tgit/commit/35c96a8)

### :wrench: Chores

- **format**: use sourcery - By [Jianqi Pan](mailto:jannchie@gmail.com) in [03f2078](https://github.com/Jannchie/tgit/commit/03f2078)

## v0.19.0

[v0.18.0...v0.19.0](https://github.com/Jannchie/tgit/compare/v0.18.0...v0.19.0)

### :rocket: Breaking Changes

- **cli**: migrate argparse to typer for all commands - By [Jannchie](mailto:jannchie@gmail.com) in [ae48a5b](https://github.com/Jannchie/tgit/commit/ae48a5b)
- **settings**: migrate yaml to json for settings && use dataclasses for type safety - By [Jannchie](mailto:jannchie@gmail.com) in [1fd7a0f](https://github.com/Jannchie/tgit/commit/1fd7a0f)

## v0.18.0

[v0.17.1...v0.18.0](https://github.com/Jannchie/tgit/compare/v0.17.1...v0.18.0)

### :sparkles: Features

- **testing**: add unit tests for core modules - By [Jannchie](mailto:jannchie@gmail.com) in [20fa74d](https://github.com/Jannchie/tgit/commit/20fa74d)
- **testing**: add comprehensive pytest test suite and tooling - By [Jannchie](mailto:panjianqi@preferred.jp) in [8cbdb4c](https://github.com/Jannchie/tgit/commit/8cbdb4c)

### :adhesive_bandage: Fixes

- **changelog**: handle commit messages type safety && improve changelog extraction - By [Jannchie](mailto:jannchie@gmail.com) in [c6ecbb5](https://github.com/Jannchie/tgit/commit/c6ecbb5)
- **version**: return input value in pre-release prompt - By [Jannchie](mailto:jannchie@gmail.com) in [124f0e1](https://github.com/Jannchie/tgit/commit/124f0e1)

### :art: Refactors

- **prompts**: replace inquirer with questionary and update user prompts - By [Jannchie](mailto:panjianqi@preferred.jp) in [e16b1a9](https://github.com/Jannchie/tgit/commit/e16b1a9)
- **version**: improve interactive version selection with questionary choices - By [Jannchie](mailto:jannchie@gmail.com) in [cbb51aa](https://github.com/Jannchie/tgit/commit/cbb51aa)

## v0.17.1

[v0.17.0...v0.17.1](https://github.com/Jannchie/tgit/compare/v0.17.0...v0.17.1)

### :art: Refactors

- **ai**: modularize ai client creation and file filtering - By [Jannchie](mailto:jannchie@gmail.com) in [8071a1c](https://github.com/Jannchie/tgit/commit/8071a1c)

## v0.17.0

[v0.16.0...v0.17.0](https://github.com/Jannchie/tgit/compare/v0.16.0...v0.17.0)

### :sparkles: Features

- **changelog**: improve changelog output with panel ui - By [Jianqi Pan](mailto:jannchie@gmail.com) in [15237ca](https://github.com/Jannchie/tgit/commit/15237ca)
- **changelog**: add custom heading render and refactor changelog output - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca81836](https://github.com/Jannchie/tgit/commit/ca81836)

## v0.16.0

[v0.15.1...v0.16.0](https://github.com/Jannchie/tgit/compare/v0.15.1...v0.16.0)

### :sparkles: Features

- **version-changelog**: add interactive changelog generation on version bump - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2c6c3b3](https://github.com/Jannchie/tgit/commit/2c6c3b3)

### :adhesive_bandage: Fixes

- **changelog**: report no changes when changelog empty - By [Jianqi Pan](mailto:jannchie@gmail.com) in [02d94ff](https://github.com/Jannchie/tgit/commit/02d94ff)

### :art: Refactors

- **changelog**: simplify current tag handling in changelog - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ac7903](https://github.com/Jannchie/tgit/commit/6ac7903)

## v0.15.1

[v0.15.0...v0.15.1](https://github.com/Jannchie/tgit/compare/v0.15.0...v0.15.1)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4ab3b1e](https://github.com/Jannchie/tgit/commit/4ab3b1e)

## v0.15.0

[v0.14.2...v0.15.0](https://github.com/Jannchie/tgit/compare/v0.14.2...v0.15.0)

### :sparkles: Features

- **prompts**: revise commit message instructions for clarity - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b58f9ec](https://github.com/Jannchie/tgit/commit/b58f9ec)

## v0.14.2

[v0.14.1...v0.14.2](https://github.com/Jannchie/tgit/compare/v0.14.1...v0.14.2)

### :adhesive_bandage: Fixes

- **version**: fix bump logic for v0 breaking changes to minor - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0f14045](https://github.com/Jannchie/tgit/commit/0f14045)

### :art: Refactors

- **changelog**: extract changelog segment, write helpers && simplify handle logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ebc1e17](https://github.com/Jannchie/tgit/commit/ebc1e17)

### :lipstick: Styles

- **changelog**: add extra newline before old changelog content && remove noqa for rich print import - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca93aaf](https://github.com/Jannchie/tgit/commit/ca93aaf)

### :memo: Documentation

- **changelog**: update changelog for v0.14.0 and v0.14.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3d26e26](https://github.com/Jannchie/tgit/commit/3d26e26)

## v0.14.1

[v0.14.0...v0.14.1](https://github.com/Jannchie/tgit/compare/v0.14.0...v0.14.1)

### :adhesive_bandage: Fixes

- **changelog**: prepend new changelog entries if file exists - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c4b3dff](https://github.com/Jannchie/tgit/commit/c4b3dff)

## v0.14.0

[v0.13.2...v0.14.0](https://github.com/Jannchie/tgit/compare/v0.13.2...v0.14.0)

### :sparkles: Features

- **changelog**: add incremental changelog generation && support appending to existing file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2d193a5](https://github.com/Jannchie/tgit/commit/2d193a5)

### :adhesive_bandage: Fixes

- **changelog**: remove head from default changelog range && update changelog entries - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f6509e3](https://github.com/Jannchie/tgit/commit/f6509e3)

## v0.13.2

[v0.13.1...v0.13.2](https://github.com/Jannchie/tgit/compare/v0.13.1...v0.13.2)

### :adhesive_bandage: Fixes

- **cli**: suppress import error for openai in thread - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4973127](https://github.com/Jannchie/tgit/commit/4973127)

## v0.13.1

[v0.13.0...v0.13.1](https://github.com/Jannchie/tgit/compare/v0.13.0...v0.13.1)

### :adhesive_bandage: Fixes

- **commit**: update no-files message for ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cda3740](https://github.com/Jannchie/tgit/commit/cda3740)

### :wrench: Chores

- **ci**: update build workflow to release only on tag push && replace artifact upload with github release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7548485](https://github.com/Jannchie/tgit/commit/7548485)
- **code-cleanup**: remove unnecessary noqa for print && update changelog and ruff ignore list - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdf5665](https://github.com/Jannchie/tgit/commit/bdf5665)

## v0.13.0

[v0.12.0...v0.13.0](https://github.com/Jannchie/tgit/compare/v0.12.0...v0.13.0)

### :sparkles: Features

- **changelog**: add progress bar and improve tag changelog aggregation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e98fba4](https://github.com/Jannchie/tgit/commit/e98fba4)
- **commit**: filter large diffs and lock files from ai commit msg input && switch from litellm to openai - By [Jianqi Pan](mailto:jannchie@gmail.com) in [587c4d1](https://github.com/Jannchie/tgit/commit/587c4d1)

### :memo: Documentation

- **changelog**: update changelog for v0.13.0 release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e61e8bb](https://github.com/Jannchie/tgit/commit/e61e8bb)

### :wrench: Chores

- **ci**: trigger on tag && simplify commands && upload artifacts only for tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee952df](https://github.com/Jannchie/tgit/commit/ee952df)
- **ci**: add github actions workflow for building python package with uv - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7450f78](https://github.com/Jannchie/tgit/commit/7450f78)

## v0.12.0

[v0.11.2...v0.12.0](https://github.com/Jannchie/tgit/compare/v0.11.2...v0.12.0)

### :sparkles: Features

- **commit**: add console status during ai command generation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [779d2da](https://github.com/Jannchie/tgit/commit/779d2da)
- **commit**: add support for user-specified commit type in get_ai_command && update get_ai_command to handle default commit types - By [Jianqi Pan](mailto:jannchie@gmail.com) in [88f6980](https://github.com/Jannchie/tgit/commit/88f6980)
- **commit**: add branch name to AI commit prompt && update dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [016facc](https://github.com/Jannchie/tgit/commit/016facc)

## v0.11.2

[v0.11.0...v0.11.2](https://github.com/Jannchie/tgit/compare/v0.11.0...v0.11.2)

### :adhesive_bandage: Fixes

- **versioning**: correct cargo.toml regex for version update && update litellm package to 1.64.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdb69c5](https://github.com/Jannchie/tgit/commit/bdb69c5)

### :wrench: Chores

- **dependencies**: update package versions && add beautifulsoup4 dependency && update comments for sys_platform checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c9d14a](https://github.com/Jannchie/tgit/commit/4c9d14a)

## v0.11.0

[v0.10.2...v0.11.0](https://github.com/Jannchie/tgit/compare/v0.10.2...v0.11.0)

### :sparkles: Features

- **cli**: add config command && update dependencies - By [Jannchie](mailto:panjianqi@preferred.jp) in [32d0ecc](https://github.com/Jannchie/tgit/commit/32d0ecc)
- **config, dependencies, commit**: Add configuration command and update dependency versions and AI provider - By [Jannchie](mailto:panjianqi@preferred.jp) in [e446030](https://github.com/Jannchie/tgit/commit/e446030)

### :art: Refactors

- **utils**: update function signature for get_commit_command - By [Jannchie](mailto:panjianqi@preferred.jp) in [4c67c0a](https://github.com/Jannchie/tgit/commit/4c67c0a)

### :memo: Documentation

- **commit**: update commit prompt with class definition - By [Jannchie](mailto:panjianqi@preferred.jp) in [2f5a464](https://github.com/Jannchie/tgit/commit/2f5a464)

### :wrench: Chores

- **dependencies**: add ruff to dev dependencies && update type hints and function signatures - By [Jannchie](mailto:panjianqi@preferred.jp) in [e137b4f](https://github.com/Jannchie/tgit/commit/e137b4f)
- **lock**: update lock file - By [Jannchie](mailto:panjianqi@preferred.jp) in [c4330c5](https://github.com/Jannchie/tgit/commit/c4330c5)

## v0.10.2

[v0.10.1...v0.10.2](https://github.com/Jannchie/tgit/compare/v0.10.1...v0.10.2)

### :adhesive_bandage: Fixes

- **template-rendering**: correct types rendering in commit prompt - By [Jianqi Pan](mailto:jannchie@gmail.com) in [542db82](https://github.com/Jannchie/tgit/commit/542db82)

### :art: Refactors

- **commit-command**: improve function signatures && handle keyword args - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f3bc59](https://github.com/Jannchie/tgit/commit/8f3bc59)

## v0.10.1

[v0.10.0...v0.10.1](https://github.com/Jannchie/tgit/compare/v0.10.0...v0.10.1)

### :adhesive_bandage: Fixes

- **file-open**: open pyproject.toml and Cargo.toml in binary mode - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5ba059a](https://github.com/Jannchie/tgit/commit/5ba059a)

### :art: Refactors

- **project**: revise configuration files && update package dependencies && enhance type annotations - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ff2ecc](https://github.com/Jannchie/tgit/commit/6ff2ecc)
- **version**: modularize version retrieval && extract diff formatting - By [Jianqi Pan](mailto:jannchie@gmail.com) in [9832dfc](https://github.com/Jannchie/tgit/commit/9832dfc)

## v0.10.0

[v0.9.0...v0.10.0](https://github.com/Jannchie/tgit/compare/v0.9.0...v0.10.0)

### :sparkles: Features

- **version**: add support for updating build.gradle.kts version - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c66e792](https://github.com/Jannchie/tgit/commit/c66e792)
- **version**: add custom path support for version handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c79f46](https://github.com/Jannchie/tgit/commit/4c79f46)

## v0.9.0

[v0.8.1...v0.9.0](https://github.com/Jannchie/tgit/compare/v0.8.1...v0.9.0)

### :sparkles: Features

- **add**: implement add command to wrap git add - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e372314](https://github.com/Jannchie/tgit/commit/e372314)
- **version**: add recursive option for version bumping - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c98bf05](https://github.com/Jannchie/tgit/commit/c98bf05)

### :wrench: Chores

- **deps**: update python version and dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3c49d1a](https://github.com/Jannchie/tgit/commit/3c49d1a)

## v0.8.1

[v0.8.0...v0.8.1](https://github.com/Jannchie/tgit/compare/v0.8.0...v0.8.1)

### :lipstick: Styles

- **commit**: update commit message instructions && change import style - By [Jianqi Pan](mailto:jannchie@gmail.com) in [538f27d](https://github.com/Jannchie/tgit/commit/538f27d)

## v0.8.0

[v0.7.1...v0.8.0](https://github.com/Jannchie/tgit/compare/v0.7.1...v0.8.0)

### :sparkles: Features

- **commit**: add 'wip' to commit types and correct invalid type error message - By [Jianqi Pan](mailto:jannchie@gmail.com) in [be64b23](https://github.com/Jannchie/tgit/commit/be64b23)

### :memo: Documentation

- **commit**: clarify role description by specifying message should cover all changes in diff - By [Jianqi Pan](mailto:jannchie@gmail.com) in [486cb2c](https://github.com/Jannchie/tgit/commit/486cb2c)

### :wrench: Chores

- **dependencies**: update dependencies versions in pyproject.toml and lock files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51142a2](https://github.com/Jannchie/tgit/commit/51142a2)
- update readme configuration to include content-type in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [122be13](https://github.com/Jannchie/tgit/commit/122be13)

## v0.7.1

[v0.7.0...v0.7.1](https://github.com/Jannchie/tgit/compare/v0.7.0...v0.7.1)

### :adhesive_bandage: Fixes

- **authentication**: handle openai authentication error - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e2e0e53](https://github.com/Jannchie/tgit/commit/e2e0e53)
- handle invalid git repository error when getting ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c8c4a54](https://github.com/Jannchie/tgit/commit/c8c4a54)

### :wrench: Chores

- update lock files with new dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [537c627](https://github.com/Jannchie/tgit/commit/537c627)

## v0.7.0

[v0.6.1...v0.7.0](https://github.com/Jannchie/tgit/compare/v0.6.1...v0.7.0)

### :sparkles: Features

- **changelog**: add ability to output changelog to a file - By [Jannchie](mailto:panjianqi@preferred.jp) in [b1a52e1](https://github.com/Jannchie/tgit/commit/b1a52e1)

## v0.6.1

[v0.6.0...v0.6.1](https://github.com/Jannchie/tgit/compare/v0.6.0...v0.6.1)

### :adhesive_bandage: Fixes

- **changelog**: simplify sort by scope logic and validate diff before AI command - By [Jannchie](mailto:panjianqi@preferred.jp) in [32dd4e3](https://github.com/Jannchie/tgit/commit/32dd4e3)

### :wrench: Chores

- update gitignore, vscode settings, and pyproject.toml - By [Jannchie](mailto:panjianqi@preferred.jp) in [103271e](https://github.com/Jannchie/tgit/commit/103271e)

## v0.6.0

[v0.5.2...v0.6.0](https://github.com/Jannchie/tgit/compare/v0.5.2...v0.6.0)

### :sparkles: Features

- **version**: introduce auto-detection of version bump based on commit types - By [Jannchie](mailto:panjianqi@preferred.jp) in [910107f](https://github.com/Jannchie/tgit/commit/910107f)

### :art: Refactors

- extract git commit range logic into separate function for better readability - By [Jannchie](mailto:panjianqi@preferred.jp) in [44f9c94](https://github.com/Jannchie/tgit/commit/44f9c94)

## v0.5.2

[v0.5.1...v0.5.2](https://github.com/Jannchie/tgit/compare/v0.5.1...v0.5.2)

### :adhesive_bandage: Fixes

- **commit**: correct commit message formatting and emoji usage - By [Jannchie](mailto:panjianqi@preferred.jp) in [34b58a9](https://github.com/Jannchie/tgit/commit/34b58a9)

## v0.5.1

[v0.5.0...v0.5.1](https://github.com/Jannchie/tgit/compare/v0.5.0...v0.5.1)

### :sparkles: Features

- **commit**: add rich print for missing commit message - By [Jannchie](mailto:panjianqi@preferred.jp) in [686cf4a](https://github.com/Jannchie/tgit/commit/686cf4a)

## v0.5.0

[v0.4.3...v0.5.0](https://github.com/Jannchie/tgit/compare/v0.4.3...v0.5.0)

### :sparkles: Features

- **tgit**: add ai-powered commit message suggestion using openai - By [Jannchie](mailto:panjianqi@preferred.jp) in [93299f1](https://github.com/Jannchie/tgit/commit/93299f1)

## v0.4.3

[v0.4.2...v0.4.3](https://github.com/Jannchie/tgit/compare/v0.4.2...v0.4.3)

### :art: Refactors

- **version**: make the code clearer - By [Jianqi Pan](mailto:jannchie@gmail.com) in [68d626e](https://github.com/Jannchie/tgit/commit/68d626e)

### :memo: Documentation

- add codetime badge - By [Jianqi Pan](mailto:jannchie@gmail.com) in [984b9d3](https://github.com/Jannchie/tgit/commit/984b9d3)

## v0.4.2

[v0.4.1...v0.4.2](https://github.com/Jannchie/tgit/compare/v0.4.1...v0.4.2)

### :adhesive_bandage: Fixes

- **depeendencies**: need python 3.11 because of tomllib - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d7b3c0a](https://github.com/Jannchie/tgit/commit/d7b3c0a)

## v0.4.1

[v0.4.0...v0.4.1](https://github.com/Jannchie/tgit/compare/v0.4.0...v0.4.1)

### :adhesive_bandage: Fixes

- **depeendencies**: add gitpython as dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51bbcb1](https://github.com/Jannchie/tgit/commit/51bbcb1)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/tgit/compare/v0.3.0...v0.4.0)

### :sparkles: Features

- **changelog**: implement basic changelog features - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cf623c6](https://github.com/Jannchie/tgit/commit/cf623c6)

### :adhesive_bandage: Fixes

- **changelog**: check whether the latest commit has a tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [310a306](https://github.com/Jannchie/tgit/commit/310a306)

### :memo: Documentation

- add readme - By [Jianqi Pan](mailto:jannchie@gmail.com) in [1b31cbf](https://github.com/Jannchie/tgit/commit/1b31cbf)

### :wrench: Chores

- **build**: use poetry - By [Jianqi Pan](mailto:jannchie@gmail.com) in [656de25](https://github.com/Jannchie/tgit/commit/656de25)
- **version**: clean the useless code - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0c24d69](https://github.com/Jannchie/tgit/commit/0c24d69)

## v0.3.0

[v0.2.2...v0.3.0](https://github.com/Jannchie/tgit/compare/v0.2.2...v0.3.0)

### :sparkles: Features

- **version**: update more version files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3a87374](https://github.com/Jannchie/tgit/commit/3a87374)
- add gitt as a alias - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bacd8fe](https://github.com/Jannchie/tgit/commit/bacd8fe)

### :wrench: Chores

- **commit**: do not show type choices because they are too long - By [Jianqi Pan](mailto:jannchie@gmail.com) in [886ed07](https://github.com/Jannchie/tgit/commit/886ed07)
- **scripts**: update build script - By [Jianqi Pan](mailto:jannchie@gmail.com) in [89702cd](https://github.com/Jannchie/tgit/commit/89702cd)

## v0.2.2

[v0.2.1...v0.2.2](https://github.com/Jannchie/tgit/compare/v0.2.1...v0.2.2)

### :adhesive_bandage: Fixes

- **commit**: add tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8ea1e80](https://github.com/Jannchie/tgit/commit/8ea1e80)

## v0.2.1

[0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1](https://github.com/Jannchie/tgit/compare/0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1)

### :sparkles: Features

- **commit**: enable emoji settings - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6acd0dc](https://github.com/Jannchie/tgit/commit/6acd0dc)
- **version**: detect version from file or git tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5b4d4aa](https://github.com/Jannchie/tgit/commit/5b4d4aa)

### :adhesive_bandage: Fixes

- **commit**: push tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [35c96a8](https://github.com/Jannchie/tgit/commit/35c96a8)

### :wrench: Chores

- **format**: use sourcery - By [Jianqi Pan](mailto:jannchie@gmail.com) in [03f2078](https://github.com/Jannchie/tgit/commit/03f2078)

## v1.1.0

[v0.17.1...v1.1.0](https://github.com/Jannchie/tgit/compare/v0.17.1...v1.1.0)

### :sparkles: Features

- **testing**: add comprehensive pytest test suite and tooling - By [Jannchie](mailto:panjianqi@preferred.jp) in [8cbdb4c](https://github.com/Jannchie/tgit/commit/8cbdb4c)

### :adhesive_bandage: Fixes

- **changelog**: handle commit messages type safety && improve changelog extraction - By [Jannchie](mailto:jannchie@gmail.com) in [c6ecbb5](https://github.com/Jannchie/tgit/commit/c6ecbb5)

### :art: Refactors

- **prompts**: replace inquirer with questionary and update user prompts - By [Jannchie](mailto:panjianqi@preferred.jp) in [e16b1a9](https://github.com/Jannchie/tgit/commit/e16b1a9)

## v0.17.1

[v0.17.0...v0.17.1](https://github.com/Jannchie/tgit/compare/v0.17.0...v0.17.1)

### :art: Refactors

- **ai**: modularize ai client creation and file filtering - By [Jannchie](mailto:jannchie@gmail.com) in [8071a1c](https://github.com/Jannchie/tgit/commit/8071a1c)

## v0.17.0

[v0.16.0...v0.17.0](https://github.com/Jannchie/tgit/compare/v0.16.0...v0.17.0)

### :sparkles: Features

- **changelog**: improve changelog output with panel ui - By [Jianqi Pan](mailto:jannchie@gmail.com) in [15237ca](https://github.com/Jannchie/tgit/commit/15237ca)
- **changelog**: add custom heading render and refactor changelog output - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca81836](https://github.com/Jannchie/tgit/commit/ca81836)

## v0.16.0

[v0.15.1...v0.16.0](https://github.com/Jannchie/tgit/compare/v0.15.1...v0.16.0)

### :sparkles: Features

- **version-changelog**: add interactive changelog generation on version bump - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2c6c3b3](https://github.com/Jannchie/tgit/commit/2c6c3b3)

### :adhesive_bandage: Fixes

- **changelog**: report no changes when changelog empty - By [Jianqi Pan](mailto:jannchie@gmail.com) in [02d94ff](https://github.com/Jannchie/tgit/commit/02d94ff)

### :art: Refactors

- **changelog**: simplify current tag handling in changelog - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ac7903](https://github.com/Jannchie/tgit/commit/6ac7903)

## v0.15.1

[v0.15.0...v0.15.1](https://github.com/Jannchie/tgit/compare/v0.15.0...v0.15.1)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4ab3b1e](https://github.com/Jannchie/tgit/commit/4ab3b1e)

## v0.15.0

[v0.14.2...v0.15.0](https://github.com/Jannchie/tgit/compare/v0.14.2...v0.15.0)

### :sparkles: Features

- **prompts**: revise commit message instructions for clarity - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b58f9ec](https://github.com/Jannchie/tgit/commit/b58f9ec)

## v0.14.2

[v0.14.1...v0.14.2](https://github.com/Jannchie/tgit/compare/v0.14.1...v0.14.2)

### :adhesive_bandage: Fixes

- **version**: fix bump logic for v0 breaking changes to minor - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0f14045](https://github.com/Jannchie/tgit/commit/0f14045)

### :art: Refactors

- **changelog**: extract changelog segment, write helpers && simplify handle logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ebc1e17](https://github.com/Jannchie/tgit/commit/ebc1e17)

### :lipstick: Styles

- **changelog**: add extra newline before old changelog content && remove noqa for rich print import - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca93aaf](https://github.com/Jannchie/tgit/commit/ca93aaf)

### :memo: Documentation

- **changelog**: update changelog for v0.14.0 and v0.14.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3d26e26](https://github.com/Jannchie/tgit/commit/3d26e26)

## v0.14.1

[v0.14.0...v0.14.1](https://github.com/Jannchie/tgit/compare/v0.14.0...v0.14.1)

### :adhesive_bandage: Fixes

- **changelog**: prepend new changelog entries if file exists - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c4b3dff](https://github.com/Jannchie/tgit/commit/c4b3dff)

## v0.14.0

[v0.13.2...v0.14.0](https://github.com/Jannchie/tgit/compare/v0.13.2...v0.14.0)

### :sparkles: Features

- **changelog**: add incremental changelog generation && support appending to existing file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2d193a5](https://github.com/Jannchie/tgit/commit/2d193a5)

### :adhesive_bandage: Fixes

- **changelog**: remove head from default changelog range && update changelog entries - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f6509e3](https://github.com/Jannchie/tgit/commit/f6509e3)

## v0.13.2

[v0.13.1...v0.13.2](https://github.com/Jannchie/tgit/compare/v0.13.1...v0.13.2)

### :adhesive_bandage: Fixes

- **cli**: suppress import error for openai in thread - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4973127](https://github.com/Jannchie/tgit/commit/4973127)

## v0.13.1

[v0.13.0...v0.13.1](https://github.com/Jannchie/tgit/compare/v0.13.0...v0.13.1)

### :adhesive_bandage: Fixes

- **commit**: update no-files message for ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cda3740](https://github.com/Jannchie/tgit/commit/cda3740)

### :wrench: Chores

- **ci**: update build workflow to release only on tag push && replace artifact upload with github release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7548485](https://github.com/Jannchie/tgit/commit/7548485)
- **code-cleanup**: remove unnecessary noqa for print && update changelog and ruff ignore list - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdf5665](https://github.com/Jannchie/tgit/commit/bdf5665)

## v0.13.0

[v0.12.0...v0.13.0](https://github.com/Jannchie/tgit/compare/v0.12.0...v0.13.0)

### :sparkles: Features

- **changelog**: add progress bar and improve tag changelog aggregation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e98fba4](https://github.com/Jannchie/tgit/commit/e98fba4)
- **commit**: filter large diffs and lock files from ai commit msg input && switch from litellm to openai - By [Jianqi Pan](mailto:jannchie@gmail.com) in [587c4d1](https://github.com/Jannchie/tgit/commit/587c4d1)

### :memo: Documentation

- **changelog**: update changelog for v0.13.0 release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e61e8bb](https://github.com/Jannchie/tgit/commit/e61e8bb)

### :wrench: Chores

- **ci**: trigger on tag && simplify commands && upload artifacts only for tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee952df](https://github.com/Jannchie/tgit/commit/ee952df)
- **ci**: add github actions workflow for building python package with uv - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7450f78](https://github.com/Jannchie/tgit/commit/7450f78)

## v0.12.0

[v0.11.2...v0.12.0](https://github.com/Jannchie/tgit/compare/v0.11.2...v0.12.0)

### :sparkles: Features

- **commit**: add console status during ai command generation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [779d2da](https://github.com/Jannchie/tgit/commit/779d2da)
- **commit**: add support for user-specified commit type in get_ai_command && update get_ai_command to handle default commit types - By [Jianqi Pan](mailto:jannchie@gmail.com) in [88f6980](https://github.com/Jannchie/tgit/commit/88f6980)
- **commit**: add branch name to AI commit prompt && update dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [016facc](https://github.com/Jannchie/tgit/commit/016facc)

## v0.11.2

[v0.11.0...v0.11.2](https://github.com/Jannchie/tgit/compare/v0.11.0...v0.11.2)

### :adhesive_bandage: Fixes

- **versioning**: correct cargo.toml regex for version update && update litellm package to 1.64.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdb69c5](https://github.com/Jannchie/tgit/commit/bdb69c5)

### :wrench: Chores

- **dependencies**: update package versions && add beautifulsoup4 dependency && update comments for sys_platform checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c9d14a](https://github.com/Jannchie/tgit/commit/4c9d14a)

## v0.11.0

[v0.10.2...v0.11.0](https://github.com/Jannchie/tgit/compare/v0.10.2...v0.11.0)

### :sparkles: Features

- **cli**: add config command && update dependencies - By [Jannchie](mailto:panjianqi@preferred.jp) in [32d0ecc](https://github.com/Jannchie/tgit/commit/32d0ecc)
- **config, dependencies, commit**: Add configuration command and update dependency versions and AI provider - By [Jannchie](mailto:panjianqi@preferred.jp) in [e446030](https://github.com/Jannchie/tgit/commit/e446030)

### :art: Refactors

- **utils**: update function signature for get_commit_command - By [Jannchie](mailto:panjianqi@preferred.jp) in [4c67c0a](https://github.com/Jannchie/tgit/commit/4c67c0a)

### :memo: Documentation

- **commit**: update commit prompt with class definition - By [Jannchie](mailto:panjianqi@preferred.jp) in [2f5a464](https://github.com/Jannchie/tgit/commit/2f5a464)

### :wrench: Chores

- **dependencies**: add ruff to dev dependencies && update type hints and function signatures - By [Jannchie](mailto:panjianqi@preferred.jp) in [e137b4f](https://github.com/Jannchie/tgit/commit/e137b4f)
- **lock**: update lock file - By [Jannchie](mailto:panjianqi@preferred.jp) in [c4330c5](https://github.com/Jannchie/tgit/commit/c4330c5)

## v0.10.2

[v0.10.1...v0.10.2](https://github.com/Jannchie/tgit/compare/v0.10.1...v0.10.2)

### :adhesive_bandage: Fixes

- **template-rendering**: correct types rendering in commit prompt - By [Jianqi Pan](mailto:jannchie@gmail.com) in [542db82](https://github.com/Jannchie/tgit/commit/542db82)

### :art: Refactors

- **commit-command**: improve function signatures && handle keyword args - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f3bc59](https://github.com/Jannchie/tgit/commit/8f3bc59)

## v0.10.1

[v0.10.0...v0.10.1](https://github.com/Jannchie/tgit/compare/v0.10.0...v0.10.1)

### :adhesive_bandage: Fixes

- **file-open**: open pyproject.toml and Cargo.toml in binary mode - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5ba059a](https://github.com/Jannchie/tgit/commit/5ba059a)

### :art: Refactors

- **project**: revise configuration files && update package dependencies && enhance type annotations - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ff2ecc](https://github.com/Jannchie/tgit/commit/6ff2ecc)
- **version**: modularize version retrieval && extract diff formatting - By [Jianqi Pan](mailto:jannchie@gmail.com) in [9832dfc](https://github.com/Jannchie/tgit/commit/9832dfc)

## v0.10.0

[v0.9.0...v0.10.0](https://github.com/Jannchie/tgit/compare/v0.9.0...v0.10.0)

### :sparkles: Features

- **version**: add support for updating build.gradle.kts version - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c66e792](https://github.com/Jannchie/tgit/commit/c66e792)
- **version**: add custom path support for version handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c79f46](https://github.com/Jannchie/tgit/commit/4c79f46)

## v0.9.0

[v0.8.1...v0.9.0](https://github.com/Jannchie/tgit/compare/v0.8.1...v0.9.0)

### :sparkles: Features

- **add**: implement add command to wrap git add - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e372314](https://github.com/Jannchie/tgit/commit/e372314)
- **version**: add recursive option for version bumping - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c98bf05](https://github.com/Jannchie/tgit/commit/c98bf05)

### :wrench: Chores

- **deps**: update python version and dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3c49d1a](https://github.com/Jannchie/tgit/commit/3c49d1a)

## v0.8.1

[v0.8.0...v0.8.1](https://github.com/Jannchie/tgit/compare/v0.8.0...v0.8.1)

### :lipstick: Styles

- **commit**: update commit message instructions && change import style - By [Jianqi Pan](mailto:jannchie@gmail.com) in [538f27d](https://github.com/Jannchie/tgit/commit/538f27d)

## v0.8.0

[v0.7.1...v0.8.0](https://github.com/Jannchie/tgit/compare/v0.7.1...v0.8.0)

### :sparkles: Features

- **commit**: add 'wip' to commit types and correct invalid type error message - By [Jianqi Pan](mailto:jannchie@gmail.com) in [be64b23](https://github.com/Jannchie/tgit/commit/be64b23)

### :memo: Documentation

- **commit**: clarify role description by specifying message should cover all changes in diff - By [Jianqi Pan](mailto:jannchie@gmail.com) in [486cb2c](https://github.com/Jannchie/tgit/commit/486cb2c)

### :wrench: Chores

- **dependencies**: update dependencies versions in pyproject.toml and lock files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51142a2](https://github.com/Jannchie/tgit/commit/51142a2)
- update readme configuration to include content-type in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [122be13](https://github.com/Jannchie/tgit/commit/122be13)

## v0.7.1

[v0.7.0...v0.7.1](https://github.com/Jannchie/tgit/compare/v0.7.0...v0.7.1)

### :adhesive_bandage: Fixes

- **authentication**: handle openai authentication error - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e2e0e53](https://github.com/Jannchie/tgit/commit/e2e0e53)
- handle invalid git repository error when getting ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c8c4a54](https://github.com/Jannchie/tgit/commit/c8c4a54)

### :wrench: Chores

- update lock files with new dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [537c627](https://github.com/Jannchie/tgit/commit/537c627)

## v0.7.0

[v0.6.1...v0.7.0](https://github.com/Jannchie/tgit/compare/v0.6.1...v0.7.0)

### :sparkles: Features

- **changelog**: add ability to output changelog to a file - By [Jannchie](mailto:panjianqi@preferred.jp) in [b1a52e1](https://github.com/Jannchie/tgit/commit/b1a52e1)

## v0.6.1

[v0.6.0...v0.6.1](https://github.com/Jannchie/tgit/compare/v0.6.0...v0.6.1)

### :adhesive_bandage: Fixes

- **changelog**: simplify sort by scope logic and validate diff before AI command - By [Jannchie](mailto:panjianqi@preferred.jp) in [32dd4e3](https://github.com/Jannchie/tgit/commit/32dd4e3)

### :wrench: Chores

- update gitignore, vscode settings, and pyproject.toml - By [Jannchie](mailto:panjianqi@preferred.jp) in [103271e](https://github.com/Jannchie/tgit/commit/103271e)

## v0.6.0

[v0.5.2...v0.6.0](https://github.com/Jannchie/tgit/compare/v0.5.2...v0.6.0)

### :sparkles: Features

- **version**: introduce auto-detection of version bump based on commit types - By [Jannchie](mailto:panjianqi@preferred.jp) in [910107f](https://github.com/Jannchie/tgit/commit/910107f)

### :art: Refactors

- extract git commit range logic into separate function for better readability - By [Jannchie](mailto:panjianqi@preferred.jp) in [44f9c94](https://github.com/Jannchie/tgit/commit/44f9c94)

## v0.5.2

[v0.5.1...v0.5.2](https://github.com/Jannchie/tgit/compare/v0.5.1...v0.5.2)

### :adhesive_bandage: Fixes

- **commit**: correct commit message formatting and emoji usage - By [Jannchie](mailto:panjianqi@preferred.jp) in [34b58a9](https://github.com/Jannchie/tgit/commit/34b58a9)

## v0.5.1

[v0.5.0...v0.5.1](https://github.com/Jannchie/tgit/compare/v0.5.0...v0.5.1)

### :sparkles: Features

- **commit**: add rich print for missing commit message - By [Jannchie](mailto:panjianqi@preferred.jp) in [686cf4a](https://github.com/Jannchie/tgit/commit/686cf4a)

## v0.5.0

[v0.4.3...v0.5.0](https://github.com/Jannchie/tgit/compare/v0.4.3...v0.5.0)

### :sparkles: Features

- **tgit**: add ai-powered commit message suggestion using openai - By [Jannchie](mailto:panjianqi@preferred.jp) in [93299f1](https://github.com/Jannchie/tgit/commit/93299f1)

## v0.4.3

[v0.4.2...v0.4.3](https://github.com/Jannchie/tgit/compare/v0.4.2...v0.4.3)

### :art: Refactors

- **version**: make the code clearer - By [Jianqi Pan](mailto:jannchie@gmail.com) in [68d626e](https://github.com/Jannchie/tgit/commit/68d626e)

### :memo: Documentation

- add codetime badge - By [Jianqi Pan](mailto:jannchie@gmail.com) in [984b9d3](https://github.com/Jannchie/tgit/commit/984b9d3)

## v0.4.2

[v0.4.1...v0.4.2](https://github.com/Jannchie/tgit/compare/v0.4.1...v0.4.2)

### :adhesive_bandage: Fixes

- **depeendencies**: need python 3.11 because of tomllib - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d7b3c0a](https://github.com/Jannchie/tgit/commit/d7b3c0a)

## v0.4.1

[v0.4.0...v0.4.1](https://github.com/Jannchie/tgit/compare/v0.4.0...v0.4.1)

### :adhesive_bandage: Fixes

- **depeendencies**: add gitpython as dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51bbcb1](https://github.com/Jannchie/tgit/commit/51bbcb1)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/tgit/compare/v0.3.0...v0.4.0)

### :sparkles: Features

- **changelog**: implement basic changelog features - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cf623c6](https://github.com/Jannchie/tgit/commit/cf623c6)

### :adhesive_bandage: Fixes

- **changelog**: check whether the latest commit has a tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [310a306](https://github.com/Jannchie/tgit/commit/310a306)

### :memo: Documentation

- add readme - By [Jianqi Pan](mailto:jannchie@gmail.com) in [1b31cbf](https://github.com/Jannchie/tgit/commit/1b31cbf)

### :wrench: Chores

- **build**: use poetry - By [Jianqi Pan](mailto:jannchie@gmail.com) in [656de25](https://github.com/Jannchie/tgit/commit/656de25)
- **version**: clean the useless code - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0c24d69](https://github.com/Jannchie/tgit/commit/0c24d69)

## v0.3.0

[v0.2.2...v0.3.0](https://github.com/Jannchie/tgit/compare/v0.2.2...v0.3.0)

### :sparkles: Features

- **version**: update more version files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3a87374](https://github.com/Jannchie/tgit/commit/3a87374)
- add gitt as a alias - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bacd8fe](https://github.com/Jannchie/tgit/commit/bacd8fe)

### :wrench: Chores

- **commit**: do not show type choices because they are too long - By [Jianqi Pan](mailto:jannchie@gmail.com) in [886ed07](https://github.com/Jannchie/tgit/commit/886ed07)
- **scripts**: update build script - By [Jianqi Pan](mailto:jannchie@gmail.com) in [89702cd](https://github.com/Jannchie/tgit/commit/89702cd)

## v0.2.2

[v0.2.1...v0.2.2](https://github.com/Jannchie/tgit/compare/v0.2.1...v0.2.2)

### :adhesive_bandage: Fixes

- **commit**: add tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8ea1e80](https://github.com/Jannchie/tgit/commit/8ea1e80)

## v0.2.1

[0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1](https://github.com/Jannchie/tgit/compare/0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1)

### :sparkles: Features

- **commit**: enable emoji settings - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6acd0dc](https://github.com/Jannchie/tgit/commit/6acd0dc)
- **version**: detect version from file or git tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5b4d4aa](https://github.com/Jannchie/tgit/commit/5b4d4aa)

### :adhesive_bandage: Fixes

- **commit**: push tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [35c96a8](https://github.com/Jannchie/tgit/commit/35c96a8)

### :wrench: Chores

- **format**: use sourcery - By [Jianqi Pan](mailto:jannchie@gmail.com) in [03f2078](https://github.com/Jannchie/tgit/commit/03f2078)

## v1.1.0

[v0.17.1...v1.1.0](https://github.com/Jannchie/tgit/compare/v0.17.1...v1.1.0)

### :sparkles: Features

- **testing**: add comprehensive pytest test suite and tooling - By [Jannchie](mailto:panjianqi@preferred.jp) in [8cbdb4c](https://github.com/Jannchie/tgit/commit/8cbdb4c)

### :adhesive_bandage: Fixes

- **changelog**: handle commit messages type safety && improve changelog extraction - By [Jannchie](mailto:jannchie@gmail.com) in [c6ecbb5](https://github.com/Jannchie/tgit/commit/c6ecbb5)

### :art: Refactors

- **prompts**: replace inquirer with questionary and update user prompts - By [Jannchie](mailto:panjianqi@preferred.jp) in [e16b1a9](https://github.com/Jannchie/tgit/commit/e16b1a9)

## v0.17.1

[v0.17.0...v0.17.1](https://github.com/Jannchie/tgit/compare/v0.17.0...v0.17.1)

### :art: Refactors

- **ai**: modularize ai client creation and file filtering - By [Jannchie](mailto:jannchie@gmail.com) in [8071a1c](https://github.com/Jannchie/tgit/commit/8071a1c)

## v0.17.0

[v0.16.0...v0.17.0](https://github.com/Jannchie/tgit/compare/v0.16.0...v0.17.0)

### :sparkles: Features

- **changelog**: improve changelog output with panel ui - By [Jianqi Pan](mailto:jannchie@gmail.com) in [15237ca](https://github.com/Jannchie/tgit/commit/15237ca)
- **changelog**: add custom heading render and refactor changelog output - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca81836](https://github.com/Jannchie/tgit/commit/ca81836)

## v0.16.0

[v0.15.1...v0.16.0](https://github.com/Jannchie/tgit/compare/v0.15.1...v0.16.0)

### :sparkles: Features

- **version-changelog**: add interactive changelog generation on version bump - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2c6c3b3](https://github.com/Jannchie/tgit/commit/2c6c3b3)

### :adhesive_bandage: Fixes

- **changelog**: report no changes when changelog empty - By [Jianqi Pan](mailto:jannchie@gmail.com) in [02d94ff](https://github.com/Jannchie/tgit/commit/02d94ff)

### :art: Refactors

- **changelog**: simplify current tag handling in changelog - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ac7903](https://github.com/Jannchie/tgit/commit/6ac7903)

## v0.15.1

[v0.15.0...v0.15.1](https://github.com/Jannchie/tgit/compare/v0.15.0...v0.15.1)

### :wrench: Chores

- **deps**: update lock file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4ab3b1e](https://github.com/Jannchie/tgit/commit/4ab3b1e)

## v0.15.0

[v0.14.2...v0.15.0](https://github.com/Jannchie/tgit/compare/v0.14.2...v0.15.0)

### :sparkles: Features

- **prompts**: revise commit message instructions for clarity - By [Jianqi Pan](mailto:jannchie@gmail.com) in [b58f9ec](https://github.com/Jannchie/tgit/commit/b58f9ec)

## v0.14.2

[v0.14.1...v0.14.2](https://github.com/Jannchie/tgit/compare/v0.14.1...v0.14.2)

### :adhesive_bandage: Fixes

- **version**: fix bump logic for v0 breaking changes to minor - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0f14045](https://github.com/Jannchie/tgit/commit/0f14045)

### :art: Refactors

- **changelog**: extract changelog segment, write helpers && simplify handle logic - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ebc1e17](https://github.com/Jannchie/tgit/commit/ebc1e17)

### :lipstick: Styles

- **changelog**: add extra newline before old changelog content && remove noqa for rich print import - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ca93aaf](https://github.com/Jannchie/tgit/commit/ca93aaf)

### :memo: Documentation

- **changelog**: update changelog for v0.14.0 and v0.14.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3d26e26](https://github.com/Jannchie/tgit/commit/3d26e26)

## v0.14.1

[v0.14.0...v0.14.1](https://github.com/Jannchie/tgit/compare/v0.14.0...v0.14.1)

### :adhesive_bandage: Fixes

- **changelog**: prepend new changelog entries if file exists - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c4b3dff](https://github.com/Jannchie/tgit/commit/c4b3dff)

## v0.14.0

[v0.13.2...v0.14.0](https://github.com/Jannchie/tgit/compare/v0.13.2...v0.14.0)

### :sparkles: Features

- **changelog**: add incremental changelog generation && support appending to existing file - By [Jianqi Pan](mailto:jannchie@gmail.com) in [2d193a5](https://github.com/Jannchie/tgit/commit/2d193a5)

### :adhesive_bandage: Fixes

- **changelog**: remove head from default changelog range && update changelog entries - By [Jianqi Pan](mailto:jannchie@gmail.com) in [f6509e3](https://github.com/Jannchie/tgit/commit/f6509e3)

## v0.13.2

[v0.13.1...v0.13.2](https://github.com/Jannchie/tgit/compare/v0.13.1...v0.13.2)

### :adhesive_bandage: Fixes

- **cli**: suppress import error for openai in thread - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4973127](https://github.com/Jannchie/tgit/commit/4973127)

## v0.13.1

[v0.13.0...v0.13.1](https://github.com/Jannchie/tgit/compare/v0.13.0...v0.13.1)

### :adhesive_bandage: Fixes

- **commit**: update no-files message for ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cda3740](https://github.com/Jannchie/tgit/commit/cda3740)

### :wrench: Chores

- **ci**: update build workflow to release only on tag push && replace artifact upload with github release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7548485](https://github.com/Jannchie/tgit/commit/7548485)
- **code-cleanup**: remove unnecessary noqa for print && update changelog and ruff ignore list - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdf5665](https://github.com/Jannchie/tgit/commit/bdf5665)

## v0.13.0

[v0.12.0...v0.13.0](https://github.com/Jannchie/tgit/compare/v0.12.0...v0.13.0)

### :sparkles: Features

- **changelog**: add progress bar and improve tag changelog aggregation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e98fba4](https://github.com/Jannchie/tgit/commit/e98fba4)
- **commit**: filter large diffs and lock files from ai commit msg input && switch from litellm to openai - By [Jianqi Pan](mailto:jannchie@gmail.com) in [587c4d1](https://github.com/Jannchie/tgit/commit/587c4d1)

### :memo: Documentation

- **changelog**: update changelog for v0.13.0 release - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e61e8bb](https://github.com/Jannchie/tgit/commit/e61e8bb)

### :wrench: Chores

- **ci**: trigger on tag && simplify commands && upload artifacts only for tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [ee952df](https://github.com/Jannchie/tgit/commit/ee952df)
- **ci**: add github actions workflow for building python package with uv - By [Jianqi Pan](mailto:jannchie@gmail.com) in [7450f78](https://github.com/Jannchie/tgit/commit/7450f78)

## v0.12.0

[v0.11.2...v0.12.0](https://github.com/Jannchie/tgit/compare/v0.11.2...v0.12.0)

### :sparkles: Features

- **commit**: add console status during ai command generation - By [Jianqi Pan](mailto:jannchie@gmail.com) in [779d2da](https://github.com/Jannchie/tgit/commit/779d2da)
- **commit**: add support for user-specified commit type in get_ai_command && update get_ai_command to handle default commit types - By [Jianqi Pan](mailto:jannchie@gmail.com) in [88f6980](https://github.com/Jannchie/tgit/commit/88f6980)
- **commit**: add branch name to AI commit prompt && update dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [016facc](https://github.com/Jannchie/tgit/commit/016facc)

## v0.11.2

[v0.11.0...v0.11.2](https://github.com/Jannchie/tgit/compare/v0.11.0...v0.11.2)

### :adhesive_bandage: Fixes

- **versioning**: correct cargo.toml regex for version update && update litellm package to 1.64.1 - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bdb69c5](https://github.com/Jannchie/tgit/commit/bdb69c5)

### :wrench: Chores

- **dependencies**: update package versions && add beautifulsoup4 dependency && update comments for sys_platform checks - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c9d14a](https://github.com/Jannchie/tgit/commit/4c9d14a)

## v0.11.0

[v0.10.2...v0.11.0](https://github.com/Jannchie/tgit/compare/v0.10.2...v0.11.0)

### :sparkles: Features

- **cli**: add config command && update dependencies - By [Jannchie](mailto:panjianqi@preferred.jp) in [32d0ecc](https://github.com/Jannchie/tgit/commit/32d0ecc)
- **config, dependencies, commit**: Add configuration command and update dependency versions and AI provider - By [Jannchie](mailto:panjianqi@preferred.jp) in [e446030](https://github.com/Jannchie/tgit/commit/e446030)

### :art: Refactors

- **utils**: update function signature for get_commit_command - By [Jannchie](mailto:panjianqi@preferred.jp) in [4c67c0a](https://github.com/Jannchie/tgit/commit/4c67c0a)

### :memo: Documentation

- **commit**: update commit prompt with class definition - By [Jannchie](mailto:panjianqi@preferred.jp) in [2f5a464](https://github.com/Jannchie/tgit/commit/2f5a464)

### :wrench: Chores

- **dependencies**: add ruff to dev dependencies && update type hints and function signatures - By [Jannchie](mailto:panjianqi@preferred.jp) in [e137b4f](https://github.com/Jannchie/tgit/commit/e137b4f)
- **lock**: update lock file - By [Jannchie](mailto:panjianqi@preferred.jp) in [c4330c5](https://github.com/Jannchie/tgit/commit/c4330c5)

## v0.10.2

[v0.10.1...v0.10.2](https://github.com/Jannchie/tgit/compare/v0.10.1...v0.10.2)

### :adhesive_bandage: Fixes

- **template-rendering**: correct types rendering in commit prompt - By [Jianqi Pan](mailto:jannchie@gmail.com) in [542db82](https://github.com/Jannchie/tgit/commit/542db82)

### :art: Refactors

- **commit-command**: improve function signatures && handle keyword args - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8f3bc59](https://github.com/Jannchie/tgit/commit/8f3bc59)

## v0.10.1

[v0.10.0...v0.10.1](https://github.com/Jannchie/tgit/compare/v0.10.0...v0.10.1)

### :adhesive_bandage: Fixes

- **file-open**: open pyproject.toml and Cargo.toml in binary mode - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5ba059a](https://github.com/Jannchie/tgit/commit/5ba059a)

### :art: Refactors

- **project**: revise configuration files && update package dependencies && enhance type annotations - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6ff2ecc](https://github.com/Jannchie/tgit/commit/6ff2ecc)
- **version**: modularize version retrieval && extract diff formatting - By [Jianqi Pan](mailto:jannchie@gmail.com) in [9832dfc](https://github.com/Jannchie/tgit/commit/9832dfc)

## v0.10.0

[v0.9.0...v0.10.0](https://github.com/Jannchie/tgit/compare/v0.9.0...v0.10.0)

### :sparkles: Features

- **version**: add support for updating build.gradle.kts version - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c66e792](https://github.com/Jannchie/tgit/commit/c66e792)
- **version**: add custom path support for version handling - By [Jianqi Pan](mailto:jannchie@gmail.com) in [4c79f46](https://github.com/Jannchie/tgit/commit/4c79f46)

## v0.9.0

[v0.8.1...v0.9.0](https://github.com/Jannchie/tgit/compare/v0.8.1...v0.9.0)

### :sparkles: Features

- **add**: implement add command to wrap git add - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e372314](https://github.com/Jannchie/tgit/commit/e372314)
- **version**: add recursive option for version bumping - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c98bf05](https://github.com/Jannchie/tgit/commit/c98bf05)

### :wrench: Chores

- **deps**: update python version and dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3c49d1a](https://github.com/Jannchie/tgit/commit/3c49d1a)

## v0.8.1

[v0.8.0...v0.8.1](https://github.com/Jannchie/tgit/compare/v0.8.0...v0.8.1)

### :lipstick: Styles

- **commit**: update commit message instructions && change import style - By [Jianqi Pan](mailto:jannchie@gmail.com) in [538f27d](https://github.com/Jannchie/tgit/commit/538f27d)

## v0.8.0

[v0.7.1...v0.8.0](https://github.com/Jannchie/tgit/compare/v0.7.1...v0.8.0)

### :sparkles: Features

- **commit**: add 'wip' to commit types and correct invalid type error message - By [Jianqi Pan](mailto:jannchie@gmail.com) in [be64b23](https://github.com/Jannchie/tgit/commit/be64b23)

### :memo: Documentation

- **commit**: clarify role description by specifying message should cover all changes in diff - By [Jianqi Pan](mailto:jannchie@gmail.com) in [486cb2c](https://github.com/Jannchie/tgit/commit/486cb2c)

### :wrench: Chores

- **dependencies**: update dependencies versions in pyproject.toml and lock files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51142a2](https://github.com/Jannchie/tgit/commit/51142a2)
- update readme configuration to include content-type in pyproject.toml - By [Jianqi Pan](mailto:jannchie@gmail.com) in [122be13](https://github.com/Jannchie/tgit/commit/122be13)

## v0.7.1

[v0.7.0...v0.7.1](https://github.com/Jannchie/tgit/compare/v0.7.0...v0.7.1)

### :adhesive_bandage: Fixes

- **authentication**: handle openai authentication error - By [Jianqi Pan](mailto:jannchie@gmail.com) in [e2e0e53](https://github.com/Jannchie/tgit/commit/e2e0e53)
- handle invalid git repository error when getting ai command - By [Jianqi Pan](mailto:jannchie@gmail.com) in [c8c4a54](https://github.com/Jannchie/tgit/commit/c8c4a54)

### :wrench: Chores

- update lock files with new dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [537c627](https://github.com/Jannchie/tgit/commit/537c627)

## v0.7.0

[v0.6.1...v0.7.0](https://github.com/Jannchie/tgit/compare/v0.6.1...v0.7.0)

### :sparkles: Features

- **changelog**: add ability to output changelog to a file - By [Jannchie](mailto:panjianqi@preferred.jp) in [b1a52e1](https://github.com/Jannchie/tgit/commit/b1a52e1)

## v0.6.1

[v0.6.0...v0.6.1](https://github.com/Jannchie/tgit/compare/v0.6.0...v0.6.1)

### :adhesive_bandage: Fixes

- **changelog**: simplify sort by scope logic and validate diff before AI command - By [Jannchie](mailto:panjianqi@preferred.jp) in [32dd4e3](https://github.com/Jannchie/tgit/commit/32dd4e3)

### :wrench: Chores

- update gitignore, vscode settings, and pyproject.toml - By [Jannchie](mailto:panjianqi@preferred.jp) in [103271e](https://github.com/Jannchie/tgit/commit/103271e)

## v0.6.0

[v0.5.2...v0.6.0](https://github.com/Jannchie/tgit/compare/v0.5.2...v0.6.0)

### :sparkles: Features

- **version**: introduce auto-detection of version bump based on commit types - By [Jannchie](mailto:panjianqi@preferred.jp) in [910107f](https://github.com/Jannchie/tgit/commit/910107f)

### :art: Refactors

- extract git commit range logic into separate function for better readability - By [Jannchie](mailto:panjianqi@preferred.jp) in [44f9c94](https://github.com/Jannchie/tgit/commit/44f9c94)

## v0.5.2

[v0.5.1...v0.5.2](https://github.com/Jannchie/tgit/compare/v0.5.1...v0.5.2)

### :adhesive_bandage: Fixes

- **commit**: correct commit message formatting and emoji usage - By [Jannchie](mailto:panjianqi@preferred.jp) in [34b58a9](https://github.com/Jannchie/tgit/commit/34b58a9)

## v0.5.1

[v0.5.0...v0.5.1](https://github.com/Jannchie/tgit/compare/v0.5.0...v0.5.1)

### :sparkles: Features

- **commit**: add rich print for missing commit message - By [Jannchie](mailto:panjianqi@preferred.jp) in [686cf4a](https://github.com/Jannchie/tgit/commit/686cf4a)

## v0.5.0

[v0.4.3...v0.5.0](https://github.com/Jannchie/tgit/compare/v0.4.3...v0.5.0)

### :sparkles: Features

- **tgit**: add ai-powered commit message suggestion using openai - By [Jannchie](mailto:panjianqi@preferred.jp) in [93299f1](https://github.com/Jannchie/tgit/commit/93299f1)

## v0.4.3

[v0.4.2...v0.4.3](https://github.com/Jannchie/tgit/compare/v0.4.2...v0.4.3)

### :art: Refactors

- **version**: make the code clearer - By [Jianqi Pan](mailto:jannchie@gmail.com) in [68d626e](https://github.com/Jannchie/tgit/commit/68d626e)

### :memo: Documentation

- add codetime badge - By [Jianqi Pan](mailto:jannchie@gmail.com) in [984b9d3](https://github.com/Jannchie/tgit/commit/984b9d3)

## v0.4.2

[v0.4.1...v0.4.2](https://github.com/Jannchie/tgit/compare/v0.4.1...v0.4.2)

### :adhesive_bandage: Fixes

- **depeendencies**: need python 3.11 because of tomllib - By [Jianqi Pan](mailto:jannchie@gmail.com) in [d7b3c0a](https://github.com/Jannchie/tgit/commit/d7b3c0a)

## v0.4.1

[v0.4.0...v0.4.1](https://github.com/Jannchie/tgit/compare/v0.4.0...v0.4.1)

### :adhesive_bandage: Fixes

- **depeendencies**: add gitpython as dependencies - By [Jianqi Pan](mailto:jannchie@gmail.com) in [51bbcb1](https://github.com/Jannchie/tgit/commit/51bbcb1)

## v0.4.0

[v0.3.0...v0.4.0](https://github.com/Jannchie/tgit/compare/v0.3.0...v0.4.0)

### :sparkles: Features

- **changelog**: implement basic changelog features - By [Jianqi Pan](mailto:jannchie@gmail.com) in [cf623c6](https://github.com/Jannchie/tgit/commit/cf623c6)

### :adhesive_bandage: Fixes

- **changelog**: check whether the latest commit has a tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [310a306](https://github.com/Jannchie/tgit/commit/310a306)

### :memo: Documentation

- add readme - By [Jianqi Pan](mailto:jannchie@gmail.com) in [1b31cbf](https://github.com/Jannchie/tgit/commit/1b31cbf)

### :wrench: Chores

- **build**: use poetry - By [Jianqi Pan](mailto:jannchie@gmail.com) in [656de25](https://github.com/Jannchie/tgit/commit/656de25)
- **version**: clean the useless code - By [Jianqi Pan](mailto:jannchie@gmail.com) in [0c24d69](https://github.com/Jannchie/tgit/commit/0c24d69)

## v0.3.0

[v0.2.2...v0.3.0](https://github.com/Jannchie/tgit/compare/v0.2.2...v0.3.0)

### :sparkles: Features

- **version**: update more version files - By [Jianqi Pan](mailto:jannchie@gmail.com) in [3a87374](https://github.com/Jannchie/tgit/commit/3a87374)
- add gitt as a alias - By [Jianqi Pan](mailto:jannchie@gmail.com) in [bacd8fe](https://github.com/Jannchie/tgit/commit/bacd8fe)

### :wrench: Chores

- **commit**: do not show type choices because they are too long - By [Jianqi Pan](mailto:jannchie@gmail.com) in [886ed07](https://github.com/Jannchie/tgit/commit/886ed07)
- **scripts**: update build script - By [Jianqi Pan](mailto:jannchie@gmail.com) in [89702cd](https://github.com/Jannchie/tgit/commit/89702cd)

## v0.2.2

[v0.2.1...v0.2.2](https://github.com/Jannchie/tgit/compare/v0.2.1...v0.2.2)

### :adhesive_bandage: Fixes

- **commit**: add tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [8ea1e80](https://github.com/Jannchie/tgit/commit/8ea1e80)

## v0.2.1

[0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1](https://github.com/Jannchie/tgit/compare/0c6d5b32aad9f01678b114120e7530dfebf4fb85...v0.2.1)

### :sparkles: Features

- **commit**: enable emoji settings - By [Jianqi Pan](mailto:jannchie@gmail.com) in [6acd0dc](https://github.com/Jannchie/tgit/commit/6acd0dc)
- **version**: detect version from file or git tags - By [Jianqi Pan](mailto:jannchie@gmail.com) in [5b4d4aa](https://github.com/Jannchie/tgit/commit/5b4d4aa)

### :adhesive_bandage: Fixes

- **commit**: push tag - By [Jianqi Pan](mailto:jannchie@gmail.com) in [35c96a8](https://github.com/Jannchie/tgit/commit/35c96a8)

### :wrench: Chores

- **format**: use sourcery - By [Jianqi Pan](mailto:jannchie@gmail.com) in [03f2078](https://github.com/Jannchie/tgit/commit/03f2078)
