from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from employee_info_fetcher import __version__
from employee_info_fetcher.api.security import verify_auth
from employee_info_fetcher.audit import get_correlation_id, new_correlation_id
from employee_info_fetcher.bootstrap import bootstrap
from employee_info_fetcher.db.session import db_session, reset_db_engine_cache
from employee_info_fetcher.jobs.store import JobStore
from employee_info_fetcher.repositories.factory import reset_repository_cache
from employee_info_fetcher.schemas import (
    EmployeeListResponse,
    ErrorResponse,
    HealthResponse,
    JobStatusResponse,
    JobSubmitResponse,
    ProfileRequest,
    ProfileResponse,
    ReadinessResponse,
)
from employee_info_fetcher.service import ProfileService, map_service_error
from employee_info_fetcher.settings import Settings, get_settings

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap()
    get_settings.cache_clear()
    reset_db_engine_cache()
    reset_repository_cache()
    app.state.job_store = JobStore()
    yield
    app.state.job_store._executor.shutdown(wait=False, cancel_futures=True)


def create_app() -> FastAPI:
    settings = get_settings()
    rate_limit = settings.rate_limit
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    Instrumentator().instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        from employee_info_fetcher.audit import correlation_id_var

        incoming = request.headers.get("X-Correlation-ID")
        if incoming:
            correlation_id_var.set(incoming)
        else:
            new_correlation_id()
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = get_correlation_id()
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=str(exc.detail),
                correlation_id=get_correlation_id(),
            ).model_dump(),
            headers={"X-Correlation-ID": get_correlation_id()},
        )

    @app.get("/health", response_model=HealthResponse, tags=["operations"])
    @limiter.exempt
    async def health(request: Request, settings: Settings = Depends(get_settings)):
        return HealthResponse(
            service=settings.app_name,
            environment=settings.app_env,
            version=__version__,
        )

    @app.get("/health/ready", response_model=ReadinessResponse, tags=["operations"])
    @limiter.exempt
    async def readiness(request: Request, settings: Settings = Depends(get_settings)):
        datastore = "postgresql" if settings.use_database else "json"
        if settings.use_database:
            try:
                with db_session() as session:
                    session.execute(text("SELECT 1"))
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc
        return ReadinessResponse(status="ready", datastore=datastore)

    @app.get(
        "/v1/employees",
        response_model=EmployeeListResponse,
        tags=["employees"],
        dependencies=[Depends(verify_auth)],
    )
    @limiter.limit(rate_limit)
    async def list_employees(
        request: Request,
        service: ProfileService = Depends(ProfileService),
    ):
        try:
            names = service.list_employees()
        except Exception as exc:
            status_code, detail = map_service_error(exc)
            raise HTTPException(status_code=status_code, detail=detail) from exc
        return EmployeeListResponse(employees=names, count=len(names))

    @app.post(
        "/v1/profiles",
        response_model=ProfileResponse,
        tags=["profiles"],
        dependencies=[Depends(verify_auth)],
    )
    @limiter.limit(rate_limit)
    async def create_profile(
        request: Request,
        body: ProfileRequest,
        service: ProfileService = Depends(ProfileService),
    ):
        try:
            return service.generate_profile(body.name.strip())
        except Exception as exc:
            status_code, detail = map_service_error(exc)
            raise HTTPException(status_code=status_code, detail=detail) from exc

    @app.post(
        "/v1/profiles/async",
        response_model=JobSubmitResponse,
        tags=["profiles"],
        dependencies=[Depends(verify_auth)],
    )
    @limiter.limit(rate_limit)
    async def create_profile_async(
        request: Request,
        body: ProfileRequest,
    ):
        job_store: JobStore = request.app.state.job_store
        job = job_store.submit(body.name.strip())
        return JobSubmitResponse(
            job_id=job.id,
            status=job.status,
            correlation_id=job.correlation_id,
        )

    @app.get(
        "/v1/jobs/{job_id}",
        response_model=JobStatusResponse,
        tags=["profiles"],
        dependencies=[Depends(verify_auth)],
    )
    @limiter.limit(rate_limit)
    async def get_job_status(request: Request, job_id: str):
        job_store: JobStore = request.app.state.job_store
        job = job_store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            correlation_id=job.correlation_id,
            employee_name=job.employee_name,
            result=job.result,
            error=job.error,
        )

    return app
