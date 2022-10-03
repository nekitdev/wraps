# Changelog

<!-- changelog: start -->

## 0.2.0 (2022-10-03)

### Features

- Rename `convert_optional -> wrap_optional`, add `extract` method.
  This allows users to defer back to `Optional[T]`, along with wrapping
  `Optional[T]` into `Option[T]` in a clear and concise way.
  ([#1](https://github.com/nekitdev/wraps/pull/1))

## 0.1.0 (2022-09-09)

Initial release.
