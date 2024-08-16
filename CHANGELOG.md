# Changelog

<!-- changelogging: start -->

## [0.14.1](https://github.com/nekitdev/wraps/tree/v0.14.1) (2024-08-16)

No significant changes.

## [0.14.0](https://github.com/nekitdev/wraps/tree/v0.14.0) (2024-08-13)

No significant changes.

## [0.13.0](https://github.com/nekitdev/wraps/tree/v0.13.0) (2024-06-21)

### Changes

- Error types are now truly forced to be non-empty.
  ([#55](https://github.com/nekitdev/wraps/pull/55))

## 0.12.0 (2024-04-30)

### Features

- Added `or_raise`, `or_raise_with` and `or_raise_with_await` for
  `Option[T]`, `Result[T, E]` and their future counterparts.

## 0.11.0 (2024-04-23)

### Features

- Added `wrap_option_on`, `wrap_option_await_on`, `wrap_result_on` and `wrap_result_await_on`.

### Changes

- `wrap_option`, `wrap_option_await`, `wrap_result` and `wrap_result_await` are no longer
  subscriptable: their `wrap_on` counterparts should be used to specify error types to handle.

- `reawaitable` was renamed to `wrap_reawaitable` for consistency.

## 0.10.0 (2024-04-22)

### Changes

- The entire library was refactored.

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
