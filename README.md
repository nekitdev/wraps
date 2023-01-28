# `wraps`

[![License][License Badge]][License]
[![Version][Version Badge]][Package]
[![Downloads][Downloads Badge]][Package]
[![Discord][Discord Badge]][Discord]

[![Documentation][Documentation Badge]][Documentation]
[![Check][Check Badge]][Actions]
[![Test][Test Badge]][Actions]
[![Coverage][Coverage Badge]][Coverage]

**Meaningful and safe wrapping types.**

## Installing

**Python 3.7 or above is required.**

### pip

Installing the library with `pip` is quite simple:

```console
$ pip install wraps
```

Alternatively, the library can be installed from source:

```console
$ git clone https://github.com/nekitdev/wraps.git
$ cd wraps
$ python -m pip install .
```

### poetry

You can add `wraps` as a dependency with the following command:

```console
$ poetry add wraps
```

Or by directly specifying it in the configuration like so:

```toml
[tool.poetry.dependencies]
wraps = "^0.3.0"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies.wraps]
git = "https://github.com/nekitdev/wraps.git"
```

## Examples

### Option

[`Option[T]`][wraps.option.Option] type represents an optional value: every option is either
[`Some[T]`][wraps.option.Some] and contains a value, or [`Null`][wraps.option.Null], and does not.

Here is an example of using [`wrap_option`][wraps.option.wrap_option] to catch any errors:

```python
from typing import List, TypeVar
from wraps import wrap_option

T = TypeVar("T", covariant=True)


class SafeList(List[T]):
    @wrap_option
    def get(self, index: int) -> T:
        return self[index]


array = SafeList([0, 1, 2, 3])

print(array.get(0))  # Some(value=0)
print(array.get(7))  # Null()
```

### Result

[`Result[T, E]`][wraps.result.Result] is the type used for returning and propagating errors.
It has two variants, [`Ok[T]`][wraps.result.Ok], representing success and containing a value,
and [`Error[E]`][wraps.result.Error], representing error and containing an error value.

```python
from wraps import Result, wrap_result


@wrap_result[ValueError]
def parse(string: str) -> int:
    return int(string)


def multiply(x: str, y: str) -> Result[int, ValueError]:
    # try to parse two strings and multiply results
    return parse(x).and_then(lambda m: parse(y).map(lambda n: m * n))


print(multiply("21", "2").unwrap())  # 42
print(multiply("!", "42").unwrap_error())  # invalid literal for `int` with base 10: `!`
```

In python versions before 3.9 (where grammar restrictions on decorators were relaxed),
one can use [`wrap_result`][wraps.result.wrap_result] without a concrete type:

```python
@wrap_result
def parse(string: str) -> int:
    return int(string)
```

However this makes the types less specific, since [`Exception`][Exception]
is caught instead of [`ValueError`][ValueError].

Instead, you can create a new concrete [`WrapResult[E]`][wraps.result.WrapResult] instance:

```python
from wraps import WrapResult

wrap_value_error = WrapResult(ValueError)

@wrap_value_error
def parse(string: str) -> int:
    return int(string)
```

### Early Return

Early return functionality (`?` operator in Rust) is implemented via `early` function
(for both [`Option`][wraps.option.Option] and [`Result`][wraps.result.Result] types)
combined with the [`@early_option`][wraps.early.early_option] or
[`@early_result`][wraps.early.early_result] decorator respectively.

```python
from wraps import Option, Some, early_option, wrap_option


@wrap_option
def parse(string: str) -> int:
    return int(string)


@early_option
def try_add(x: str, y: str) -> Option[int]:
    m = parse(x).early()
    n = parse(y).early()

    return Some(m + n)
```

## Documentation

You can find the documentation [here][Documentation].

## Support

If you need support with the library, you can send us an [email][Email]
or refer to the official [Discord server][Discord].

## Changelog

You can find the changelog [here][Changelog].

## Security Policy

You can find the Security Policy of `wraps` [here][Security].

## Contributing

If you are interested in contributing to `wraps`, make sure to take a look at the
[Contributing Guide][Contributing Guide], as well as the [Code of Conduct][Code of Conduct].

## License

`wraps` is licensed under the MIT License terms. See [License][License] for details.

[Email]: mailto:support@nekit.dev

[Discord]: https://nekit.dev/discord

[Actions]: https://github.com/nekitdev/wraps/actions

[Changelog]: https://github.com/nekitdev/wraps/blob/main/CHANGELOG.md
[Code of Conduct]: https://github.com/nekitdev/wraps/blob/main/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/nekitdev/wraps/blob/main/CONTRIBUTING.md
[Security]: https://github.com/nekitdev/wraps/blob/main/SECURITY.md

[License]: https://github.com/nekitdev/wraps/blob/main/LICENSE

[Package]: https://pypi.org/project/wraps
[Coverage]: https://codecov.io/gh/nekitdev/wraps
[Documentation]: https://nekitdev.github.io/wraps

[Discord Badge]: https://img.shields.io/badge/chat-discord-5865f2
[License Badge]: https://img.shields.io/pypi/l/wraps
[Version Badge]: https://img.shields.io/pypi/v/wraps
[Downloads Badge]: https://img.shields.io/pypi/dm/wraps

[Documentation Badge]: https://github.com/nekitdev/wraps/workflows/docs/badge.svg
[Check Badge]: https://github.com/nekitdev/wraps/workflows/check/badge.svg
[Test Badge]: https://github.com/nekitdev/wraps/workflows/test/badge.svg
[Coverage Badge]: https://codecov.io/gh/nekitdev/wraps/branch/main/graph/badge.svg

[wraps.option.Option]: https://nekitdev.github.io/wraps/reference/option#wraps.option.Option
[wraps.option.Some]: https://nekitdev.github.io/wraps/reference/option#wraps.option.Some
[wraps.option.Null]: https://nekitdev.github.io/wraps/reference/option#wraps.option.Null
[wraps.option.wrap_option]: https://nekitdev.github.io/wraps/reference/option#wraps.option.wrap_option

[wraps.result.Result]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Result
[wraps.result.Ok]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Ok
[wraps.result.Error]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Error
[wraps.result.wrap_result]: https://nekitdev.github.io/wraps/reference/result#wraps.result.wrap_result

[wraps.result.WrapResult]: https://nekitdev.github.io/wraps/reference/result#wraps.result.WrapResult

[wraps.early.early_option]: https://nekitdev.github.io/wraps/reference/early#wraps.early.early_option
[wraps.early.early_result]: https://nekitdev.github.io/wraps/reference/early#wraps.early.early_result

[Exception]: https://docs.python.org/3/library/exceptions#Exception
[ValueError]: https://docs.python.org/3/library/exceptions#ValueError
