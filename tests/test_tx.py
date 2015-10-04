from __future__ import absolute_import, division, print_function

import pytest

pytest.importorskip("twisted")

from twisted.internet.defer import Deferred, succeed, fail

from prometheus_async import tx


class TestTwisted(object):
    def test_is_async_true(self):
        """
        is_async recognizes Deferreds.
        """
        assert True is tx._decorators.is_async(Deferred())

    @pytest.mark.parametrize("sync_val", [
        None,
        "sync",
        object(),
    ])
    def test_is_async_false(self, sync_val):
        """
        is_async rejects everything else.
        """
        assert False is tx._decorators.is_async(sync_val)

    @pytest.inlineCallbacks
    def test_deferred(self, fo, patch_timer):
        """
        time works with Deferreds.
        """
        @tx.time(fo)
        def func():
            return succeed(42)

        rv = func()

        # Twisted runs fired callbacks immediately.
        assert [1] == fo._observed
        assert 42 == (yield rv)
        assert [1] == fo._observed

    @pytest.inlineCallbacks
    def test_exc(self, fo, patch_timer):
        """
        Does not swallow exceptions.
        """
        @tx.time(fo)
        def func():
            return fail(ValueError("foo"))

        with pytest.raises(ValueError):
            yield func()
