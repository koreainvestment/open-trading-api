import uuid
from datetime import datetime
import time

from fastmcp.server.middleware import Middleware, MiddlewareContext

import module.factory as factory

# 기본 미들웨어
class EnvironmentMiddleware(Middleware):
    def __init__(self, environment):
        self.environment = environment

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        ctx = context.fastmcp_context

        # time counter start
        t0 = time.perf_counter()

        # started_at
        started_dt = datetime.now()
        ctx.set_state(factory.CONTEXT_STARTED_AT, started_dt.strftime("%Y-%m-%d %H:%M:%S"))

        # request id
        request_id = uuid.uuid4().hex
        ctx.set_state(factory.CONTEXT_REQUEST_ID, request_id)

        # context setup
        ctx.set_state(factory.CONTEXT_ENVIRONMENT, self.environment)

        try:
            result = await call_next(context)
            return result
        except Exception as e:
            raise e
        finally:
            # ended at
            ended_at = datetime.now()
            ctx.set_state(factory.CONTEXT_ENDED_AT, ended_at.strftime("%Y-%m-%d %H:%M:%S"))

            # time counter end
            elapsed_sec = time.perf_counter() - t0
            ctx.set_state(factory.CONTEXT_ELAPSED_SECONDS, round(elapsed_sec, 2))



