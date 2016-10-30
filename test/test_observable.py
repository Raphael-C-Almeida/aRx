import pytest
import asyncio
import logging

from aioreactive.testing import VirtualTimeEventLoop
from aioreactive.observable import AsyncObservable, AsyncAnonymousObserver
from aioreactive.core import AsyncStream

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@pytest.yield_fixture()
def event_loop():
    loop = VirtualTimeEventLoop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_observable_map():
    xs = AsyncObservable.from_iterable([1, 2, 3])
    result = []

    async def mapper(value):
        await asyncio.sleep(0.1)
        return value * 10

    ys = xs.select(mapper)

    async def on_next(value):
        result.append(value)

    sub = await ys.subscribe(AsyncAnonymousObserver(on_next))
    await sub
    assert result == [10, 20, 30]


@pytest.mark.asyncio
async def test_observable_simple_pipe():
    xs = AsyncObservable.from_iterable([1, 2, 3])
    result = []

    async def mapper(value):
        await asyncio.sleep(0.1)
        return value * 10

    async def predicate(value):
        await asyncio.sleep(0.1)
        return value > 1

    ys = xs.where(predicate).select(mapper)

    async def on_next(value):
        result.append(value)

    sub = await ys.subscribe(AsyncAnonymousObserver(on_next))
    await sub
    assert result == [20, 30]


@pytest.mark.asyncio
async def test_observable_complex_pipe():
    xs = AsyncObservable.from_iterable([1, 2, 3])
    result = []

    async def mapper(value):
        await asyncio.sleep(0.1)
        return value * 10

    async def predicate(value):
        await asyncio.sleep(0.1)
        return value > 1

    async def long_running(value):
        return AsyncObservable.from_iterable([value])

    ys = (xs
          .where(predicate)
          .select(mapper)
          .select_many(long_running))

    async def on_next(value):
        result.append(value)

    sub = await ys.subscribe(AsyncAnonymousObserver(on_next))
    await sub
    assert result == [20, 30]