import logging
import time

from django.http import JsonResponse

from ecommerce_backend.resource_manager import resource_manager

logger = logging.getLogger("resource_manager")


OBSERVABILITY_PATHS = {
    "/metrics",
    "/system/local-metrics",
    "/system/metrics",
    "/system/dashboard",
}

class ResourceManagerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in OBSERVABILITY_PATHS:
            return self.get_response(request)

        if not resource_manager.acquire():
            logger.warning(
                "Request rejected – system at capacity  path=%s",
                request.path,
            )
            return JsonResponse(
                {
                    "error": "Queue is full. All workers are busy and no "
                             "waiting slots are available. "
                             "Please try again shortly.",
                },
                status=503,
            )

        start = time.perf_counter()
        try:
            response = self.get_response(request)
        finally:
            resource_manager.release()
            elapsed = time.perf_counter() - start
            logger.debug(
                "Request completed  path=%s  elapsed=%.3fs",
                request.path,
                elapsed,
            )

        return response
