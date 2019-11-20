# Monkey patching must happen before all other imports. Do not move these lines.
# Add all monkey patching to this part of the code.

# Notably, gevent should be the very first one.
# See http://www.gevent.org/gevent.monkey.html for more info.
import gevent.monkey
gevent.monkey.patch_all()  # noqa:E402
