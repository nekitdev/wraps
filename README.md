# `wraps`

[![License][License Badge]][License]
[![Version][Version Badge]][Package]
[![Downloads][Downloads Badge]][Package]
[![Discord][Discord Badge]][Discord]

[![Documentation][Documentation Badge]][Documentation]
[![Check][Check Badge]][Actions]
[![Test][Test Badge]][Actions]
[![Coverage][Coverage Badge]][Coverage]

> *Meaningful and safe wrapping types.*

## Installing

**Python 3.8 or above is required.**

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
wraps = "^0.13.0"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies.wraps]
git = "https://github.com/nekitdev/wraps.git"
```

## Examples

### Option

[`Option[T]`][wraps.primitives.option.Option] type represents an optional value: every option is either
[`Some[T]`][wraps.primitives.option.Some] and contains a value, or [`Null`][wraps.primitives.option.Null], and does not.

Here is an example of using [`wrap_option`][wraps.wraps.option.wrap_option] to catch any errors:

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

[`Result[T, E]`][wraps.primitives.result.Result] is the type used for returning and propagating errors.
It has two variants, [`Ok[T]`][wraps.primitives.result.Ok], representing success and containing a value,
and [`Error[E]`][wraps.primitives.result.Error], representing error and containing an error value.

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
(for both [`Option[T]`][wraps.primitives.option.Option] and [`Result[T, E]`][wraps.primitives.result.Result] types)
combined with the [`@early_option`][wraps.early.decorators.early_option] and
[`@early_result`][wraps.early.decorators.early_result] decorators respectively.

```python
from wraps import Option, early_option, wrap_option_on


@wrap_option_on(ValueError)
def parse(string: str) -> float:
    return float(string)


@wrap_option_on(ZeroDivisionError)
def divide(numerator: float, denominator: float) -> float:
    return numerator / denominator


@early_option
def function(x: str, y: str) -> Option[float]:
    return divide(parse(x).early(), parse(y).early())
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

[Discord]: https://nekit.dev/chat

[Actions]: https://github.com/nekitdev/wraps/actions

[Changelog]: https://github.com/nekitdev/wraps/blob/main/CHANGELOG.md
[Code of Conduct]: https://github.com/nekitdev/wraps/blob/main/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/nekitdev/wraps/blob/main/CONTRIBUTING.md
[Security]: https://github.com/nekitdev/wraps/blob/main/SECURITY.md

[License]: https://github.com/nekitdev/wraps/blob/main/LICENSE

[Package]: https://pypi.org/project/wraps
[Coverage]: https://codecov.io/gh/nekitdev/wraps
[Documentation]: https://nekitdev.github.io/wraps

[Discord Badge]: https://img.shields.io/discord/728012506899021874
[License Badge]: https://img.shields.io/pypi/l/wraps
[Version Badge]: https://img.shields.io/pypi/v/wraps
[Downloads Badge]: https://img.shields.io/pypi/dm/wraps

[Documentation Badge]: https://github.com/nekitdev/wraps/workflows/docs/badge.svg
[Check Badge]: https://github.com/nekitdev/wraps/workflows/check/badge.svg
[Test Badge]: https://github.com/nekitdev/wraps/workflows/test/badge.svg
[Coverage Badge]: https://codecov.io/gh/nekitdev/wraps/branch/main/graph/badge.svg

[wraps.primitives.option.Option]: https://nekitdev.github.io/wraps/reference/primitives/option#wraps.primitives.option.Option
[wraps.primitives.option.Some]: https://nekitdev.github.io/wraps/reference/primitives/option#wraps.primitives.option.Some
[wraps.primitives.option.Null]: https://nekitdev.github.io/wraps/reference/primitives/option#wraps.primitives.option.Null

[wraps.primitives.result.Result]: https://nekitdev.github.io/wraps/reference/primitives/result#wraps.primitives.result.Result
[wraps.primitives.result.Ok]: https://nekitdev.github.io/wraps/reference/primitives/result#wraps.primitives.result.Ok
[wraps.primitives.result.Error]: https://nekitdev.github.io/wraps/reference/primitives/result#wraps.primitives.result.Error

[wraps.wraps.option.wrap_option]: https://nekitdev.github.io/wraps/reference/wraps/option#wraps.wraps.option.wrap_option

[wraps.early.decorators.early_option]: https://nekitdev.github.io/wraps/reference/early/decorators#wraps.early.decorators.early_option
[wraps.early.decorators.early_result]: https://nekitdev.github.io/wraps/reference/early/decorators#wraps.early.decorators.early_result
