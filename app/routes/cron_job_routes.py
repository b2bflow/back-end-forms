from flask import Blueprint
from app.controllers.cron_job_controller import CronJobController
from app.repository.lead_repository import LeadRepository
from app.services.cron_job_service import CronJobService

cron_job_bp = Blueprint("cron_job", __name__)

repository = LeadRepository()
service = CronJobService(repository)
controller = CronJobController(service)

cron_job_bp.get("/api/v1/cron_job")(controller.run)