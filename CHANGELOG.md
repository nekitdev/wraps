# Changelog

<!-- changelogging: start -->

## 0.6.1 (2023-05-24)

### Fixes

- Fixed `final` import to be compatible with Python 3.7.

## 0.6.0 (2023-05-21)

### Internal

- Migrated to using `typing-aliases` library.

## 0.5.0 (2023-05-12)

### Features

- Implement missing methods in future variants of options and results.

## 0.4.0 (2023-04-24)

### Internal

- Internal improvements.

## 0.3.0 (2023-01-28)

### Features

- Implemented `Either[L, R]` type.

## 0.2.0 (2022-10-03)

### Features

- Renamed `convert_optional -> wrap_optional`, added `extract` method.
  This allows users to defer back to `Optional[T]`, along with wrapping
  `Optional[T]` into `Option[T]` in a clear and concise way.
  ([#1](https://github.com/nekitdev/wraps/pull/1))

## 0.1.0 (2022-09-09)

Initial release.
