# Changelog

<!-- changelogging: start -->

## 0.9.2 (2024-03-16)

### Changes

- Improved type narrowing via using `TypeIs` instead of `TypeGuard`.

## 0.9.1 (2024-02-26)

No significant changes.

## 0.9.0 (2024-02-25)

### Features

- Added `map_either` and `map_either_await` to `Either[L, R]`.
- Updated `FutureEither[L, R]` to be in sync with `Either[L, R]`.

## 0.8.0 (2024-01-08)

### Features

- Added `NULL` for convenience:

  ```python
  NULL = Null()
  ```

## 0.7.0 (2024-01-07)

### Changes

- Renamed functions in `Future[T]`; `name_future` is now `base_name`.

### Internal

- Migrated to Python 3.8.

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
