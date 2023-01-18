# Changelog

## [Unreleased]

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

[Unreleased]: https://github.com/getindata/streaming-cli/compare/1.7.1...HEAD

[1.7.1]: https://github.com/getindata/streaming-cli/compare/1.7.0...1.7.1

[1.7.0]: https://github.com/getindata/streaming-cli/compare/1.6.0...1.7.0

[1.6.0]: https://github.com/getindata/streaming-cli/compare/1.5.0...1.6.0

[1.5.0]: https://github.com/getindata/streaming-cli/compare/1.4.0...1.5.0

[1.4.0]: https://github.com/getindata/streaming-cli/compare/1.3.2...1.4.0

[1.3.2]: https://github.com/getindata/streaming-cli/compare/1.3.1...1.3.2

[1.3.1]: https://github.com/getindata/streaming-cli/compare/1.3.0...1.3.1

[1.3.0]: https://github.com/getindata/streaming-cli/compare/1.2.3...1.3.0

[1.2.3]: https://github.com/getindata/streaming-cli/compare/1.2.2...1.2.3

[1.2.2]: https://github.com/getindata/streaming-cli/compare/46ec0366c64d64f8f0b769568b6f0956387f2a7c...1.2.2
