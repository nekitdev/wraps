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

Alternatively, the library can be installed from the source:

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
wraps = "^0.6.1"
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

Here is an example of using [`wrap_option`][wraps.wraps.wrap_option] to catch any errors:

```python
from typing import List, TypeVar
from wraps import wrap_option

T = TypeVar("T", covariant=True)


class Array(List[T]):
    @wrap_option
    def get(self, index: int) -> T:
        return self[index]


array = Array([1, 2, 3])

print(array.get(0).unwrap())  # 1
print(array.get(5).unwrap_or(0))  # 0
```

### Result

[`Result[T, E]`][wraps.result.Result] is the type used for returning and propagating errors.
It has two variants, [`Ok[T]`][wraps.result.Ok], representing success and containing a value,
and [`Error[E]`][wraps.result.Error], representing error and containing an error value.

```python
from enum import Enum

from wraps import Error, Ok, Result


class DivideError(Enum):
    DIVISION_BY_ZERO = "division by zero"


def divide(numerator: float, denominator: float) -> Result[float, DivideError]:
    return Ok(numerator / denominator) if denominator else Error(DivideError.DIVISION_BY_ZERO)
```

### Early Return

Early return functionality (like the *question-mark* (`?`) operator in Rust) is implemented via `early` methods
(for both [`Option`][wraps.option.Option] and [`Result`][wraps.result.Result] types)
combined with the [`@early_option`][wraps.early.early_option] and
[`@early_result`][wraps.early.early_result] decorators respectively.

```python
from wraps import Option, early_option, wrap_option


@wrap_option[ValueError]
def parse(string: str) -> float:
    return float(string)


@wrap_option[ZeroDivisionError]
def divide(numerator: float, denominator: float) -> float:
    return numerator / denominator


@early_option
def function(x: str, y: str) -> Option[float]:
    return divide(parse(x).early(), parse(y).early())
```

### Decorators

In Python 3.9 the restrictions on the decorators' syntax have been lifted, which allows for nifty
syntax which can be seen above. On older versions of Python, one can use:

```python
from wraps import wrap_option

@wrap_option
def parse(string: str) -> int:
    return int(string)
```

However, this isn't the best way to handle errors, as *any* normal errors will be caught, without
a way to distinguish between them.
To counter this, one can use [`WrapOption`][wraps.wraps.WrapOption] directly,
passing the concrete error type:

```python
from wraps import WrapOption

wrap_value_error = WrapOption(ValueError)


@wrap_value_error
def parse(string: str) -> int:
    return int(string)
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

[wraps.result.Result]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Result
[wraps.result.Ok]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Ok
[wraps.result.Error]: https://nekitdev.github.io/wraps/reference/result#wraps.result.Error

[wraps.wraps.wrap_option]: https://nekitdev.github.io/wraps/reference/wraps#wraps.wraps.wrap_option

[wraps.wraps.WrapOption]: https://nekitdev.github.io/wraps/reference/wraps#wraps.wraps.WrapOption

[wraps.early.early_option]: https://nekitdev.github.io/wraps/reference/early#wraps.early.early_option
[wraps.early.early_result]: https://nekitdev.github.io/wraps/reference/early#wraps.early.early_result
