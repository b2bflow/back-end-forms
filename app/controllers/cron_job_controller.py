from app.interfaces.services.cron_job_service_interface import CronJobServiceInterface


class CronJobController:
    def __init__(self, service: CronJobServiceInterface):
        self.service = service

    def run(self):
        confirmarion_messages = self.service.send_confirmation_messager()
        recovery_message = self.service.send_recovery_message()
        meeting_reminder = self.service.send_meeting_reminder()

        return {"confirmarion_messages": confirmarion_messages, "recovery_message": recovery_message, "meeting_reminder": meeting_reminder}, 200