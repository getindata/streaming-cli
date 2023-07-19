# Changelog

## [Unreleased]

## [2.0.0] - 2023-05-30

## [1.11.1] - 2023-05-19

## [1.11.0] - 2023-05-19

### Added

-   New `flink_execute_sql_set` magic processing - create a statement set with inserts

## [1.10.2] - 2023-03-28

### Added

-   Separate CI job for docker creation

## [1.10.1] - 2023-03-27

### Fixed

-   Properly handle http response status

## [1.10.0] - 2023-03-21

### Added

-   Deploy to vvp with given deployment descriptor
-   Documentation on adding certificates needed by requests library

### Changed

-   Ververica job deployment now uses PUT http method instead of POST

## [1.9.1] - 2023-03-02

### Added

-   Create and publish docker image

## [1.9.0] - 2023-02-28

### Added

-   Handle `%%flink_execute`

### Fixed

-   Don't add shell commands to the converted notebooks

## [1.8.1] - 2023-02-02

### Fixed

-   Deploy - develop mode

## [1.8.0] - 2023-01-20

### Added

-   Convert CMD

### Fixed

-   Repository template protocol ssh -> https

## [1.7.1] - 2023-01-18

### Added

-   Fixed version of python-dateutil

### Fixed

## [1.7.0] - 2023-01-17

### Added

-   Deploy using Flink Kubernetes Operator

### Fixed

-   Allow for whitespaces in secret variables regex.

## [1.6.0] - 2022-09-12

### Added

-   Convert secret variables (marked with `${variable_name}`) to use environment variables.
-   Load secret from file using `%load_secret_file` magic.
-   Load secrets from files listed in `.streaming_config.yml` file.

### Fixed

-   Show raw `"status"` response from Docker if it is not a string.

## [1.5.0] - 2022-08-25

### Added

-   Skip `explain`, `describe` and `show`

## [1.4.0] - 2022-08-22

### Added

-   Using `init.sql` as the initialization script.
-   Use plugin to download jars

### Changed

-   `scli project build` prints Docker client output to the standard output.

## [1.3.2] - 2022-05-26

### Added

-   `--template_url` flag to `scli project init` command.

### Fixed

-   `scli project init` references proper default template URLs.

## [1.3.1] - 2022-05-10

## [1.3.0] - 2022-05-09

## [1.2.3] - 2022-05-09

## [1.2.2] - 2022-05-09

-   First release

# [Unreleased]&#x3A; <https://github.com/getindata/streaming-cli/compare/1.8.0...HEAD>

[Unreleased]: https://github.com/getindata/streaming-cli/compare/2.0.0...HEAD

[2.0.0]: https://github.com/getindata/streaming-cli/compare/1.11.1...2.0.0

[1.11.1]: https://github.com/getindata/streaming-cli/compare/1.11.0...1.11.1

[1.11.0]: https://github.com/getindata/streaming-cli/compare/1.10.2...1.11.0

[1.10.2]: https://github.com/getindata/streaming-cli/compare/1.10.1...1.10.2

[1.10.1]: https://github.com/getindata/streaming-cli/compare/1.10.0...1.10.1

[1.10.0]: https://github.com/getindata/streaming-cli/compare/1.9.1...1.10.0

[1.9.1]: https://github.com/getindata/streaming-cli/compare/1.9.0...1.9.1

[1.9.0]: https://github.com/getindata/streaming-cli/compare/1.8.0...1.9.0

[1.8.0]: https://github.com/getindata/streaming-cli/compare/1.7.1...1.8.0

[1.7.0]: https://github.com/getindata/streaming-cli/compare/1.6.0...1.7.0

[1.6.0]: https://github.com/getindata/streaming-cli/compare/1.5.0...1.6.0

[1.5.0]: https://github.com/getindata/streaming-cli/compare/1.4.0...1.5.0

[1.4.0]: https://github.com/getindata/streaming-cli/compare/1.3.2...1.4.0

[1.3.2]: https://github.com/getindata/streaming-cli/compare/1.3.1...1.3.2

[1.3.1]: https://github.com/getindata/streaming-cli/compare/1.3.0...1.3.1

[1.3.0]: https://github.com/getindata/streaming-cli/compare/1.2.3...1.3.0

[1.2.3]: https://github.com/getindata/streaming-cli/compare/1.2.2...1.2.3

[1.2.2]: https://github.com/getindata/streaming-cli/compare/46ec0366c64d64f8f0b769568b6f0956387f2a7c...1.2.2
